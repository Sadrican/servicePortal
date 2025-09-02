"""Domain models for the portal app.

This module defines PartnerService, Customer, SparePart, WarrantyClaim, and
through models for claim spare parts and labours. Only readability-oriented
improvements (docstrings, comments) are applied to avoid schema changes.
"""

from Service_Portal.settings import AUTH_USER_MODEL as User
from django.db import models
from datetime import date
from django.utils.translation import gettext_lazy as _


class PartnerService(models.Model):
    """Represents a partner (dealer/service) organization."""

    name = models.CharField(max_length=64)
    email = models.EmailField(verbose_name=_("Partner Email"))
    phone_number = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return self.name


class Customer(models.Model):
    """Represents an end-customer served by a PartnerService."""

    first_name = models.CharField(_("Customer First Name"), max_length=64)
    last_name = models.CharField(_("Customer Last Name"), max_length=64)
    company = models.CharField(_("Customer's Company Name"), max_length=64)
    email = models.EmailField(_("Customer Email"), unique=True, db_index=True)
    phone_number = models.CharField(max_length=20)
    city = models.CharField(max_length=64)
    country = models.CharField(max_length=64)
    address = models.TextField()
    # Note: default=0 kept to avoid migrations in current task scope
    partner_service = models.ForeignKey(
        PartnerService, on_delete=models.CASCADE, related_name="customers", default=0
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}".title()

    @property
    def display_company(self):
        """Title-cased company name for display purposes."""
        return f"{self.company.title()}"


class SparePart(models.Model):
    """Catalog entry for a spare part with prices in multiple currencies."""

    class Currency(models.TextChoices):
        USD = "USD", _("US Dollar")
        EUR = "EUR", _("Euro")
        GBP = "GBP", _("Pound Sterling")
        TRY = "TRY", _("Turkish Lira")

    stock_code = models.CharField(
        max_length=64, unique=True, db_index=True, verbose_name="Stock Code", default=0
    )
    description = models.TextField()
    # Store prices for all supported currencies
    price_usd = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    price_eur = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    price_gbp = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    price_try = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.stock_code}"

    def get_price(self, currency):
        """Return the unit price in the requested currency.

        If currency is unknown, returns None.
        """
        mapping = {
            self.Currency.USD: self.price_usd,
            self.Currency.EUR: self.price_eur,
            self.Currency.GBP: self.price_gbp,
            self.Currency.TRY: self.price_try,
        }
        return mapping.get(currency)


class WarrantyClaim(models.Model):
    """A warranty claim created by a partner for a customer and vehicle."""

    class ClaimTypes(models.TextChoices):
        Repair = "RP", _("Repair")
        Bulletin = "BT", _("Bulletin")

    class VehicleTypes(models.TextChoices):
        CurtainSider = "CS", _("Curtain Sider")
        Platform = "PF", _("Platform")
        ContainerChassis = "CC", _("Container Chassis")
        SwapBody = "SB", _("Swap Body")
        Refer = "RF", _("Reefer")
        Box = "BX", _("Box")
        Silo = "SI", _("Silo")
        Tanker = "TK", _("Tanker")
        LowBed = "LB", _("Low-Bed")
        Tipper = "TP", _("Tipper")
        Other = "OT", _("Other")

    class ClaimStatus(models.TextChoices):
        New = "NW", _("New")
        Revised = "RV", _("Revised")
        NeedsRevise = "NR", _("Needs Revise")
        Accepted = "AC", _("Accepted")
        Rejected = "RJ", _("Rejected")
        Completed = "CP", _("Completed")

    claim_date = models.DateField(auto_now_add=True)
    claim_last_modified = models.DateField(auto_now=True)
    claim_type = models.CharField(max_length=2, choices=ClaimTypes.choices, default=ClaimTypes.Repair)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="claims")
    vehicle_driver_name = models.CharField(max_length=64)
    vehicle_driver_phone = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=2, choices=VehicleTypes.choices, default=VehicleTypes.Other)
    vehicle_defect_date = models.DateField(default=date.today())
    vehicle_chassis_number = models.IntegerField()
    vehicle_registration_date = models.DateField(default=date.today())
    vehicle_kilometer = models.IntegerField()
    defect_category = models.TextField()
    defect_description = models.TextField()
    status = models.CharField(max_length=2, choices=ClaimStatus.choices, default=ClaimStatus.New)
    partner_service = models.ForeignKey(PartnerService, on_delete=models.CASCADE, related_name="claims")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_claims")
    spare_parts = models.ManyToManyField(
        "SparePart",
        through="ClaimSparePart",
        related_name="claims",
        blank=True,
    )


class ClaimSparePart(models.Model):
    """Through model storing part snapshot and pricing at claim time."""

    claim = models.ForeignKey(WarrantyClaim, on_delete=models.CASCADE, related_name="parts")
    # Keep an M2M through FK for referential integrity, but user will type stock_code
    spare_part = models.ForeignKey(SparePart, on_delete=models.PROTECT, related_name="claim_spareparts")

    # User-entered stock code field to look up the SparePart; also stored as snapshot
    stock_code = models.CharField(max_length=64, verbose_name=_("Stock Code"))
    description = models.TextField(blank=True, verbose_name=_("Description"))

    # Pricing snapshot
    currency = models.CharField(max_length=3, choices=SparePart.Currency.choices, default=SparePart.Currency.EUR)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    quantity = models.PositiveIntegerField()
    approved_quantity = models.PositiveIntegerField(null=True, blank=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = (("claim", "spare_part"),)

    def __str__(self):
        return f"{self.stock_code}"


class Labour(models.Model):
    """Catalog entry for labour with hourly rates in multiple currencies."""

    class Currency(models.TextChoices):
        USD = "USD", _("US Dollar")
        EUR = "EUR", _("Euro")
        GBP = "GBP", _("Pound Sterling")
        TRY = "TRY", _("Turkish Lira")

    code = models.CharField(max_length=64, unique=True, db_index=True, verbose_name=_("Labour Code"))
    description = models.TextField()
    rate_usd = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    rate_eur = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    rate_gbp = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    rate_try = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return self.code

    def get_rate(self, currency):
        """Return the hourly rate in the requested currency, or None if unknown."""
        mapping = {
            self.Currency.USD: self.rate_usd,
            self.Currency.EUR: self.rate_eur,
            self.Currency.GBP: self.rate_gbp,
            self.Currency.TRY: self.rate_try,
        }
        return mapping.get(currency)


class ClaimLabour(models.Model):
    """Through model storing labour snapshot and pricing at claim time."""

    claim = models.ForeignKey(WarrantyClaim, on_delete=models.CASCADE, related_name="labours")
    labour = models.ForeignKey(Labour, on_delete=models.PROTECT, related_name="claim_labours")

    code = models.CharField(max_length=64, verbose_name=_("Labour Code"))
    description = models.TextField(blank=True, verbose_name=_("Description"))

    currency = models.CharField(max_length=3, choices=Labour.Currency.choices, default=Labour.Currency.EUR)
    unit_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    duration = models.DecimalField(max_digits=7, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = (("claim", "labour"),)

    def __str__(self):
        return f"{self.code}"






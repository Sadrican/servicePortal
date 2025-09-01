from Service_Portal.settings import AUTH_USER_MODEL as User
from django.db import models
from datetime import date
from django.utils.translation import gettext_lazy as _
# Create your models here.

#bayi tablosu
class PartnerService(models.Model):

    name = models.CharField(max_length=64)
    email = models.EmailField(verbose_name=_("Partner Email"))
    phone_number = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return self.name

#müşteriler tablosu
class Customer(models.Model):

    first_name = models.CharField(_("Customer First Name"),max_length=64)
    last_name = models.CharField(_("Customer Last Name"),max_length=64)
    company = models.CharField(_("Customer's Company Name"),max_length=64)
    email = models.EmailField(_("Customer Email"), unique=True, db_index=True)
    phone_number = models.CharField(max_length=20)
    city = models.CharField(max_length=64)
    country = models.CharField(max_length=64)
    address = models.TextField()
    partner_service = models.ForeignKey(PartnerService, on_delete=models.CASCADE, related_name="customers",default=0)

    def __str__(self):
        return f"{self.first_name} {self.last_name}".title()
    @property
    def display_company(self):
        return f"{self.company.title()}"
#garanti talep tablosu
class WarrantyClaim(models.Model):
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
    claim_type = models.CharField(max_length=3, choices=ClaimTypes.choices, default=ClaimTypes.Repair)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="claims")
    vehicle_driver_name = models.CharField(max_length=64)
    vehicle_driver_phone = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=2, choices=VehicleTypes.choices, default=VehicleTypes.Other)
    vehicle_defect_date = models.DateField(default=date.today())
    vehicle_chassis_number = models.CharField(max_length=64)
    vehicle_registration_date = models.DateField( default= date.today())
    vehicle_kilometer = models.IntegerField()
    defect_category = models.TextField()
    claim_status = models.CharField(max_length=2, choices= ClaimStatus.choices, default= ClaimStatus.New)
    defect_description = models.TextField()
    partner_service = models.ForeignKey(PartnerService, on_delete=models.CASCADE, related_name="claims")
    createdBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_claims")


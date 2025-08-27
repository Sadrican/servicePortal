from users.models import Partner
from django.db import models
from datetime import date
from django.utils.translation import gettext_lazy as _
# Create your models here.

#bayi tablosu
class PartnerService(models.Model):

    name = models.CharField(max_length=64)
    email = models.EmailField(verbose_name="Partner Email")
    phone_number = models.CharField(max_length=20)
    address = models.TextField()

#müşteriler tablosu
class Customer(models.Model):

    customer_first_name = models.CharField(_("Customer First Name"),max_length=64)
    customer_last_name = models.CharField(_("Customer Last Name"),max_length=64)
    customer_company = models.CharField(_("Customer's Company Name"),max_length=64)
    customer_email = models.EmailField(_("Customer Email"), unique=True)
    customer_phone_number = models.CharField(max_length=20)
    customer_city = models.CharField(max_length=64)
    customer_country = models.CharField(max_length=64)
    customer_address = models.TextField()
    customer_partner_service = models.ForeignKey(PartnerService, on_delete=models.CASCADE, related_name="customers",default=0)


#garanti talep tablosu
class WarrantyClaim(models.Model):
    class ClaimTypes(models.TextChoices):
        Repair = "RP", _("Repair")
        Bulletin = "BT", _("Bulletin")

    class VehicleTypes(models.TextChoices):

        CurtainSider = "CS", _("CurtainSider")
        Platform = "PF", _("Platform")
        ContainerChassis = "CC", _("ContainerChassis")
        SwapBody = "SB", _("SwapBody")
        Refer = "RF", _("Reefer")
        Box = "BX", _("Box")
        Silo = "SI", _("Silo")
        Tanker = "TK", _("Tanker")
        LowBed = "LB", _("LowBed")
        Tipper = "TP", _("Tipper")
        Other = "OT", _("Other")

    claim_date = models.DateField(auto_now_add=True)
    claim_last_modified = models.DateField(auto_now=True)
    claim_type = models.CharField(max_length=2, choices=ClaimTypes.choices, default=ClaimTypes.Repair)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="claims")
    vehicle_driver_name = models.CharField(max_length=64)
    vehicle_driver_phone = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=2, choices=VehicleTypes.choices, default=VehicleTypes.Other)
    vehicle_defect_date = models.DateField(default=date.today())
    vehicle_chassis_number = models.CharField(max_length=64)
    vehicle_registration_date = models.DateField( default= date.today())
    vehicle_kilometer = models.IntegerField()
    defect_category = models.TextField()
    claim_status = models.BooleanField(default=False)
    defect_description = models.TextField()




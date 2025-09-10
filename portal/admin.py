from django.contrib import admin
from portal.models import PartnerService, Customer, SparePart, WarrantyClaim, ClaimSparePart

# Register your models here.
admin.site.register(PartnerService)
admin.site.register(Customer)
admin.site.register(SparePart)
admin.site.register(WarrantyClaim)
admin.site.register(ClaimSparePart)

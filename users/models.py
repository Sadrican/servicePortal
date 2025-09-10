from django.contrib.auth.models import AbstractUser,UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from portal.models import PartnerService
from portal.models import WarrantyClaim


# Create your models here.
class User(AbstractUser):
    class Types(models.TextChoices):
        PARTNER = "PARTNER", "Partner"
        PARTNER_ADMIN = "PARTNER_ADMIN", "Partner Admin"
        SSH = "SSH", "SSH"
        SSH_ADMIN = "SSH_ADMIN", "SSH Admin"

    base_role = Types.PARTNER
    role = models.CharField(_('Type'), max_length=20, choices=Types.choices,default=base_role)


    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
        return super().save(*args, **kwargs)
    def __str__(self):
        return self.username

    @property
    def is_partner(self):
        return self.role == self.Types.PARTNER

    @property
    def is_ssh(self):
        return self.role == self.Types.SSH

    @property
    def is_partner_admin(self):
        return self.role == self.Types.PARTNER_ADMIN

    @property
    def is_ssh_admin(self):
        return self.role == self.Types.SSH_ADMIN

    def get_partner_claims(self):
        if not (self.is_partner or self.is_partner_admin):
            return "That is not a partner"
        else:
            try:
                ps = self.partner_fields.partner_service.claims.all()
            except Exception:
                return "Cannot find any claims for this partner service or partner service "
            else:
                return ps



class PartnerManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(role=self.model.Types.PARTNER)


class PartnerFields(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="partner_fields",
    )
    #her servis kullanıcısnın ait olduğu bayi id'si bilgisini tutar
    partner_service=models.ForeignKey(PartnerService, on_delete=models.CASCADE, related_name="users")

    def __str__(self):
        return f"{self.user.username}'s partner fields"


class Partner(User):
    base_role = User.Types.PARTNER
    objects = PartnerManager()

    @property
    def more(self):
        return self.partner_fields

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
        return super().save(*args,**kwargs)



class SSHManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(role=self.model.Types.SSH)


class SSH(User):
    base_role = User.Types.SSH
    objects = SSHManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
        return super().save(*args,**kwargs)


class PartnerAdminManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(role=self.model.Types.PARTNER_ADMIN)


class PartnerAdmin(Partner):
    base_role = User.Types.PARTNER_ADMIN
    objects = PartnerAdminManager()


class SSHAdminManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(role=self.model.Types.SSH_ADMIN)


class SSHAdmin(User):
    base_role = User.Types.SSH_ADMIN
    objects = SSHAdminManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
        return super().save(*args, **kwargs)


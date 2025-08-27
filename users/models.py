from django.contrib.auth.models import AbstractUser,UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class User(AbstractUser):
    class Types(models.TextChoices):
        PARTNER = "PARTNER", "Partner"
        SSH = "SSH", "SSH"

    base_role = Types.PARTNER
    role = models.CharField(_('Type'), max_length=10, choices=Types.choices,default=base_role)


    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
        return super().save(*args, **kwargs)
    def __str__(self):
        return self.username


class PartnerManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(role=self.model.Types.PARTNER)


class PartnerFields(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="partner_fields"
    )
    #her servis kullanıcısnın ait olduğu bayi id'si bilgisini tutar
    partner_service=models.ForeignKey("portal.PartnerService", on_delete=models.CASCADE, related_name="users")

    def __str__(self):
        return f"{self.user.username} partner fields"


class Partner(User):
    base_role = User.Types.PARTNER
    objects = PartnerManager()

    @property
    def more(self):
        return getattr(self, "partner_fields", None)

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


from django import forms
from django.forms.widgets import DateInput
from django.utils.translation import gettext_lazy as _
from .models import WarrantyClaim, Customer

class LoginForm(forms.Form):
    username = forms.CharField(label=_('Username'),max_length=100,widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': _('Username'),
    }))
    password = forms.CharField(label=_('Password'),widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': _('Password')
    }))


class WarrantyClaimForm(forms.ModelForm):
    class Meta:
        model = WarrantyClaim
        # Exclude id (implicit), createdBy, partner_service, and auto date fields
        exclude = ["status",'created_by', 'partner_service', 'claim_date', 'claim_last_modified']
        widgets = {
            "claim_type": forms.Select(attrs={"class": "form-select"}),
            "customer": forms.Select(attrs={"class": "form-select"}),
            "vehicle_driver_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Driver name"}),
            "vehicle_driver_phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone number"}),
            "vehicle_type": forms.Select(attrs={"class": "form-select"}),
            "vehicle_defect_date": DateInput(attrs={"type":"date","class": "form-control"}),
            "vehicle_chassis_number": forms.TextInput(attrs={"class": "form-control"}),
            "vehicle_registration_date": DateInput(attrs={"type":"date","class": "form-control"}),
            "vehicle_kilometer": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "defect_category": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "defect_description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),

        }

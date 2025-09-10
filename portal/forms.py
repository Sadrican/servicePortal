"""Forms for authentication and claim management.

Readability improvements include docstrings and consistent widget attrs.
"""

from django import forms
from django.forms.widgets import DateInput
from django.utils.translation import gettext_lazy as _
from .models import WarrantyClaim, Customer, ClaimSparePart, SparePart


class LoginForm(forms.Form):
    """Simple username/password login form with Bootstrap-friendly widgets."""

    username = forms.CharField(
        label=_('Username'), max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Username')})
    )
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Password')})
    )


class CreateWarrantyClaimForm(forms.ModelForm):
    """Form for creating/editing WarrantyClaim, excluding system fields."""
    parts = forms.JSONField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = WarrantyClaim
        # Exclude id (implicit), status (system), created_by, partner_service, and auto date fields
        exclude = ["status", 'created_by', 'partner_service', 'claim_date', 'claim_last_modified']
        widgets = {
            "claim_type": forms.Select(attrs={"class": "form-select"}),
            "customer": forms.Select(attrs={"class": "form-select"}),
            "vehicle_driver_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Driver name"}),
            "vehicle_driver_phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone number"}),
            "vehicle_type": forms.Select(attrs={"class": "form-select"}),
            "vehicle_defect_date": DateInput(attrs={"type": "date", "class": "form-control"}),
            "vehicle_chassis_number": forms.TextInput(attrs={"class": "form-control"}),
            "vehicle_registration_date": DateInput(attrs={"type": "date", "class": "form-control"}),
            "vehicle_kilometer": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "defect_category": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "defect_description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }

    def clean_parts(self):
        data = self.cleaned_data.get("parts")
        # Optional: validate structure/content
        return data


class WarrantyClaimReadOnlyForm():
    """Read-only variant used in details page."""
    pass


class CreateClaimSparePartForm(forms.ModelForm):
    """Form for adding a spare part to a claim by entering its stock code."""

    class Meta:
        model = ClaimSparePart

        fields = [
            'stock_code', 'quantity', 'currency'
        ]
        widgets = {
            'stock_code': forms.TextInput(attrs={'class': 'form-control'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'approved_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }




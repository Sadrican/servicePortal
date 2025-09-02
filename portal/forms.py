"""Forms for authentication and claim management.

Readability improvements include docstrings and consistent widget attrs.
"""

from django import forms
from django.forms.widgets import DateInput
from django.utils.translation import gettext_lazy as _
from .models import WarrantyClaim, Customer, ClaimSparePart, SparePart, Labour, ClaimLabour


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


class WarrantyClaimForm(forms.ModelForm):
    """Form for creating/editing WarrantyClaim, excluding system fields."""

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


class WarrantyClaimReadOnlyForm(WarrantyClaimForm):
    """Read-only variant used in details page."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.disabled = True


class ClaimSparePartForm(forms.ModelForm):
    """Form for adding a spare part to a claim by entering its stock code."""

    stock_code = forms.CharField(
        label=_('Stock Code'), max_length=64, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter stock code (e.g., ABC-123)')})
    )
    quantity = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    currency = forms.ChoiceField(choices=SparePart.Currency.choices, initial=SparePart.Currency.EUR, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = ClaimSparePart
        fields = ['stock_code', 'quantity', 'currency']

    def save(self, claim, commit=True):
        """Create ClaimSparePart by resolving SparePart from provided stock_code.

        Snapshots stock_code, description, currency and unit_price; computes
        total_price based on selected currency.
        """
        if not self.is_valid():
            raise ValueError("Form must be valid before calling save().")
        stock_code = self.cleaned_data.get('stock_code')
        qty = self.cleaned_data.get('quantity') or 1
        currency = self.cleaned_data.get('currency')
        try:
            spare = SparePart.objects.get(stock_code=stock_code)
        except SparePart.DoesNotExist:
            self.add_error('stock_code', _('Stock code not found'))
            raise
        unit = spare.get_price(currency) or 0
        part = ClaimSparePart(
            claim=claim,
            spare_part=spare,
            stock_code=spare.stock_code,
            description=spare.description,
            currency=currency,
            unit_price=unit,
            quantity=qty,
            total_price=unit * qty,
        )
        if commit:
            part.save()
        return part


class ClaimLabourForm(forms.ModelForm):
    """Form for adding a labour item to a claim by entering its code."""

    code = forms.CharField(
        label=_('Labour Code'), max_length=64, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter labour code')})
    )
    duration = forms.DecimalField(
        min_value=0.25, max_digits=7, decimal_places=2, initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.25'})
    )
    currency = forms.ChoiceField(
        choices=Labour.Currency.choices, initial=Labour.Currency.EUR,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = ClaimLabour
        fields = ['code', 'duration', 'currency']

    def save(self, claim, commit=True):
        """Create ClaimLabour by resolving Labour from provided code."""
        if not self.is_valid():
            raise ValueError("Form must be valid before calling save().")
        code = (self.cleaned_data.get('code') or '').strip()
        dur = self.cleaned_data.get('duration') or 1
        currency = self.cleaned_data.get('currency')
        try:
            lab = Labour.objects.get(code=code)
        except Labour.DoesNotExist:
            self.add_error('code', _('Labour code not found'))
            raise
        rate = lab.get_rate(currency) or 0
        row = ClaimLabour(
            claim=claim,
            labour=lab,
            code=lab.code,
            description=lab.description,
            currency=currency,
            unit_rate=rate,
            duration=dur,
            total_price=rate * dur,
        )
        if commit:
            row.save()
        return row


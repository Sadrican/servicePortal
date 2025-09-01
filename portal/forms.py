from django import forms
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
        exclude = ['createdBy', 'partner_service', 'claim_date', 'claim_last_modified']
        widgets = {
            'claim_type': forms.Select(attrs={'class': 'form-select'}),
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'vehicle_driver_name': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_driver_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-select'}),
            'vehicle_defect_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'vehicle_chassis_number': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_registration_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'vehicle_kilometer': forms.NumberInput(attrs={'class': 'form-control'}),
            'defect_category': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'claim_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'defect_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Limit customers to the partner's own customers if user is partner
        if user and hasattr(user, 'partner_fields'):
            try:
                ps = user.partner_fields.partner_service
                self.fields['customer'].queryset = Customer.objects.filter(partner_service=ps)
            except Exception:
                self.fields['customer'].queryset = Customer.objects.none()

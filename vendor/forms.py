from django import forms
from .models import *

class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = Vendor
        fields = ['fname', 'lname', 'username', 'email', 'phone', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            if widget.__class__.__name__ not in ['CheckboxInput', 'RadioSelect', 'ClearableFileInput']:
                existing_classes = widget.attrs.get('class', '')
                widget.attrs['class'] = (existing_classes + ' form-control').strip()

class ProfileForm(forms.ModelForm):
    
    class Meta:
        model = Vendor
        fields = ['fname', 'lname', 'email', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            if widget.__class__.__name__ not in ['CheckboxInput', 'RadioSelect', 'ClearableFileInput']:
                existing_classes = widget.attrs.get('class', '')
                widget.attrs['class'] = (existing_classes + ' form-control').strip()

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            if widget.__class__.__name__ not in ['CheckboxInput', 'RadioSelect', 'ClearableFileInput']:
                existing_classes = widget.attrs.get('class', '')
                widget.attrs['class'] = (existing_classes + ' form-control').strip()

class DiamondForm(forms.ModelForm):
    class Meta:
        model = Diamond
        exclude = ['sr_no', 'vendor','price_per_carat', 'total_amount', 'measurements', 'created_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            if widget.__class__.__name__ not in ['CheckboxInput', 'RadioSelect', 'ClearableFileInput']:
                existing_classes = widget.attrs.get('class', '')
                widget.attrs['class'] = (existing_classes + ' form-control').strip()

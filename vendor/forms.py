from django import forms
from .models import *

class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = Vendor
        fields = ['fname', 'lname', 'username', 'email', 'phone', 'password1', 'password2']

class ProfileForm(forms.ModelForm):
    
    class Meta:
        model = Vendor
        fields = ['fname', 'lname', 'email', 'phone']

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class DiamondForm(forms.ModelForm):
    class Meta:
        model = Diamond
        exclude = ['sr_no', 'vendor','price_per_carat', 'total_amount', 'measurements', 'created_at']

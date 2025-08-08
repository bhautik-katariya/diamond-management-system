from django import forms
from vendor.models import Vendor
from customer.models import Customer

# forms.py
from django import forms
from vendor.models import Vendor
from customer.models import Customer

class RegistrationForm(forms.Form):
    fname = forms.CharField(max_length=255, label="First Name")
    lname = forms.CharField(max_length=255, label="Last Name")
    username = forms.CharField(max_length=150, label="Username")
    email = forms.EmailField(label="Email")
    phone = forms.CharField(max_length=15, label="Phone")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.RadioSelect):
                widget.attrs['class'] = 'form-check-input'
            else:
                existing_classes = widget.attrs.get('class', '')
                widget.attrs['class'] = (existing_classes + ' form-control').strip()

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        if user_type not in ['vendor', 'customer']:
            raise forms.ValidationError("Invalid user type selected.")

        # Dynamically determine the model
        Model = Vendor if user_type == 'vendor' else Customer

        # Username check
        username = cleaned_data.get('username')
        if username and Model.objects.filter(username=username).exists():
            raise forms.ValidationError(f"This username is already taken by a {user_type}.")

        # Email check
        email = cleaned_data.get('email')
        if email and Model.objects.filter(email=email).exists():
            raise forms.ValidationError(f"This email is already registered by a {user_type}.")

        # Phone check
        phone = cleaned_data.get('phone')
        if phone and Model.objects.filter(phone=phone).exists():
            raise forms.ValidationError(f"This phone number is already registered by a {user_type}.")

        return cleaned_data



class ProfileForm(forms.ModelForm):
    class Meta:
        model = Vendor  # default, will be replaced dynamically
        fields = ['fname', 'lname', 'email', 'phone']

    def __init__(self, *args, **kwargs):
        self.user_type = kwargs.pop('user_type')
        self.user_id = kwargs.pop('user_id')
        super().__init__(*args, **kwargs)

        # Dynamically switch model if user is customer
        if self.user_type == 'customer':
            self._meta.model = Customer

        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            widget = field.widget
            if widget.__class__.__name__ not in ['CheckboxInput', 'RadioSelect', 'ClearableFileInput']:
                existing_classes = widget.attrs.get('class', '')
                widget.attrs['class'] = (existing_classes + ' form-control').strip()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        Model = Vendor if self.user_type == 'vendor' else Customer
        if Model.objects.exclude(id=self.user_id).filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        Model = Vendor if self.user_type == 'vendor' else Customer
        if Model.objects.exclude(id=self.user_id).filter(phone=phone).exists():
            raise forms.ValidationError("This phone number is already registered.")
        return phone

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            if widget.__class__.__name__ not in ['CheckboxInput', 'RadioSelect', 'ClearableFileInput']:
                existing_classes = widget.attrs.get('class', '')
                widget.attrs['class'] = (existing_classes + ' form-control').strip()
            elif widget.__class__.__name__ == 'RadioSelect':
                widget.attrs['class'] = 'form-check-input'

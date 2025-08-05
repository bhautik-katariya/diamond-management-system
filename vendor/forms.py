from django import forms
from .models import Diamond

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

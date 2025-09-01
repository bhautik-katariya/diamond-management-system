from django import forms
from .models import Diamond

class DiamondForm(forms.ModelForm):
    class Meta:
        model = Diamond
        exclude = ['vendor','price_per_carat', 'total_amount', 'measurements', 'created_at']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.is_bound and self.errors:
            # self.data is immutable QueryDict, so copy it first
            data_copy = self.data.copy()

            for field_name in self.errors.keys():
                if field_name in data_copy:
                    data_copy[field_name] = ''   # clear textbox/number
            self.data = data_copy  # replace with cleaned copy

        # Add bootstrap classes
        for field_name, field in self.fields.items():
            widget = field.widget
            if widget.__class__.__name__ not in ['CheckboxInput', 'RadioSelect', 'ClearableFileInput']:
                existing_classes = widget.attrs.get('class', '')
                if field_name in self.errors:
                    widget.attrs['class'] = (existing_classes + ' form-control is-invalid').strip()
                else:
                    widget.attrs['class'] = (existing_classes + ' form-control').strip()

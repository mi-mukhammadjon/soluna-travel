# bookings/forms.py
from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'travel_date',
            'num_adults',
            'num_children',
            'special_requests',
        ]
        widgets = {
            'travel_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': timezone.now().date().isoformat(),
            }),
            'num_adults': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1, 'max': 20,
            }),
            'num_children': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0, 'max': 10,
            }),
            'special_requests': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Dietary needs, accessibility, etc.'),
            }),
        }
        labels = {
            'travel_date': _('Travel Date'),
            'num_adults': _('Adults'),
            'num_children': _('Children'),
            'special_requests': _('Special Requests'),
        }

    def clean_travel_date(self):
        date = self.cleaned_data['travel_date']
        if date < timezone.now().date():
            raise forms.ValidationError(_("Travel date cannot be in the past."))
        return date

    def clean_num_adults(self):
        n = self.cleaned_data['num_adults']
        if n < 1:
            raise forms.ValidationError(_("At least 1 adult is required."))
        return n
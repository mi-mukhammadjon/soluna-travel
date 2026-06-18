from django import forms
from django.utils import timezone
from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['travel_date', 'num_adults', 'num_children', 'special_requests']
        widgets = {
            'travel_date': forms.DateInput(
                attrs={'type': 'date', 'min': timezone.now().date().isoformat()}
            ),
            'num_adults': forms.NumberInput(attrs={'min': 1, 'max': 20}),
            'num_children': forms.NumberInput(attrs={'min': 0, 'max': 20}),
            'special_requests': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_travel_date(self):
        date = self.cleaned_data['travel_date']
        if date < timezone.now().date():
            raise forms.ValidationError("Sana o'tib ketgan.")
        if (date - timezone.now().date()).days < 1:
            raise forms.ValidationError("Kamida 1 kun oldin bron qiling.")
        return date

    def clean_num_adults(self):
        num = self.cleaned_data['num_adults']
        if num < 1:
            raise forms.ValidationError("Kamida 1 kattalar bo'lishi kerak.")
        return num
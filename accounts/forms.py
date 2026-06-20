import re
from django import forms
from django.conf import settings
from .models import User

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'avatar', 'preferred_language']
        widgets = {
            'preferred_language': forms.Select(
                choices=settings.LANGUAGES,
                attrs={'class': 'form-control'}
            )
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower()
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Bu email boshqa foydalanuvchiga tegishli.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if phone and not re.fullmatch(r'^\+?[\d\s\-]+$', phone):
            raise forms.ValidationError("Telefon raqam noto'g'ri formatda.")
        return phone
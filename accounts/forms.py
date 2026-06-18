import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

# Tillar ro'yxatini formaning ichiga emas, tashqariga o'zgarmas qilib (constant) yozamiz. 
# Eng yaxshi praktika: buni settings.LANGUAGES dan olish yoki Modelning o'zida yozish.
LANGUAGE_CHOICES = [
    ('uz', "O'zbek"),
    ('ru', 'Русский'),
    ('en', 'English'),
    ('zh-hans', '中文'),
    ('ar', 'العربية'),
    ('de', 'Deutsch'),
    ('fr', 'Français'),
    ('ja', '日本語'),
    ('ko', '한국어'),
]

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    phone = forms.CharField(max_length=20, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        # UserCreationForm avtomat ravishda password1 va password2 ni qo'shadi. 
        # Shuning uchun ularni Meta fields'ga yozish ortiqcha.
        fields = ['username', 'first_name', 'last_name', 'email', 'phone']

    def clean_email(self):
        # Emailni har doim kichik harflarda (lowercase) saqlash va tekshirish kerak
        email = self.cleaned_data.get('email', '').lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu email allaqachon ro'yxatdan o'tgan.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if phone:
            # Regex orqali validatsiya: faqat + belgisi (ixtiyoriy), raqamlar, bo'sh joy va chiziqchalar ruxsat etiladi
            if not re.fullmatch(r'^\+?[\d\s\-]+$', phone):
                raise forms.ValidationError("Telefon raqam noto'g'ri formatda.")
        return phone


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'avatar', 'preferred_language']
        widgets = {
            'preferred_language': forms.Select(
                choices=LANGUAGE_CHOICES,
                attrs={'class': 'form-control'} # Eslatmangiz asosida class qo'shildi
            )
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower()
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Bu email boshqa foydalanuvchiga tegishli.")
        return email
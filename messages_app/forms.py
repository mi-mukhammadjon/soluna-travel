import time
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import ContactMessage

# Forma to'ldirish uchun minimal vaqt (sekund). Bundan tez -> bot.
MIN_FILL_SECONDS = 3
# Off-screen honeypot uslubi (odam ko'rmaydi, ekran o'quvchi o'qimaydi)
_HP_STYLE = ('position:absolute!important;left:-9999px!important;top:-9999px!important;'
             'width:1px;height:1px;opacity:0;overflow:hidden;')


class ContactForm(forms.ModelForm):
    # ── Anti-bot: honeypot (yashirin maydon — botlar to'ldiradi) ──
    website = forms.CharField(
        required=False, label='',
        widget=forms.TextInput(attrs={
            'tabindex': '-1', 'autocomplete': 'off', 'aria-hidden': 'true',
            'style': _HP_STYLE, 'class': 'hp-field',
        }),
    )
    # ── Anti-bot: forma ochilgan vaqt (time-trap) ──
    ts = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'body']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ismingiz'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+998 90 123 45 67'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mavzu'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Xabaringiz...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            self.fields['ts'].initial = str(int(time.time()))

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if phone and not phone.replace('+', '').replace(' ', '').replace('-', '').isdigit():
            raise forms.ValidationError("Telefon raqam noto'g'ri formatda.")
        return phone

    def clean(self):
        cleaned = super().clean()
        # 1) Honeypot to'ldirilgan bo'lsa -> bot
        if (cleaned.get('website') or '').strip():
            raise forms.ValidationError(_('Spam detected.'))
        # 2) Juda tez yuborilgan bo'lsa -> bot
        raw_ts = (self.data.get('ts') or '').strip()
        try:
            elapsed = int(time.time()) - int(raw_ts)
        except (TypeError, ValueError):
            elapsed = -1
        if elapsed < MIN_FILL_SECONDS:
            raise forms.ValidationError(_('The form was submitted too quickly. Please try again.'))
        return cleaned


class ReplyForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['reply_text']
        widgets = {
            'reply_text': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Javob matni...'})
        }
        labels = {
            'reply_text': 'Javob'
        }
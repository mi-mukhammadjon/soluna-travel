from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
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

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if phone and not phone.replace('+', '').replace(' ', '').replace('-', '').isdigit():
            raise forms.ValidationError("Telefon raqam noto'g'ri formatda.")
        return phone


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
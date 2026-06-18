from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(i, f"{i} ★") for i in range(1, 6)],
        widget=forms.RadioSelect,
    )

    class Meta:
        model = Review
        fields = ['rating', 'title', 'body']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Sarlavha (ixtiyoriy)'}),
            'body': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Fikringizni yozing...'}),
        }

    def clean_body(self):
        body = self.cleaned_data.get('body', '')
        if len(body) < 10:
            raise forms.ValidationError("Izoh kamida 10 ta belgi bo'lishi kerak.")
        return body
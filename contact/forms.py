from django import forms

from .models import ContactInquiry


class ContactInquiryForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactInquiry
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your name', 'autocomplete': 'name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'you@example.com', 'autocomplete': 'email'}),
            'subject': forms.TextInput(attrs={'placeholder': 'What is this about?'}),
            'message': forms.Textarea(attrs={'rows': 5, 'placeholder': 'How can we help?'}),
        }

    def clean_website(self):
        website = self.cleaned_data['website']
        if website:
            raise forms.ValidationError('Invalid form submission.')
        return website
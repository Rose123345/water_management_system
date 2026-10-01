from django import forms

from .models import ContactInquiry


class ContactInquiryForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactInquiry
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }

    def clean_website(self):
        website = self.cleaned_data['website']
        if website:
            raise forms.ValidationError('Invalid form submission.')
        return website
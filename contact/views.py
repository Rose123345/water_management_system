from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ContactInquiryForm


def contact(request):
    if request.method == 'POST':
        form = ContactInquiryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thanks for reaching out. Your message has been received.')
            return redirect('contact:contact')
    else:
        form = ContactInquiryForm()

    return render(request, 'contact/contact.html', {'form': form})
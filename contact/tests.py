from django.test import TestCase

from .models import ContactInquiry


class ContactPageTests(TestCase):
    def test_contact_page_is_public(self):
        response = self.client.get('/contact/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Send an inquiry')

    def test_valid_submission_is_saved(self):
        response = self.client.post('/contact/', {
            'name': 'Amina Doe',
            'email': 'amina@example.com',
            'subject': 'Product question',
            'message': 'Please share package options.',
            'website': '',
        })

        self.assertRedirects(response, '/contact/')
        self.assertTrue(ContactInquiry.objects.filter(email='amina@example.com').exists())

    def test_invalid_submission_is_not_saved(self):
        response = self.client.post('/contact/', {
            'name': 'Amina Doe',
            'email': 'not-an-email',
            'subject': 'Product question',
            'message': 'Please share package options.',
            'website': '',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactInquiry.objects.count(), 0)
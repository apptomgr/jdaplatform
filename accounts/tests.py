from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import UserRegisterForm

User = get_user_model()


VALID_FORM_DATA = {
    "first_name": "Terms",
    "last_name": "Tester",
    "email": "terms_tester@example.com",
    "username": "terms_tester_user",
    "password1": "SomeStrongPass123!",
    "password2": "SomeStrongPass123!",
}


class RegistrationTermsAcceptanceTests(TestCase):
    """
    Registration must hard-gate on the Terms and Conditions checkbox, both
    at the form level and, more importantly, at the view/POST level so a
    client that never runs the page's JS (or a direct POST bypassing the
    browser entirely) still cannot register without accepting.
    """

    def test_form_is_invalid_without_terms_accepted(self):
        form = UserRegisterForm(data=VALID_FORM_DATA)
        self.assertFalse(form.is_valid())
        self.assertIn("terms_accepted", form.errors)

    def test_form_is_valid_with_terms_accepted(self):
        form = UserRegisterForm(data={**VALID_FORM_DATA, "terms_accepted": True})
        self.assertTrue(form.is_valid(), form.errors)

    def test_register_view_rejects_post_without_terms_accepted(self):
        response = self.client.post(reverse("register"), data=VALID_FORM_DATA)
        self.assertEqual(response.status_code, 200)  # re-renders the form, no redirect
        self.assertFalse(User.objects.filter(username="terms_tester_user").exists())
        self.assertContains(response, "You must accept the Terms and Conditions to register.")

    def test_register_view_succeeds_with_terms_accepted(self):
        response = self.client.post(
            reverse("register"),
            data={**VALID_FORM_DATA, "terms_accepted": True},
        )
        self.assertRedirects(response, reverse("verification_sent"))
        self.assertTrue(User.objects.filter(username="terms_tester_user").exists())

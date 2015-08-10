import datetime
import re

from django.core import mail
from django.test import TestCase
from django.utils.six import text_type

from userena.models import UserenaSignup
from userena import settings as userena_settings
from userena.utils import get_user_model

User = get_user_model()

MUGSHOT_RE = re.compile('^[a-f0-9]{40}$')


class UserenaSignupModelTests(TestCase):
    """ Test the model of UserenaSignup """
    user_info = {'username': 'alice',
                 'password': 'swordfish',
                 'email': 'alice@example.com'}

    fixtures = ['users']

    def test_stringification(self):
        """
        Test the stringification of a ``UserenaSignup`` object. A
        "human-readable" representation of an ``UserenaSignup`` object.

        """
        signup = UserenaSignup.objects.get(pk=1)
        self.failUnlessEqual(signup.__str__(),
                             signup.user.username)

    def test_change_email(self):
        """ TODO """
        pass

    def test_activation_expired_account(self):
        """
        ``UserenaSignup.activation_key_expired()`` is ``True`` when the
        ``activation_key_created`` is more days ago than defined in
        ``USERENA_ACTIVATION_DAYS``.

        """
        user = UserenaSignup.objects.create_user(**self.user_info)
        user.date_joined -= datetime.timedelta(days=userena_settings.USERENA_ACTIVATION_DAYS + 1)
        user.save()

        user = User.objects.get(username='alice')
        self.failUnless(user.userena_signup.activation_key_expired())

    def test_activation_used_account(self):
        """
        An user cannot be activated anymore once the activation key is
        already used.

        """
        user = UserenaSignup.objects.create_user(**self.user_info)
        activated_user = UserenaSignup.objects.activate_user(user.userena_signup.activation_key)
        self.failUnless(activated_user.userena_signup.activation_key_expired())

    def test_activation_unexpired_account(self):
        """
        ``UserenaSignup.activation_key_expired()`` is ``False`` when the
        ``activation_key_created`` is within the defined timeframe.``

        """
        user = UserenaSignup.objects.create_user(**self.user_info)
        self.failIf(user.userena_signup.activation_key_expired())

    def test_activation_email(self):
        """
        When a new account is created, a activation e-mail should be send out
        by ``UserenaSignup.send_activation_email``.

        """
        new_user = UserenaSignup.objects.create_user(**self.user_info)
        self.failUnlessEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user_info['email']])

    def test_plain_email(self):
        """
        If HTML emails are disabled, check that outgoing emails are not multipart
        """
        userena_settings.USERENA_HTML_EMAIL = False
        new_user = UserenaSignup.objects.create_user(**self.user_info)
        self.failUnlessEqual(len(mail.outbox), 1)
        self.assertEqual(text_type(mail.outbox[0].message()).find("multipart/alternative"),-1)

    def test_html_email(self):
        """
        If HTML emails are enabled, check outgoings emails are multipart and
        that different html and plain text templates are used
        """
        userena_settings.USERENA_HTML_EMAIL = True
        userena_settings.USERENA_USE_PLAIN_TEMPLATE = True

        new_user = UserenaSignup.objects.create_user(**self.user_info)

        # Reset configuration
        userena_settings.USERENA_HTML_EMAIL = False
        self.failUnlessEqual(len(mail.outbox), 1)
        self.assertTrue(text_type(mail.outbox[0].message()).find("multipart/alternative")>-1)
        self.assertTrue(text_type(mail.outbox[0].message()).find("text/plain")>-1)
        self.assertTrue(text_type(mail.outbox[0].message()).find("text/html")>-1)
        self.assertTrue(text_type(mail.outbox[0].message()).find("<html>")>-1)
        self.assertTrue(text_type(mail.outbox[0].message()).find("<p>Thank you for signing up")>-1)
        self.assertFalse(mail.outbox[0].body.find("<p>Thank you for signing up")>-1)

    def test_generated_plain_email(self):
        """
        If HTML emails are enabled and plain text template are disabled,
        check outgoings emails are multipart and that plain text is generated
        from html body
        """
        userena_settings.USERENA_HTML_EMAIL = True
        userena_settings.USERENA_USE_PLAIN_TEMPLATE = False

        new_user = UserenaSignup.objects.create_user(**self.user_info)

        # Reset configuration
        userena_settings.USERENA_HTML_EMAIL = False
        userena_settings.USERENA_USE_PLAIN_TEMPLATE = True

        self.failUnlessEqual(len(mail.outbox), 1)
        self.assertTrue(text_type(mail.outbox[0].message()).find("multipart/alternative")>-1)
        self.assertTrue(text_type(mail.outbox[0].message()).find("text/plain")>-1)
        self.assertTrue(text_type(mail.outbox[0].message()).find("text/html")>-1)
        self.assertTrue(text_type(mail.outbox[0].message()).find("<html>")>-1)
        self.assertTrue(text_type(mail.outbox[0].message()).find("<p>Thank you for signing up")>-1)
        self.assertTrue(mail.outbox[0].body.find("Thank you for signing up")>-1)

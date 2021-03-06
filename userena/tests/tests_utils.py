
from django.test import TestCase
from django.conf import settings
from django.utils.six.moves.urllib_parse import urlparse, parse_qs

from userena.utils import get_gravatar, signin_redirect, get_protocol, get_user_model


class UtilsTests(TestCase):
    """ Test the extra utils methods """
    fixtures = ['users']

    def test_get_gravatar(self):
        template = 's=%(size)s&d=%(type)s'

        # Check the defaults.
        parsed = urlparse(get_gravatar('alice@example.com'))
        self.failUnlessEqual(
            parse_qs(parsed.query),
            parse_qs(template % {'size': 80, 'type': 'identicon'})
        )

        # Check different size
        parsed = urlparse(get_gravatar('alice@example.com', size=200))
        self.failUnlessEqual(
            parse_qs(parsed.query),
            parse_qs(template % {'size': 200, 'type': 'identicon'})
        )

        # Check different default
        parsed = urlparse(get_gravatar('alice@example.com', default='404'))
        self.failUnlessEqual(
            parse_qs(parsed.query),
            parse_qs(template % {'size': 80, 'type': '404'})
        )

    def test_signin_redirect(self):
        """
        Test redirect function which should redirect the user after a
        succesfull signin.

        """
        # Test with a requested redirect
        self.failUnlessEqual(signin_redirect(redirect='/accounts/'), '/accounts/')

        # Test with only the user specified
        user = get_user_model().objects.get(pk=1)
        self.failUnlessEqual(signin_redirect(user=user),
                             '/accounts/%s/' % user.username)

        # The ultimate fallback, probably never used
        self.failUnlessEqual(signin_redirect(), settings.LOGIN_REDIRECT_URL)

    def test_get_protocol(self):
        """ Test if the correct protocol is returned """
        self.failUnlessEqual(get_protocol(), 'http')

        with self.settings(USERENA_USE_HTTPS=True):
            self.failUnlessEqual(get_protocol(), 'https')

from datetime import timedelta

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication, get_authorization_header

TOKEN_EXPIRATION_DAYS = 1


class ExpiringTokenAuthentication(TokenAuthentication):
    """
    The Expiring Token authentication class.
    Extends TokenAuthenticaton to suppoprt token expiration and to check environment access rights.
    """

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        """

        :param key: token from http authentication header
        :return: user with preseleted organization and token
        """
        model = self.get_model()
        try:
            token = model.objects.select_related(
                'user', 'user__organization'
            ).get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        user = token.user

        if not user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        if not user.verified_accounts:
            raise exceptions.AuthenticationFailed(_('User hasn\'t verified any account yet.'))

        if token.created < timezone.now() - timedelta(days=TOKEN_EXPIRATION_DAYS):
            token.delete()
            raise exceptions.AuthenticationFailed(_('Token has expired.'))

        return user, token

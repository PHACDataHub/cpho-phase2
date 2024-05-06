"""Code related to custom oauth authentication"""

from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.sessions.models import Session
from django.db.models import Q
from django.http.request import HttpRequest

from cpho.util import is_allowed_email


class OAuthBackend(BaseBackend):
    """Authentication backend used by OAuth to create users based on their
    Microsoft credentials."""

    def _should_update(self, user_info, user):
        return (
            user_info.get("email") != user.email
            or user_info.get("name") != user.name
            or user_info.get("oid") != user.username
        )

    def _sync_user(self, user, user_info, force=False):
        # Update the user object if required.
        if force or self._should_update(user_info, user):
            user.email = user_info.get("email", user.email).lower()
            user.name = user_info.get("name", user.name)
            user.username = user_info.get("oid", user.username)
            user.save()

    def _delete_all_user_sessions(self, user):
        sessions = Session.objects.all()

        for old_session in sessions:
            if str(user.pk) == old_session.get_decoded().get("_auth_user_id"):
                old_session.delete()

    def authenticate(
        self,
        request: HttpRequest,
        user_info: dict | None = None,
        **kwargs: Any,
    ) -> AbstractBaseUser | None:
        # Lookup sign-in user in database, create if it does not exist.
        if user_info is not None:
            oid = user_info.get("oid", None)
            email = user_info.get("email", None)
            if not oid:
                return None
            user_model = get_user_model()

            user = user_model.objects.filter(
                Q(username=oid) | Q(email__iexact=email)
            ).first()
            if user:
                self._sync_user(user, user_info)
            else:
                # register this new user

                if settings.DISABLE_AUTO_REGISTRATION:
                    return None

                if not is_allowed_email(email):
                    # only allow phac emails to register
                    return None

                user = user_model(username=oid)
                self._sync_user(user, user_info, True)

            self._delete_all_user_sessions(user)

            return user
        return None

    def get_user(self, user_id):
        # Return the user based on the primary key.  This method is called for
        # every request after a user is authenticated to populate the session.
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None

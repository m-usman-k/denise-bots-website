"""
MongoDB-compatible AppConfig overrides.

Django's built-in apps and allauth set their own default_auto_field which
overrides the global DEFAULT_AUTO_FIELD setting. We subclass each AppConfig
to force ObjectIdAutoField so django-mongodb-backend system checks pass.
"""
from django.contrib.admin.apps import AdminConfig
from django.contrib.auth.apps import AuthConfig
from django.contrib.contenttypes.apps import ContentTypesConfig
from django.contrib.sessions.apps import SessionsConfig
from allauth.account.apps import AccountConfig
from allauth.socialaccount.apps import SocialAccountConfig

_OBJECT_ID = 'django_mongodb_backend.fields.ObjectIdAutoField'


class MongoAdminConfig(AdminConfig):
    default_auto_field = _OBJECT_ID


class MongoAuthConfig(AuthConfig):
    default_auto_field = _OBJECT_ID


class MongoContentTypesConfig(ContentTypesConfig):
    default_auto_field = _OBJECT_ID


class MongoSessionsConfig(SessionsConfig):
    default_auto_field = _OBJECT_ID


class MongoAccountConfig(AccountConfig):
    default_auto_field = _OBJECT_ID


class MongoSocialAccountConfig(SocialAccountConfig):
    default_auto_field = _OBJECT_ID

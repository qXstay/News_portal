"""
URL configuration for NewsPortal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from allauth.socialaccount.providers.google import views as google_views
from allauth.socialaccount.providers.yandex import views as yandex_views
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.yandex.views import YandexAuth2Adapter
from allauth.socialaccount.providers.google.views import oauth2_login as google_login
from allauth.socialaccount.providers.yandex.views import oauth2_login as yandex_login
from django.views.i18n import set_language

handler403 = 'portal.views.custom_permission_denied'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pages/', include('django.contrib.flatpages.urls')),
    path('accounts/', include('allauth.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('accounts/google/login/', google_views.oauth2_login, name='google_login'),
    path('accounts/google/login/callback/', google_views.oauth2_callback, name='google_callback'),
    path('accounts/yandex/login/', yandex_views.oauth2_login, name='yandex_login'),
    path('accounts/yandex/login/callback/', yandex_views.oauth2_callback, name='yandex_callback'),
    path('accounts/google/login/', google_login, name='google_login'),
    path('accounts/yandex/login/', yandex_login, name='yandex_login'),
    path('i18n/setlang/', set_language, name='set_language'),
    path('i18n/', include('django.conf.urls.i18n')),
]


urlpatterns += i18n_patterns(
    path('', include('portal.urls')),
    prefix_default_language=True,
)
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from django.core.exceptions import MultipleObjectsReturned

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_app(self, request, provider):
        try:
            return SocialApp.objects.get(provider=provider)
        except MultipleObjectsReturned:
            return SocialApp.objects.filter(provider=provider).first()
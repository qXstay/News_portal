from allauth.account.models import EmailAddress
from django.core.exceptions import PermissionDenied

class EmailVerifiedRequiredMixin:
    """
    Запрещает доступ к вьюхам, если пользователь не подтвердил email.
    """
    def dispatch(self, request, *args, **kwargs):
        if not EmailAddress.objects.filter(user=request.user, verified=True).exists():
            raise PermissionDenied("Пожалуйста, подтвердите email для доступа к этой странице.")
        return super().dispatch(request, *args, **kwargs)
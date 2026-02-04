# jdasubscriptions/services.old.py
from django.utils import timezone
from .models import UserSubscription, CustomerSubscription, InstitutionSubscription
from django.utils import timezone



def user_has_active_subscription(user) -> bool:

    if not user.is_authenticated:
        return False

    return UserSubscription.objects.filter(
        user=user,
        status="active",
        end_date__gte=timezone.now(),
    ).exists()





def user_has_active_subscription(user):
    if not user.is_authenticated:
        print(f"services.py 25 user is authenticated: {user.is_authenticated}")
        return False

    return (
            CustomerSubscription.objects.filter(user=user, status="active").exists()
            or InstitutionSubscription.objects.filter(user=user, status="active").exists()
    )



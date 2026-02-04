
from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription, CustomerSubscription, InstitutionSubscription
from django.contrib import admin, messages
from django.utils import timezone


admin.site.register(SubscriptionPlan)
admin.site.register(UserSubscription)
#0Charloadmin.site.register(CustomerSubscription)
#admin.site.register(InstitutionSubscription)

#from django.contrib import admin
#from .models import SubscriptionPlan
#
# @admin.register(SubscriptionPlan)
# class SubscriptionPlanAdmin(admin.ModelAdmin):
#     list_display = ("name", "plan_type", "monthly_price", "yearly_price", "is_active", "sort_order")
#     list_filter = ("plan_type", "is_active")
#     ordering = ("sort_order",)

@admin.register(CustomerSubscription)
class CustomerSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "plan",
        "status",
        "starts_at",
        "ends_at",
        "paystack_reference",
        "created_at",
    )

    list_filter = (
        "status",
        "plan",
        "created_at",
    )

    search_fields = (
        "user__email",
        "user__username",
        "paystack_reference",
    )

    ordering = ("-created_at",)

    # 🔒 Read-only fields
    readonly_fields = (
        "user",
        "plan",
        "status",
        "starts_at",
        "ends_at",
        "paystack_reference",
        "paystack_status",
        "created_at",
    )

    actions = ["force_expire_subscription"]



    @admin.action(description="Force expire selected subscriptions")
    def force_expire_subscription(self, request, queryset):
        now = timezone.now()

        active_subscriptions = queryset.filter(status="active")

        if not active_subscriptions.exists():
            self.message_user(
                request,
                "No active subscriptions selected.",
                level=messages.WARNING,
            )
            return

        count = active_subscriptions.update(
            status="expired",
            ends_at=now,
        )

        self.message_user(
            request,
            f"{count} subscription(s) were force expired.",
            level=messages.SUCCESS,
        )


    def has_add_permission(self, request):
        return False  # No manual creation

    def has_delete_permission(self, request, obj=None):
        return False  # No deletion ever

    def has_change_permission(self, request, obj=None):
        # Allow change view (read-only), but not inline edits
        return True


@admin.register(InstitutionSubscription)
class InstitutionSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "plan",
        "status",
        "starts_at",
        "ends_at",
        "paystack_reference",
        "created_at",
    )

    list_filter = (
        "status",
        "plan",
        "created_at",
    )

    search_fields = (
        "user__email",
        "user__username",
        "paystack_reference",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "user",
        "plan",
        "status",
        "starts_at",
        "ends_at",
        "paystack_reference",
        "paystack_status",
        "created_at",
    )

    actions = ["force_expire_subscription"]


    @admin.action(description="Force expire selected subscriptions")
    def force_expire_subscription(self, request, queryset):
        now = timezone.now()

        active_subscriptions = queryset.filter(status="active")

        if not active_subscriptions.exists():
            self.message_user(
                request,
                "No active subscriptions selected.",
                level=messages.WARNING,
            )
            return

        count = active_subscriptions.update(
            status="expired",
            ends_at=now,
        )

        self.message_user(
            request,
            f"{count} institution subscription(s) were force expired.",
            level=messages.SUCCESS,
        )


def has_add_permission(self, request):
    return False

def has_delete_permission(self, request, obj=None):
    return False

def has_change_permission(self, request, obj=None):
    return True



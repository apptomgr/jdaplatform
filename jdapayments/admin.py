from django.contrib import admin, messages
from jdapayments.models import Payment
from jdapayments.services import reprocess_payment
from django.utils.html import format_html



@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "user",
        "amount",
        "status",
        "created_at",
    )

    list_filter = ("status", "created_at")
    search_fields = ("reference", "user__email")

    readonly_fields = (
        "reference",
        "user",
        "amount",
        "status",
        "raw_response",
        "created_at",
    )

    ordering = ("-created_at",)

    actions = ["reprocess_selected_payments"]

    # 🔒 No editing payments manually
    def has_change_permission(self, request, obj=None):
        return False

    # 🔒 No deletion
    def has_delete_permission(self, request, obj=None):
        return False

    # -----------------------------
    # Admin Action
    # -----------------------------
    @admin.action(description="🔁 Reprocess selected payments")
    def reprocess_selected_payments(self, request, queryset):
        success = 0
        skipped = 0

        for payment in queryset:
            result = reprocess_payment(payment.reference)
            if "successfully" in result.lower():
                success += 1
            else:
                skipped += 1

        if success:
            self.message_user(
                request,
                f"✅ {success} payment(s) reprocessed successfully.",
                level=messages.SUCCESS,
            )

        if skipped:
            self.message_user(
                request,
                f"⚠️ {skipped} payment(s) skipped (already processed or invalid).",
                level=messages.WARNING,
            )


from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription, CustomerSubscription, InstitutionSubscription

admin.site.register(SubscriptionPlan)
admin.site.register(UserSubscription)
admin.site.register(CustomerSubscription)
admin.site.register(InstitutionSubscription)

#from django.contrib import admin
#from .models import SubscriptionPlan
#
# @admin.register(SubscriptionPlan)
# class SubscriptionPlanAdmin(admin.ModelAdmin):
#     list_display = ("name", "plan_type", "monthly_price", "yearly_price", "is_active", "sort_order")
#     list_filter = ("plan_type", "is_active")
#     ordering = ("sort_order",)

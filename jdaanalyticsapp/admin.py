from django.contrib import admin

from .models import IndexPriceModel, SecurityPriceModel, SecurityModel


admin.site.register(IndexPriceModel)
admin.site.register(SecurityPriceModel)
admin.site.register(SecurityModel)

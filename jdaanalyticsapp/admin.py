from django.contrib import admin

from .models import IndexModel, IndexPriceModel, SecurityPriceModel, SecurityModel

admin.site.register(IndexModel)
admin.site.register(IndexPriceModel)
admin.site.register(SecurityPriceModel)
admin.site.register(SecurityModel)

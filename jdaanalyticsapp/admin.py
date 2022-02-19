from django.contrib import admin
from .models import IndexModel, IndexPriceModel, SecurityPriceModel, SecurityModel, ExchangeModel, StockModel, BondModel

admin.site.register(IndexModel)
admin.site.register(IndexPriceModel)
admin.site.register(SecurityPriceModel)
admin.site.register(ExchangeModel)
admin.site.register(SecurityModel)
admin.site.register(StockModel)
admin.site.register(BondModel)


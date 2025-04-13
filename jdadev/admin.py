from django.contrib import admin
from .models import StockDailyValuesModel, BondModel,  ClientPortfolioModel, ClientEquityAndRightsModel, ClientBondsModel, Daily_stock, Option, \
    Country, City, MutualFundModel, DepositaireModel,ClientMutualFundsModel, ClientProfileModel, TransactionFeesModel


admin.site.register(StockDailyValuesModel)
admin.site.register(BondModel)
admin.site.register(ClientBondsModel)

admin.site.register(ClientPortfolioModel)
admin.site.register(ClientEquityAndRightsModel)
admin.site.register(MutualFundModel)
admin.site.register(ClientProfileModel)
admin.site.register(DepositaireModel)
admin.site.register(ClientMutualFundsModel)

admin.site.register(TransactionFeesModel)

admin.site.register(Daily_stock)
admin.site.register(Option)

admin.site.register(Country)
admin.site.register(City)
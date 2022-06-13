from django.contrib import admin
from .models import *

admin.site.register(SectorModel)
admin.site.register(CompanyModel)
admin.site.register(AddressModel)
admin.site.register(LeadersModel)
admin.site.register(CountryModel)
admin.site.register(EconomicDataModel)
admin.site.register(TradePartnersModel)
admin.site.register(OtherIndicatorsModel)

admin.site.register(FinancialStatementModel)
admin.site.register(FinancialStatementLineModel)
admin.site.register(FinancialStatementLineSequenceModel)
admin.site.register(FinancialStatementFactModel)
admin.site.register(FinancialStatementBalLinkModel)
admin.site.register(FinancialStatementIncLinkModel)
admin.site.register(FinancialStatementInvAcctLinkModel)

# admin.site.register(Programmer)
# admin.site.register(Language)
admin.site.register(ShareholderModel)


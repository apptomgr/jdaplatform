from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class StockDailyValuesModel(models.Model):
    ticker = models.CharField(max_length=100, blank=False, null=False)
    daily_value = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    target_value = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    entry_date = models.DateField(auto_now_add=True, blank=False, null=False)

    def __str__(self):
        return f"{self.ticker}"

    class Meta:
        verbose_name_plural = 'StockDailyValuesModel'
        unique_together = [['ticker', 'entry_date']]


#///////////////////////////////BondModel/////////////////////////////////
class BondModel(models.Model):
    symbol = models.CharField(max_length=100, blank=False, null=False)
    bond_name = models.CharField(max_length=100, blank=False, null=False)
    original_value = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    coupon = models.DecimalField(default=0.0000, max_digits=18, decimal_places=4, blank=False, null=False)
    current_value = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    nbr_of_shares = models.IntegerField(blank=True, null=True)
    total_value = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    institution_type = models.CharField(max_length=100, blank=False, null=False)
    #institution_type_id = models.ForeignKey(InstitutionTypeModel, on_delete=models.CASCADE, related_name='bonds')
    entry_date = models.DateField(auto_now_add=True, blank=False, null=False)

    def __str__(self):
        return f"{self.symbol}"

    class Meta:
        verbose_name_plural = 'BondModel'
        unique_together = [['symbol', 'entry_date']]


#////////////////////////////////////////////InstitutionTypeModel////////////////////////////////
class InstitutionTypeModel(models.Model):
    inst_type = models.CharField(max_length=200)

    def __str__(self):
        return self.inst_type


#///////////////////////////////MutualFundModel/////////////////////////////////
class MutualFundModel(models.Model):
    sociate_de_gession = models.CharField(max_length=100, blank=False, null=False)
    depositaire = models.CharField(max_length=100, blank=True, null=True)
    opcvm = models.CharField(max_length=100, blank=False, null=False)
    original_value = models.DecimalField(default=0.00, max_digits=18, decimal_places=4, blank=True, null=True)
    current_value = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    nbr_of_share = models.IntegerField(blank=True, null=True)
    total_current_value = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    entry_date = models.DateField(auto_now_add=True, blank=False, null=False)

    def __str__(self):
        return self.opcvm

    class Meta:
        verbose_name_plural = 'MutualFundModel'
        unique_together = [['opcvm', 'entry_date']]

#///////////////////////////////ClientProfileModel/////////////////////////////////
class ClientProfileModel(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)  # client
    liquid_assets = models.DecimalField(default=0.00, max_digits=18, decimal_places=4, blank=False, null=False)
    equity_and_rights = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=False, null=False)
    bonds = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=False, null=False)
    mutual_funds = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=False, null=False)
    profile_type = models.CharField(default='custom', max_length=50, blank=False, null=False)
    entry_date = models.DateField(auto_now_add=True, blank=False, null=False)

    def __str__(self):
        return f"Client {self.client} as of {self.entry_date}"

    def clean(self):
        total = float(self.liquid_assets or 0) + float(self.equity_and_rights or 0) + float(self.bonds or 0) + float(self.mutual_funds or 0)

        # Allow a small epsilon for floating-point tolerance
        if not 99.99 <= total <= 100.01:
            raise ValidationError("The sum of all asset percentages must be exactly 100%.")

        if total != 100:
            raise ValidationError("The sum of asset allocations must be exactly 100%.")

    class Meta:
        verbose_name_plural = 'ClientProfileModel'

#///////////////////////////////TransactionFeesModel/////////////////////////////////
class TransactionFeesModel(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    commission_sgi = models.DecimalField(default=0.00, max_digits=18, decimal_places=2)
    tps = models.DecimalField(default=0.00, max_digits=18, decimal_places=2)
    country_sgi = models.DecimalField(default=0.00, max_digits=18, decimal_places=2)
    commission_brvm = models.DecimalField(default=0.00, max_digits=18, decimal_places=2)
    commission_dc_br = models.DecimalField(default=0.00, max_digits=18, decimal_places=2)
    total_commission = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    actual_loss = models.DecimalField(default=0.00, max_digits=18, decimal_places=2)
    potential_loss =models.DecimalField(default=0.00, max_digits=18, decimal_places=2)
    entry_date = models.DateField(auto_now_add=True)


    def __str__(self):
        return f"Client {self.client} as of {self.entry_date}"


#////////////////////////////////////////////SociateDeGessionModel////////////////////////////////
class SociateDeGessionModel(models.Model):
    sociate_de_gession = models.CharField(max_length=100, blank=False, null=False)

    def __str__(self):
        return self.sociate_de_gession


#////////////////////////////////////////////DepositaireModel////////////////////////////////
class DepositaireModel(models.Model):
    depositaire = models.CharField(max_length=100, blank=False, null=False)
    #depositaire = models.ForeignKey(MutualFundModel, related_name="depositaires", on_delete=models.CASCADE)
    def __str__(self):
        return self.depositaire

#////////////////////////////////////////////ClientPortfolioModel////////////////////////////////
class ClientPortfolioModel(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)  # client
    liquid_assets = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    equity_and_rights = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    bonds = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    mutual_funds = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    entry_date = models.DateField(auto_now_add=True, blank=False, null=False)

    def __str__(self):
        return f"Client {self.client}: Liquid Assets: {self.liquid_assets}, Equity & Rights: {self.equity_and_rights}, Bond: {self.bonds}, Mutual Funds: {self.mutual_funds}"

    class Meta:
        verbose_name_plural = 'ClientPortfolioModel'
        #unique_together = [['ticker', 'entry_date']]


#////////////////////////////////////////////ClientEquityAndRightsModel////////////////////////////////
class ClientEquityAndRightsModel(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    stocks = models.ForeignKey(StockDailyValuesModel, related_name='stocks', on_delete=models.CASCADE, blank=True, null=True)
    nbr_of_stocks = models.IntegerField(blank=True, null=True)
    avg_weighted_cost = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    daily_value = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    total_current_value = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    total_purchase_value = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    total_gain_or_loss = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)

    def __str__(self):
         return f"Client {self.client} - Stock: {self.stocks} - Avg Weighted Cost: {self.avg_weighted_cost} - Daily Value: {self.daily_value}"

    class Meta:
         verbose_name_plural = 'ClientEquityAndRightsModel'
         #unique_together = [['ticker', 'entry_date']]


#////////////////////////////////////////////ClientBondsModel////////////////////////////////
class ClientBondsModel(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    institution_type = models.ForeignKey(InstitutionTypeModel, related_name='institution_types', on_delete=models.CASCADE, blank=True, null=True)
    symbol = models.ForeignKey(BondModel, related_name='symbols', on_delete=models.CASCADE, blank=True, null=True)
    bond_name = models.ForeignKey(BondModel, related_name='bond_names', on_delete=models.CASCADE, blank=True, null=True)
    nbr_of_shares = models.IntegerField(blank=True, null=True)
    coupon = models.DecimalField(default=0.00, max_digits=18, decimal_places=4, blank=False, null=False)
    original_value = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    current_value = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    total_current_value = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    total_purchase_value = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    total_gain_or_loss = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Client {self.client} - Symbol: {self.symbol}"

    class Meta:
        verbose_name_plural = 'ClientBondsModel'
        #unique_together = [['ticker', 'entry_date']]


#////////////////////////////////////////////ClientMutualFundsModel////////////////////////////////
class ClientMutualFundsModel(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    sociate_de_gession = models.ForeignKey(SociateDeGessionModel, related_name='sociate_de_gessions', on_delete=models.CASCADE, blank=True, null=True)
    depositaire = models.ForeignKey(DepositaireModel, related_name='depositaires', on_delete=models.CASCADE, blank=True, null=True)
    opcvm = models.ForeignKey(MutualFundModel, related_name='opcvms', on_delete=models.CASCADE, blank=True, null=True)
    mu_original_value = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    mu_current_value = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    mu_nbr_of_share = models.IntegerField(blank=True, null=True)
    mu_total_current_value = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    mu_total_purchase_value = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    mu_total_gain_or_loss = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    entry_date = models.DateField(auto_now_add=True, blank=False, null=False)


    def __str__(self):
        return f"Client {self.client} - opcvm: {self.opcvm}"

    class Meta:
        verbose_name_plural = 'ClientMutualFundsModel'
        #unique_together = [['ticker', 'entry_date']]


#////////////////////////////////////////////SimHeldSecuritiesModel////////////////////////////////
class SimHeldSecuritiesModel(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)

    stock = models.CharField(max_length=100, blank=False, null=False)
    nbr_of_stocks = models.IntegerField(blank=False, null=False)
    avg_weighted_cost = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    mkt_price = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    gain_or_loss = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    target_price = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    potential_gain_or_loss = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    selling_price = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)

    decision = models.CharField(max_length=10, blank=False, null=False)
    sale_amount = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    entry_date = models.DateField(auto_now_add=True, blank=False, null=False)


    def __str__(self):
        return f"Client {self.client} - Security {self.stock} as of {self.entry_date}"

    class Meta:
        verbose_name_plural = 'SimHeldSecuritiesModel'
        #unique_together = [['ticker', 'entry_date']]

#//////////////////////////prototype below this line //////////////////////////
class Daily_stock(models.Model):
    stock = models.CharField(max_length=100)
    daily_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.stock

class Client_portfolio(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Daily_stock, on_delete=models.CASCADE)
    number_of_stocks = models.PositiveIntegerField()
    total_value = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f'{self.client.username} - {self.stock.stock}'


#/////////////////////ValidatorModel/////////////////
class ValidatorModel(models.Model):
    entry_date = models.DateField(unique=True)
    anomalies = models.TextField(blank=True)
    missing_data = models.TextField(blank=True)
    insights = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-entry_date']

    def __str__(self):
        return f"Validation Report for {self.entry_date}"
#/////////  for testing purposes ////////
class Option(models.Model):
    name = models.CharField(max_length=100)




class Country(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Countries'

class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='cities')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Cities'


class CountryCityModel(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.country} - {self.city}"

    class Meta:
        verbose_name_plural = 'CountryCityModel'


class ResModel(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.country} "

    class Meta:
        verbose_name_plural = 'ResModel'
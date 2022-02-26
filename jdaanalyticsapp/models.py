from django.db import models
from django_countries.fields import CountryField
from jdafinancialsapp.models import CompanyModel, SectorModel


# ///////////////////////////// ExchangeModel ///////////////////////////////
class ExchangeModel(models.Model):
    name = models. CharField(max_length=25, null=False, blank=False)
    acronym = models. CharField(max_length=10, null=False, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'ExchangeModel'


# /////////////////////////////// IndexModel//////////////////////////////////////////////
class IndexModel(models.Model):
    idx = models.CharField(max_length=12, blank=False, null=False)

    def __str__(self):
        return self.idx

    class Meta:
        verbose_name_plural = 'IndexModel'


# //////////////////////////////// IndexPriceModel//////////////////////////////////////////////
class IndexPriceModel(models.Model):
    index_date = models.DateTimeField(blank=False, null=False)
    idx = models.ForeignKey(IndexModel, on_delete=models.CASCADE, null=False, blank=False)
    value = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    res = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.idx.idx} - {self.value}"

    class Meta:
        verbose_name_plural = 'IndexPriceModel'


# /////////////////////////////// SecurityModel//////////////////////////////////////////////
class SecurityModel(models.Model):
    # ticker = models.CharField(max_length=12, blank=False, null=False)
    # isin = models.CharField(max_length=20, blank=False, null=False)
    # name = models.CharField(max_length=200, blank=True, null=True)
    #
    # def __str__(self):
    #     return f"{self.ticker} - {self.name}"
    #
    # class Meta:
    #     verbose_name_plural = 'SecurityModel'

    CHOICES_INSTR_TYPE = (
        ('', 'Security Status'),
        ('Listed', 'Listed'),
        ('Unquoted', 'Unquoted'),
        ('Suspended', 'Suspended'),
    )
    CHOICES_LISTG = (
        ('', 'Listing Status'),
        ('Listed', 'Listed'),
        ('Unlisted', 'Unlisted'),
        ('Suspended', 'Suspended'),
        ('Deleted', 'Deleted'),
    )
    CHOICES_TITLE_TYPE = (
        ('', 'Title Type'),
        ('Listed Share', 'Listed Share'),
        ('Listed Bond', 'Listed Bond'),
        ('Unlisted Share', 'Unlisted Share'),
        ('Unlisted Bond', 'Unlisted Bond'),
    )
    CHOICES_SHR_CLASS = (
        ('', 'Share Class'),
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
    )
    CHOICES_ISUR_TYPE = (
        ('', 'Issuer Type'),
        ('Private', 'Private'),
        ('Public', 'Public'),
    )
    CHOICES_RGSTRR = (
        ('', 'Registrar'),
        ('Central Bank', 'Central Bank'),
    )
    CHOICES_DEPSTY = (
        ('', 'Depository'),
        ('Bourse Regionale', 'Bourse Regionale'),
    )

    ticker = models.CharField(max_length=12, blank=False, null=False)
    isin = models.CharField(max_length=20, blank=False, null=False)
    name = models.CharField(max_length=200, blank=True, null=True)
    instr_type = models.CharField(max_length=20, blank=True, null=True, choices=CHOICES_INSTR_TYPE)
    isu_dt = models.DateTimeField(blank=True, null=True)
    open_dt = models.DateTimeField(blank=True, null=True)
    close_dt = models.DateTimeField(blank=True, null=True)
    desc = models.CharField(max_length=50, blank=True, null=True)
    listg_sts = models.CharField(max_length=20, blank=True, null=True, choices=CHOICES_LISTG)
    nmnl_amt = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=20, blank=True, null=True)
    min_lot = models.IntegerField(blank=True, null=True)
    ttl_type = models.CharField(max_length=20, blank=True, null=True, choices=CHOICES_TITLE_TYPE)
    shr_class = models.CharField(max_length=20, blank=True, null=True, choices=CHOICES_SHR_CLASS)
    isur_type = models.CharField(max_length=20, blank=True, null=True, choices=CHOICES_ISUR_TYPE)
    sector = models.ForeignKey(SectorModel, on_delete=models.CASCADE, null=True, blank=True)
    issue = models.ForeignKey(CompanyModel, on_delete=models.CASCADE, null=True, blank=True)
    cntry = CountryField(blank=True, null=True, unique=True)
    rgstrr = models.CharField(max_length=20, blank=True, null=True, choices=CHOICES_RGSTRR)
    exchg = models.ForeignKey(ExchangeModel, on_delete=models.CASCADE, null=True, blank=True)
    depsty = models.CharField(max_length=100, blank=True, null=True, choices=CHOICES_DEPSTY)
    cntry_tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    invstr_cntry_tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    txtn_code = models.BooleanField(blank=True, null=True)
    exchg_tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    val_code = models.BooleanField(blank=True, null=True)
    lwst_appl_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    hghst_appl_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.ticker} - {self.name}"

    class Meta:
        verbose_name_plural = 'SecurityModel'


# /////////////////////////////// SecurityPriceModel//////////////////////////////////////////////
class SecurityPriceModel(models.Model):
    security = models.ForeignKey(SecurityModel, on_delete=models.CASCADE, null=False, blank=False)
    security_date = models.DateTimeField(blank=False, null=False)
    avg_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    open = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    close = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    high = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    low = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ask = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bid = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    trans_total = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    volume = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    trans_value = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.security.ticker

    class Meta:
        verbose_name_plural = 'SecurityPriceModel'


# ///////////////////////////// StockModel ///////////////////////////////
class StockModel(models.Model):
    CHOICES_SECR_STS = (
        ('', 'Security Status'),
        ('Listed', 'Listed'),
        ('Unquoted', 'Unquoted'),
        ('Suspended', 'Suspended'),
    )
    security = models.ForeignKey(SecurityModel, on_delete=models.CASCADE, null=False, blank=False)
    stock_type = models. CharField(max_length=25, null=False, blank=False)
    under_stock_type = models. CharField(max_length=25, null=False, blank=False)
    secr_status = models.CharField(max_length=30, choices=CHOICES_SECR_STS)
    dvdnd = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.security.ticker

    class Meta:
        verbose_name_plural = 'StockModel'


# ///////////////////////////// BondModel ///////////////////////////////
class BondModel(models.Model):
    CHOICES_BND_TYPE = (
        ('', 'Bond Type'),
        ('Redeemable in Share', 'Redeemable in Share'),
        ('Constant Redemption Bond', 'Constant Redemption Bond'),
        ('Deferred Constant Redemption Bond', 'Deferred Constant Redemption Bond'),
        ('In Fine Bond', 'In Fine Bond'),
    )
    CHOICES_DURATN_UNITS = (
        ('', 'Duration Units'),
        ('Monthly', 'Monthyl'),
        ('Quarterly', 'Quarterly'),
        ('Semi-annually', 'Semi-annually'),
        ('Annually', 'Annually'),
    )
    PYMT_PERD = (
        ('', 'Payment Period'),
        ('Monthly', 'Monthyl'),
        ('Quarterly', 'Quarterly'),
        ('Semi-annually', 'Semi-annually'),
        ('Annually', 'Annually'),
    )
    CHOICES_PYMT_PERDU = (
        ('', 'Payment Period Units'),
        ('1', '1'),
        ('5', '5'),
        ('10', '10'),
        ('20', '20'),
        ('30', '30'),
    )
    CHOICES_DRPU = (
        ('', 'Deferred Repayment Period Units'),
        ('0', '1'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
    )
    CHOICES_RPYMT_MTHD = (
        ('', 'Repayment Method'),
        ('Sur Valeur', 'Sur Valeur'),
        ('Sur Valeur', 'Sur Valeur'),
    )
    CHOICES_RPYMT_TYPE = (
        ('', 'Repayment Type'),
        ('Fixed rate', 'Fixed rate'),
        ('Variable rate', 'Variaible'),
    )
    CHOICES_USAGE = (
        ('', 'Usage'),
        ('360', '360'),
        ('365', '365'),
    )
    security = models.ForeignKey(SecurityModel, on_delete=models.CASCADE, null=False, blank=False)
    auth = models.BooleanField()
    security_date = models.DateTimeField(blank=False, null=False)
    gr_bnd_int_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    net_bnd_int_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    bnd_type = models.CharField(max_length=50, choices=CHOICES_BND_TYPE)
    duratn_amt = models.IntegerField(blank=False, null=False)
    duratn_units = models.CharField(max_length=50, choices=CHOICES_DURATN_UNITS)
    pymt_perd = models.CharField(max_length=50, choices=PYMT_PERD)
    pymt_perd_units = models.CharField(max_length=50, choices=CHOICES_PYMT_PERDU)
    dfrrd_rpymt_perd_units = models.CharField(max_length=50, choices=CHOICES_DRPU)
    rpymt_mthd = models.CharField(max_length=50, choices=CHOICES_RPYMT_MTHD)
    rpymt_type = models.CharField(max_length=50, choices=CHOICES_RPYMT_TYPE)
    bnd_isu_dt = models.DateField(auto_now=False)
    first_pay_date = models.DateField(auto_now_add=False)
    lst_pay_dt = models.DateField(auto_now_add=False)
    usage = models.IntegerField(blank=False, null=False, choices=CHOICES_USAGE)

    def __str__(self):
        return self.security.ticker

    class Meta:
        verbose_name_plural = 'BondModel'


# ////////////////// Test models ///////////////////////////////////////////
class Author(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    number_of_pages = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title
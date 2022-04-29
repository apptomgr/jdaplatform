from django.db import models
from django_countries.fields import CountryField
from jdafinancialsapp.models import CompanyModel, SectorModel
from django_countries.fields import CountryField, countries
from  jdafinancialsapp.utils import merge_two_lists, merge_company_lists




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


# ///////////////////////////// ExchangeModel ///////////////////////////////
class ExchangeModel(models.Model):
    #security =models.ForeignKey(SecurityModel, on_delete=models.CASCADE, blank=False, null=True)
    name = models. CharField(max_length=225, null=True, blank=True)
    acronym = models. CharField(max_length=225, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'ExchangeModel'

# /////////////////////////////// SecurityModel//////////////////////////////////////////////
class SecurityModel(models.Model):

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
        ('ABCO BOURSE','ABCO BOURSE'),
        ('AFRICABOURSE','AFRICABOURSE'),
        ('AFRICAINE DE GESTION ET D’INTERMEDIATION (AGI)','AFRICAINE DE GESTION ET D’INTERMEDIATION (AGI)'),
        ('ATLANTIQUE FINANCE','ATLANTIQUE FINANCE'),
        ('ATTIJARI SECURITIES WEST AFRICA (ASWA)','ATTIJARI SECURITIES WEST AFRICA (ASWA)'),
        ('BICI BOURSE','BICI BOURSE'),
        ('BIIC FINANCIAL SERVICES (BFS)','BIIC FINANCIAL SERVICES (BFS)'),
        ('BNI FINANCES SA','BNI FINANCES SA'),
        ('BOA CAPITAL SECURITIES','BOA CAPITAL SECURITIES'),
        ('BRIDGE SECURITIES','BRIDGE SECURITIES'),
        ('BSIC CAPITAL','BSIC CAPITAL'),
        ('CIFA-BOURSE SA','CIFA-BOURSE SA'),
        ('COMPAGNIE DE GESTION FINANCIÈRE ET DE BOURSE (CGF BOURSE)','COMPAGNIE DE GESTION FINANCIÈRE ET DE BOURSE (CGF BOURSE)'),
        ('CORIS BOURSE','CORIS BOURSE'),
        ('ECOBANK INVESTMENT CORPORATION (EIC)','ECOBANK INVESTMENT CORPORATION (EIC)'),
        ('EVEREST FINANCE','EVEREST FINANCE'),
        ('FINANCE GESTION ET INTERMÉDIATION (FGI)','FINANCE GESTION ET INTERMÉDIATION (FGI)'),
        ('GLOBAL CAPITAL','GLOBAL CAPITAL'),
        ('HUDSON & CIE','HUDSON & CIE'),
        ('IMPAXIS SECURITIES','IMPAXIS SECURITIES'),
        ('INVICTUS CAPITAL FINANCE','INVICTUS CAPITAL FINANCE'),
        ('MAC - AFRICAN SGI','MAC - AFRICAN SGI'),
        ('MATHA SECURITIES','MATHA SECURITIES'),
        ('NSIA FINANCES','NSIA FINANCES'),
        ('SGI BÉNIN SA','SGI BÉNIN SA'),
        ('SGI MALI','SGI MALI'),
        ('SGI NIGER','SGI NIGER'),
        ('SGI TOGO','SGI TOGO'),
        ('SGI-PHOENIX CAPITAL MANAGEMENT (PCM)','SGI-PHOENIX CAPITAL MANAGEMENT (PCM)'),
        ('SIRIUS CAPITAL','SIRIUS CAPITAL'),
        ('SOCIÉTÉ BURKINABÉ D\'INTERMÉDIATION FINANCIÈRE (SBIF)','SOCIÉTÉ BURKINABÉ D\'INTERMÉDIATION FINANCIÈRE (SBIF)'),
        ('SOCIÉTÉ GÉNÉRALE CAPITAL SECURITIES WEST AFRICA (SG – CSWA)','SOCIÉTÉ GÉNÉRALE CAPITAL SECURITIES WEST AFRICA (SG – CSWA)'),
        ('UNITED CAPITAL FOR AFRICA','UNITED CAPITAL FOR AFRICA'),
    )

    CHOICES_DEPSTY = (
        ('', 'Depository'),
        ('BCEAO','BCEAO'),
        ('DC/BR','DC/BR'),
    )

    country_list = []
    country_list_name = []

    for code, name in list(countries):
        country_list_name.append(name)

    country_list = merge_two_lists(country_list_name, country_list_name)
    country_list =  tuple(country_list)

    company = CompanyModel.objects.values_list('company', flat=True).order_by('company')
    company_list = list(company)
    company_list = merge_company_lists(company_list, company_list)

    country_company = tuple(country_list) + tuple(company_list)

    CHOICES_ISSUE_LIST= country_company #CountryField(blank_label='Country') #company # country.union(company).order_by('cntry_name')

    ticker = models.CharField(max_length=12, blank=False, null=False)
    isin = models.CharField(max_length=20, blank=False, null=False)
    name = models.CharField(max_length=200, blank=True, null=True)
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
    issuer = models.CharField(max_length=200, blank=True, null=True, choices=CHOICES_ISSUE_LIST) #models.ForeignKey(CompanyModel, on_delete=models.CASCADE, null=True, blank=True)
    cntry = CountryField(blank=True, null=True, unique=False)
    rgstrr = models.CharField(max_length=200, blank=True, null=True, choices=CHOICES_RGSTRR)
    exchg = models.ForeignKey(ExchangeModel, on_delete=models.CASCADE, null=True, blank=True)
    depsty = models.CharField(max_length=100, blank=True, null=True, choices=CHOICES_DEPSTY)
    cntry_tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    invstr_cntry_tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    txtn_code = models.BooleanField(blank=False, null=False)
    exchg_tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    val_code = models.BooleanField(blank=True, null=True)
    lwst_appl_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    hghst_appl_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.ticker

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
        ('Deleted', 'Deleted'),
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
        ('Redeemable in Shares', 'Redeemable in Shares'),
        ('Constant Redemption Bond', 'Constant Redemption Bond'),
        ('Deferred Constant Redemption Bond', 'Deferred Constant Redemption Bond'),
        ('In Fine Bond', 'In Fine Bond'),
    )
    CHOICES_DURATN_UNITS = (
        ('', 'Duration Units'),
        ('Monthly', 'Monthly'),
        ('Quarterly', 'Quarterly'),
        ('Semi-Annually', 'Semi-Annually'),
        ('Annually', 'Annually'),
    )

    CHOICES_PYMT_PERDU =  (
        ('', 'Payment Period Unit'),
        ('Monthly', 'Monthly'),
        ('Quarterly', 'Quarterly'),
        ('Semi-Annually', 'Semi-Annually'),
        ('Annually', 'Annually'),
    )
    CHOICES_DRPU = (
        ('', 'Deferred Repayment Period Units'),
        ('Monthly', 'Monthly'),
        ('Quarterly', 'Quarterly'),
        ('Semi-Annually', 'Semi-Annually'),
        ('Annually', 'Annually'),
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
        (360, 360),
        (365, 365),
    )
    security = models.ForeignKey(SecurityModel, on_delete=models.CASCADE, null=False, blank=False)
    auth = models.BooleanField()
    #security_date = models.DateTimeField(blank=False, null=False)
    gr_bnd_int_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    net_bnd_int_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    nbr_shrs_outstg = models.IntegerField(blank=True, null=True)
    bnd_type = models.CharField(max_length=50, choices=CHOICES_BND_TYPE)
    duratn_amt = models.IntegerField(blank=False, null=False)
    duratn_units = models.CharField(max_length=50, choices=CHOICES_DURATN_UNITS)
    pymt_perd = models.IntegerField() #max_length=50, choices=PYMT_PERD)
    pymt_perd_units = models.CharField(max_length=50, choices=CHOICES_PYMT_PERDU)
    dfrrd_rpymt_perd = models.IntegerField(blank=True, null=True)
    dfrrd_rpymt_perd_units = models.CharField(max_length=50, choices=CHOICES_DRPU)
    rpymt_mthd = models.CharField(max_length=50, choices=CHOICES_RPYMT_MTHD)
    rpymt_type = models.CharField(max_length=50, choices=CHOICES_RPYMT_TYPE)
    bnd_isu_dt = models.DateField(auto_now=False)
    first_pay_dt = models.DateField(auto_now_add=False)
    lst_pay_dt = models.DateField(auto_now_add=False)
    usage = models.IntegerField(blank=False, null=False, choices=CHOICES_USAGE)

    def __str__(self):
        return self.security.ticker

    class Meta:
        verbose_name_plural = 'BondModel'

# ///////////////////////// GuarantorModel ///////////////////////////////////////////
class GuarantorModel(models.Model):
    security =models.ForeignKey(SecurityModel, on_delete=models.CASCADE, blank=False, null=True)
    guarantor = models.CharField(max_length=25, blank=True, null=True)
    guarantor_pctg = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    guarantor_val = models.DecimalField(max_digits=100, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.guarantor

    class Meta:
        verbose_name_plural = 'GuarantorModel'





# ////////////////// Test models ///////////////////////////////////////////
# class Author(models.Model):
#     name = models.CharField(max_length=50)
#
#     def __str__(self):
#         return self.name
#
#
# class Book(models.Model):
#     author = models.ForeignKey(Author, on_delete=models.CASCADE)
#     title = models.CharField(max_length=100)
#     number_of_pages = models.PositiveIntegerField(default=1)
#
#     def __str__(self):
#         return self.title
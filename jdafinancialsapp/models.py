from django.db import models
import datetime
from .utils import get_rpt_range_period, get_period
from django.core.exceptions import ValidationError
from django_countries.fields import CountryField


#///////////////////////////////// SectorModel /////////////////////////////////
class SectorModel(models.Model):
    sector = models.CharField(max_length=50, blank=False, null=False, unique=True)

    def __str__(self):
        return self.sector

    class Meta:
        verbose_name_plural ='SectorModel'


#/////////////////////////////////// ShareholderModel ///////////////////////////////
class ShareholderModel(models.Model):
    #company = models.ForeignKey(CompanyModel, on_delete=models.CASCADE)
    shrhldr_name = models.CharField(max_length=100, blank=True, null=True)
    shrhldr_type = models.CharField(max_length=35, blank=True, null=True)
    shrs_hld     = models.DecimalField(max_digits=13, decimal_places=2, blank=True, null=True)
    #
    # shrhldr_name_2 = models.CharField(max_length=100, blank=True, null=True)
    # shrhldr_type_2 = models.CharField(max_length=35, blank=True, null=True)
    # shrs_hld_2     = models.DecimalField(max_digits=13, decimal_places=2, blank=True, null=True)
    #
    # shrhldr_name_3 = models.CharField(max_length=100, blank=True, null=True)
    # shrhldr_type_3 = models.CharField(max_length=35, blank=True, null=True)
    # shrs_hld_3     = models.DecimalField(max_digits=13, decimal_places=2, blank=True, null=True)
    #
    # shrhldr_name_4 = models.CharField(max_length=100, blank=True, null=True)
    # shrhldr_type_4 = models.CharField(max_length=35, blank=True, null=True)
    # shrs_hld_4     = models.DecimalField(max_digits=13, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.shrhldr_name

    class Meta:
        verbose_name_plural ='ShareholderModel'

#///////////////////////////////// CompanyModel /////////////////////////////////
class CompanyModel(models.Model):
    CHOICES = (
        ('Quarterly', 'Quarterly'),
        ('Semi-annually', 'Semi-Annually'),
        ('Annually', 'Annually'),
    )
    corp_name = models.CharField(max_length=100, blank=True, null=True)
    company = models.CharField(max_length=200, blank=False, null=False, unique=True)
    sector = models.ForeignKey(SectorModel, on_delete=models.CASCADE)
    #rpt_period = models.CharField(max_length=50, choices=CHOICES, blank=True, null=True)
    legl_form = models.CharField(max_length=10, blank=False, null=False)
    creatn_dt = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    rccm_nbr = models.CharField(max_length=15, blank=True, null=True)
    country = CountryField(blank=True, null=True)
    #country =models.CharField(max_length=300, blank=False, null=False)
    #id_cntry = models.IntegerField(blank=False, null=True)
    flag_pub_ctrl = models.BooleanField(default=True)
    actvty_sctr = models.CharField(max_length=30, blank=True, null=True)
    actvty_code = models.CharField(max_length=30, blank=True, null=True)
    intrnl_actvty_code = models.CharField(max_length=30, blank=True, null=True)
    othr_bus_sctr = models.CharField(max_length=30, blank=True, null=True)
    shareholder = models.ForeignKey(ShareholderModel, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.company

    class Meta:
        verbose_name_plural ='CompanyModel'


#///////////////////////////// ExchangeModel ///////////////////////////////
class ExchangeModel(models.Model):
    name = models. CharField(max_length=25, null=False, blank=False)
    acronym = models. CharField(max_length=10, null=False, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'ExchangeModel'


# /////////////////////////////////// FinancialStatementModel ///////////////////////////////
class FinancialStatementModel(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural ='FinancialStatementModel'

class FinancialStatementLineModel(models.Model):
    name = models.CharField(max_length=300)
    flag_input= models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural ='FinancialStatementLineModel'

# /////////////////////////////////// FinancialStatementLineSequenceModel ///////////////////////////////
class FinancialStatementLineSequenceModel(models.Model):
    financial_statement = models.ForeignKey(FinancialStatementModel, on_delete=models.CASCADE)
    financial_statement_line = models.ForeignKey(FinancialStatementLineModel, on_delete=models.CASCADE)
    sequence = models.IntegerField(null=False)

    def __str__(self):
        return f"{self.sequence} - {self.financial_statement_line}"

    class Meta:
        unique_together = ('financial_statement', 'financial_statement_line', 'sequence')

    class Meta:
        verbose_name_plural ='FinancialStatementLineSequenceModel'


# /////////////////////////////////// FinancialStatementFactModel ///////////////////////////////////////
class FinancialStatementFactModel(models.Model):
    company = models.ForeignKey(CompanyModel, on_delete=models.CASCADE, null=False, blank=False)
    financial_statement_line = models.ForeignKey(FinancialStatementLineModel, on_delete=models.CASCADE, null=False, blank=False)
    entry_date= models.DateField(auto_now=False, auto_now_add=False, blank=False, null=False)
    brut = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)


    def __str__(self):
        return f"{self.company.company}  - {self.financial_statement_line} - {self.entry_date}"

    class Meta:
        verbose_name_plural ='FinancialStatementFactModel'
        unique_together = ("company", "entry_date", "financial_statement_line")


# /////////////////////////////////// FinancialStatementBalLinkModel ///////////////////////////////////////
class FinancialStatementBalLinkModel(models.Model):
    company = models.ForeignKey(CompanyModel, on_delete=models.CASCADE, null=False, blank=False)
    entry_date  = models.DateField(auto_now=False, auto_now_add=False, blank=False, null=False)

    brut_0 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_1  = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_2  = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_3 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_4 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_5 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_6 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_7 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_8 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_9 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_10 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_11 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_12 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_13 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_14 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_15 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_16 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_17 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_18 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_19 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_20 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_21 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_22 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_23 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_24 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_25 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_26 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_27 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_28 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_29 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_30 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_31 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_32 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_33 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_34 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_35 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_36 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_37 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_38 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_39 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_40 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_41 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_42 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_43 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_44 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_45 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_46 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_47 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_48 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_49 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_50 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_51 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_52 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_53 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_54 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_55 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_56 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_57 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_58 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_59 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)

    amort_0 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_1 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_2 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_3 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_4 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_5 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_6 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_7 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_8 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_9 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_10 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_11 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_12 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_13 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_14 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_15 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_16 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_17 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_18 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_19 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_20 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_21 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_22 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_23 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_24 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_25 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_26 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_27 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_28 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_29 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_30 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_31 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_32 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_33 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_34 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_35 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_36 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_37 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_38 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_39 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_40 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_41 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_42 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_43 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_44 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_45 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_46 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_47 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_48 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_49 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_50 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_51 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_52 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_53 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_54 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_55 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_56 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_57 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_58 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_59 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)

    net_0 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_1   = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_2   = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_3 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_4 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_5 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_6 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_7 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_8 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_9 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_10 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_11 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_12 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_13 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_14 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_15 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_16 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_17 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_18 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_19 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_20 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_21 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_22 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_23 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_24 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_25 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_26 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_27 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_28 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_29 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_30 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_31 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_32 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_33 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_34 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_35 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_36 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_37 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_38 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_39 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_40 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_41 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_42 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_43 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_44 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_45 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_46 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_47 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_48 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_49 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_50 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_51 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_52 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_53 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_54 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_55 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_56 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_57 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_58 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_59 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)


    def __str__(self):
        return f"{self.company}  - {self.entry_date}"

    class Meta:
        verbose_name_plural ='FinancialStatementBalLinkModel'


# ///////////////////////////////////// FinancialStatementIncLinkModel ////////////////////////////////
class FinancialStatementIncLinkModel(models.Model):
    company = models.ForeignKey(CompanyModel, on_delete=models.CASCADE, null=False, blank=False)
    entry_date  = models.DateField(auto_now=False, auto_now_add=False, blank=False, null=False)
    brut_0 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_1  = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_2  = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_3 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_4 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_5 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_6 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_7 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_8 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_9 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_10 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_11 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_12 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_13 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_14 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_15 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_16 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_17 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_18 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_19 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_20 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_21 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_22 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_23 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_24 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_25 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_26 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_27 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_28 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_29 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_30 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_31 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_32 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_33 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_34 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_35 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_36 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_37 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_38 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_39 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_40 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_41 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_42 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)


    def __str__(self):
        return f"{self.company}  - {self.entry_date}"

    class Meta:
        verbose_name_plural ='FinancialStatementIncLinkModel'


#///////////////////////////////////// FinancialStatementIncLinkModel ////////////////////////////////
class FinancialStatementInvAcctLinkModel(models.Model):
    company = models.ForeignKey(CompanyModel, on_delete=models.CASCADE, null=False, blank=False)
    entry_date  = models.DateField(auto_now=False, auto_now_add=False, blank=False, null=False)
    brut_0 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_1  = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_2  = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_3 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_4 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_5 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_6 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)

    amort_0 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_1  = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_2  = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_3 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_4 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_5 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_6 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.company}  - {self.entry_date}"

    class Meta:
        verbose_name_plural ='FinancialStatementInvAcctLinkModel'








# class Programmer(models.Model):
#     name = models.CharField(max_length=100)
#
#     def __str__(self):
#         return self.name
#
#
# class Language(models.Model):
#     name = models.CharField(max_length=100)
#     programmer = models.ForeignKey(Programmer, on_delete=models.CASCADE)
#
#     def __str__(self):
#         return self.name


# """
# select *
# from Company c, FinancialStatementFact fsf, FinancialStatementLine fsl, FinancialStatementLineSequence fsls, FinancialStatement fs
# where c.id=fsf.company_id                   [Company - Fact]
# and fsf.financial_statement_line_id=fsl.id  [fact - line ]
# and fsl.id=fsls.financial_statement_line_id [line - seq]
# and fsls.financial_statement_id=fs.id [seq - stmt];
# """





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

#///////////////////////////////// CompanyModel /////////////////////////////////
class CompanyModel(models.Model):
    CHOICES = (
        ('Quarterly', 'Quarterly'),
        ('Semi-annually', 'Semi-Annually'),
        ('Annually', 'Annually'),
    )
    corp_name = models.CharField(max_length=100, blank=False, null=False)
    company = models.CharField(max_length=200, blank=False, null=False, unique=True)
    sector = models.ForeignKey(SectorModel, on_delete=models.CASCADE, blank=True, null=True)
    #rpt_period = models.CharField(max_length=50, choices=CHOICES, blank=True, null=True)
    legl_form = models.CharField(max_length=100, blank=True, null=True)
    creatn_dt = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    rccm_nbr = models.CharField(max_length=50, blank=True, null=True)
    country = CountryField(blank=True, null=True)
    #country =models.CharField(max_length=300, blank=False, null=False)
    #id_cntry = models.IntegerField(blank=False, null=True)
    flag_pub_ctrl = models.BooleanField(default=True)
    actvty_sctr = models.CharField(max_length=50, blank=True, null=True)
    actvty_code = models.CharField(max_length=50, blank=True, null=True)
    intrnl_actvty_code = models.CharField(max_length=50, blank=True, null=True)
    othr_bus_sctr = models.CharField(max_length=50, blank=True, null=True)
    #shareholder = models.ForeignKey(ShareholderModel, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.company

    class Meta:
        verbose_name_plural ='CompanyModel'

#/////////////////////////////////// ShareholderModel ///////////////////////////////
class ShareholderModel(models.Model):
    company = models.ForeignKey(CompanyModel, related_name='shareholders', on_delete=models.CASCADE, blank=True, null=True)
    shrhldr_name = models.CharField(max_length=100, blank=True, null=True)
    shrhldr_type = models.CharField(max_length=100, blank=True, null=True)
    shrs_hld     = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.shrhldr_name

    class Meta:
        verbose_name_plural ='ShareholderModel'
        db_table = 'ShareholderModel'


#/////////////////////////////////// AddressModel ///////////////////////////////
class AddressModel(models.Model):
    company = models.ForeignKey(CompanyModel, related_name='addresses', on_delete=models.CASCADE, blank=True, null=True)
    addr = models.CharField(max_length=250, blank=True, null=True)
    phone_nbr =  models.CharField(max_length=30, blank=True, null=True)
    fax_nbr = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(max_length=240, blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.addr

    class Meta:
        verbose_name_plural ='AddressModel'
        db_table = 'AddressModel'

#/////////////////////////////////// LeadersModel ///////////////////////////////
class LeadersModel(models.Model):
    company = models.ForeignKey(CompanyModel, related_name='leaders', on_delete=models.CASCADE, blank=True, null=True)
    lst_name = models.CharField(max_length=100, blank=False, null=False)
    func =  models.CharField(max_length=50, blank=True, null=True)
    phone_nbr = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(max_length=240, blank=True, null=True)

    def __str__(self):
        return self.lst_name

    class Meta:
        verbose_name_plural ='LeadersModel'
        db_table = 'LeadersModel'

#/////////////////////////////////// ParentCompanyModel ///////////////////////////////
class ParentCompanyModel(models.Model):
    company = models.ForeignKey(CompanyModel, related_name='parentcompany', on_delete=models.CASCADE, blank=True, null=True)
    legl_name = models.CharField(max_length=200, blank=False, null=False)
    comm_name =  models.CharField(max_length=200, blank=True, null=True)
    cntry = CountryField(blank=True, null=True)

    def __str__(self):
        return self.legl_name

    class Meta:
        verbose_name_plural ='ParentCompanyModel'
        db_table = 'ParentCompanyModel'

#/////////////////////////////////// SubsidiaryModel ///////////////////////////////
class SubsidiaryModel(models.Model):
    company = models.ForeignKey(CompanyModel, related_name='subsidaries', on_delete=models.CASCADE, blank=True, null=True)
    company_name = models.CharField(max_length=200, blank=False, null=False)
    share_amt =  models.IntegerField(blank=True, null=True)
    url = models.URLField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name_plural ='SubsidiaryModel'
        db_table = 'SubsidiaryModel'


#/////////////////////////////////// CountryModel ///////////////////////////////
class CountryModel(models.Model):
    country = CountryField(blank=True, null=True, unique=True)
    crncy = models.CharField(max_length=3, blank=True, null=True)
    prsdnt_name = models.CharField(max_length=200, blank=True, null=True)
    area = models.CharField(max_length=100, blank=True, null=True) # models.IntegerField(blank=True, null=True)
    ofcl_lang = models.CharField(max_length=60, blank=False, null=False)
    continent = models.CharField(max_length=30, blank=True, null=True)
    capl_city = models.CharField(max_length=120, blank=False, null=False)
    ph_code = models.CharField(max_length=20, blank=False, null=False)

    def __str__(self):
        return self.country.name

    class Meta:
        verbose_name_plural ='CountryModel'
        db_table = 'CountryModel'

#/////////////////////////////////// EconomicDataModel ///////////////////////////////
class EconomicDataModel(models.Model):
    country = models.ForeignKey(CountryModel, related_name='econs', on_delete=models.CASCADE, blank=True, null=True)
    yr = models.IntegerField(blank=True, null=True)
    popltn = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    popltn_grth_rate = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    actv_popltn = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    lf_exprn = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    unemplmt_rate = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    poverty_rate = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    rnkg_bus = models.IntegerField(blank=True, null=True)
    hsehold_cnsmptn = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    idh = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    yr_gdp = models.IntegerField(blank=True, null=True)
    gdp_amt	= models.IntegerField(blank=True, null=True)
    gdp_rate = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    gdp_prim_sctr = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    gdp_secy_sctr = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    gdp_tertry_sctr = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    gr_ntnl_prodt = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    mrgnl_lndg_rate = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    fixd_capl_invstmt = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    ide = models.IntegerField(blank=True, null=True)
    yr_dbt = models.IntegerField(blank=True, null=True)
    infltn_rate = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    pub_dbt = models.IntegerField(blank=True, null=True)
    forgn_dbt = models.IntegerField(blank=True, null=True)
    dmstc_dbt = models.IntegerField(blank=True, null=True)
    trd_bal = models.IntegerField(blank=True, null=True)
    exp_amt = models.IntegerField(blank=True, null=True)
    imp_amt = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.country}"

    class Meta:
        verbose_name_plural ='EconomicDataModel'
        db_table = 'EconomicDataModel'

#/////////////////////////////////// ElectionModel ///////////////////////////////
class ElectionModel(models.Model):
    country = models.ForeignKey(CountryModel, related_name='elections', on_delete=models.CASCADE, blank=True, null=True)
    elecn_dt = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    elecn_type = models.CharField(max_length=15, blank=True, null=True)
    cmnts = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return f"{self.country} election type {self.elecn_type}"

    class Meta:
        verbose_name_plural ='ElectionModel'
        db_table = 'ElectionModel'

#/////////////////////////////////// EconomicZoneModel ///////////////////////////////
class EconomicZoneModel(models.Model):
    country = models.ForeignKey(CountryModel, related_name='econ_zones', on_delete=models.CASCADE, blank=True, null=True)
    econ_zone = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.econ_zone

    class Meta:
        verbose_name_plural ='EconomicZoneModel'
        db_table = 'EconomicZoneModel'
        unique_together = [['country', 'econ_zone']]


#/////////////////////////////////// OtherIndicatorsModel ///////////////////////////////
class OtherIndicatorsModel(models.Model):
    country = models.ForeignKey(CountryModel, related_name='other_indicators', on_delete=models.CASCADE, blank=True, null=True)
    yr = models.IntegerField(blank=True, null=True)
    ind_name = models.CharField(max_length=35, blank=True, null=True)
    ind_val = models.IntegerField(default=0, blank=True, null=True)
    cmnts = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.ind_name

    class Meta:
        verbose_name_plural ='OtherIndicatorsModel'
        db_table = 'OtherIndicatorsModel'


#/////////////////////////////////// TradePartnersModel ///////////////////////////////
class TradePartnersModel(models.Model):
    country = models.ForeignKey(CountryModel, related_name='business_partners', on_delete=models.CASCADE, blank=True, null=True)
    yr = models.IntegerField(blank=True, null=True)
    exp_cntry = CountryField(blank=True, null=True)
    exp_amt = models.IntegerField(blank=True, null=True)
    exp_rate = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    exp_prodt_name = models.CharField(max_length=150, blank=True, null=True)
    imp_cntry = CountryField(blank=True, null=True)
    imp_amt = models.IntegerField(blank=True, null=True)
    imp_rate = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    imp_prodt_name = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f'Trading Partners: Export country: {self.exp_cntry.name} - Import country {self.imp_cntry.name}'

    class Meta:
        verbose_name_plural ='TradePartnersModel'
        db_table = 'TradePartnersModel'

#/////////////////////////////////// EnergyModel ///////////////////////////////
class EnergyModel(models.Model):
    country = models.ForeignKey(CountryModel, related_name='energies', on_delete=models.CASCADE, blank=True, null=True)
    energy_yr = models.IntegerField(blank=True, null=True)
    elec_hydro_dam_nbr = models.IntegerField(blank=True, null=True)
    elec_pwr_sttn_nbr = models.IntegerField(blank=True, null=True)
    elec_otr_nbr = models.IntegerField(blank=True, null=True)
    crude_prodtn_amt = models.IntegerField(blank=True, null=True)
    crude_exp_amt = models.IntegerField(blank=True, null=True)
    crude_imp_amt = models.IntegerField(blank=True, null=True)
    crude_rsrvs_amt=models.IntegerField(blank=True, null=True)
    refined_prodtn_amt=models.IntegerField(blank=True, null=True)
    refined_cnsmptn_amt=models.IntegerField(blank=True, null=True)
    refined_exp_amt=models.IntegerField(blank=True, null=True)
    refined_imp_amt=models.IntegerField(blank=True, null=True)
    gas_prodtn_amt=models.IntegerField(blank=True, null=True)
    gas_exp_amt=models.IntegerField(blank=True, null=True)
    gas_imp_amt=models.IntegerField(blank=True, null=True)
    gas_rsrv_amt=models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f'Trading Partners: Export country: {self.country.name} - Year: {self.energy_yr}'

    class Meta:
        verbose_name_plural ='EnergyModel'
        db_table = 'EnergyModel'

# #/////////////////////////////////// ImportExportModel ///////////////////////////////
# class ImportExportModel(models.Model):
#     country = models.ForeignKey(CountryModel, related_name='import_export', on_delete=models.CASCADE, blank=True, null=True)
#     yr = models.IntegerField(blank=True, null=True)
#     prodt_name = models.CharField(max_length=35, blank=True, null=True)
#     ind_val = models.IntegerField(blank=True, null=True)
#     cmnts = models.CharField(max_length=250, blank=True, null=True)
#
#     def __str__(self):
#         return self.ind_name
#
#     class Meta:
#         verbose_name_plural ='ImportExportModel'
#         db_table = 'ImportExportModel'
# #/////////////////////////////////// GdpModel ///////////////////////////////
# class GdpModel(models.Model):
#     country = models.ForeignKey(CountryModel, related_name='econs', on_delete=models.CASCADE, blank=True, null=True)
#     yr = models.IntegerField(blank=True, null=True)
#     popltn = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
#     popltn_grth_rate = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
#     actv_popltn = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
#     lf_exprn = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
#     unemplmt_rate = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
#     poverty_rate = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
#     rnkg_bus = models.IntegerField(default=0.00, blank=True, null=True)
#     hsehold_cnsmptn = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
#     idh = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
#
#     def __str__(self):
#         return f"{self.country}"
#
#     class Meta:
#         verbose_name_plural ='EconomicDataModel'
#         db_table = 'EconomicDataModel'
# PIB en montant	gdp_amt	IntegerField		TRUE	TRUE	gdp_amt=models.IntegerField(blank=TRUE, null=TRUE)
# Croissance du PIB	gdp_rate	DecimalField		TRUE	TRUE	gdp_rate=models.DecimalField(decimal_places=2)
# PIB-Secteur primaire	gdp_prim_sctr	DecimalField		TRUE	TRUE	gdp_prim_sctr=models.DecimalField(decimal_places=2)
# PIB-Secteur secondaire	gdp_secy_sctr	DecimalField		TRUE	TRUE	gdp_secy_sctr=models.DecimalField(decimal_places=2)
# PIB-Secteur tertiaire	gdp_tertry_sctr	DecimalField		TRUE	TRUE	gdp_tertry_sctr=models.DecimalField(decimal_places=2)
# Produit National Brut	gr_ntnl_prodt	DecimalField		TRUE	TRUE	gr_ntnl_prodt=models.DecimalField(decimal_places=2)
# Taux de pret marginal	mrgnl_lndg_rate	DecimalField		TRUE	TRUE	mrgnl_lndg_rate=models.DecimalField(decimal_places=2)
# Investissement en capital fixe	fixd_capl_invstmt	DecimalField		TRUE	TRUE	fixd_capl_invstmt=models.DecimalField(decimal_places=2)
# IDE	ide	IntegerField		TRUE	TRUE	ide=models.IntegerField(blank=TRUE, null=TRUE)
#////////////////////////// TestModel ///////////////////
class ResModel(models.Model):
    name= models.CharField(max_length=20)
    country = CountryField(blank=True, null=True)

    def __str__(self):
        return self.name




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


class ResTest(models.Model):
    restes_name = models.CharField(max_length=25, null=True, blank=True)



# class ProductModel(models.Model):
#     prod_name = models.CharField(max_length=250)
#     prod_price = models.PositiveIntegerField()
#
#     def __str__(self):
#         return self.prod_name
#
# class ProductMetaModel(models.Model):
#     product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
#     prod_meta_name = models.CharField('Property', max_length=50)
#     prod_meta_value = models.CharField(max_length=200, blank=True, null=True)
#
#     def __str__(self):
#         return f'ID: {self.pk}, {self.prod_meta_name} for ProdcutID: {self.product.pk}'




# class Programmer(models.Model):
#     name = models.CharField(max_length=100)
#
#     def __str__(self):
#         return self.name

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





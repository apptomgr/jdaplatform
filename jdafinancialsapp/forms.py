from django import forms
from .models import CompanyModel, SectorModel, FinancialStatementModel,  \
    FinancialStatementBalLinkModel, FinancialStatementIncLinkModel, FinancialStatementFactModel, \
    FinancialStatementInvAcctLinkModel, ShareholderModel, AddressModel, LeadersModel, ParentCompanyModel, \
    SubsidiaryModel, CountryModel, EconomicDataModel, ElectionModel, EconomicZoneModel, OtherIndicatorsModel, TradePartnersModel, EnergyModel
from jdaanalyticsapp.models import SecurityModel, StockModel, BondModel, GuarantorModel, ExchangeModel
from django_countries.fields import CountryField, countries, country_to_text
from django.utils.translation import ugettext_lazy
from .utils import merge_two_lists, merge_company_lists
from django.forms import inlineformset_factory
from django.forms import modelformset_factory
from countries_plus.models import Country
from django.urls import reverse_lazy
from languages_plus.utils import associate_countries_and_languages
from languages_plus.models import Language, CultureCode
import datetime
#from bootstrap_datepicker_plus.widgets import DatePickerInput
#from bootstrap_datepicker_plus.widgets import DateTimePickerInput
#from bootstrap_datepicker_plus.widgets import DateTimePickerInput

# from jdafinancialsapp.utils import merge_two_lists

# /////////////////////////// SectorForm //////////////////////////
class SectorForm(forms.ModelForm):
    sector = forms.CharField(max_length=50, label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sector...'},))

    class Meta:
        model = SectorModel
        fields = ['sector']


# /////////////////////////// CompanyForm //////////////////////////
class CompanyForm(forms.ModelForm):
    CHOICES = (
        ('', 'Reporting Period'),
        ('Quarterly', 'Quarterly'),
        ('Semi-annually', 'Semi-Annually'),
        ('Annually', 'Annually'),
    )

    corp_name = forms.CharField(max_length=50, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Corporate Name')},))
    company = forms.CharField(max_length=50, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder':ugettext_lazy('Company')},))
    sector = forms.ModelChoiceField(required=False, queryset=SectorModel.objects.all(), empty_label='Type de Tier', label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker show-tick my_dropdown', 'data-live-search=': 'true'}))
    #rpt_period = forms.ChoiceField(choices=CHOICES, label='', widget=forms.Select(attrs={'class': 'form-control-sm selector selectpicker show-tick', 'placeholder':'Reporting Period'}))
    legl_form = forms.CharField(required=False, max_length=50, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm mt-3', 'placeholder': ugettext_lazy('Legal Form')},))
    creatn_dt = forms.DateField(required=False, label='', widget=forms.DateInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Creation Date')}))
    rccm_nbr = forms.CharField(required=False, max_length=20, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm mt-3', 'placeholder': ugettext_lazy('RCCM Number')}, ))
    country = CountryField(blank_label=ugettext_lazy('Country')).formfield(label='', widget=forms.Select(attrs={'class': 'form-control-sm selector selectpicker show-tick', 'data-live-search=': 'true', 'placeholder':ugettext_lazy('Country')}))
    #id_cntry = forms.IntegerField(label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Pays du siege social'}, ))
    #flag_pub_ctrl = forms.BooleanField(label='Societe sous control public', required=False, widget=forms.widgets.CheckboxInput(attrs={'class': 'form-control-sm-sm form-check-input checkbox-inline', 'id':'flag_pub_ctrl'})),
    flag_pub_ctrl = forms.BooleanField(required=False, initial=True, label='', widget=forms.CheckboxInput(attrs={'class':'form-check-input my_checkbox mt-4','type':'checkbox'}))#forms.BooleanField(label='Visible', required=True, widget=forms.widgets.CheckboxInput(attrs={'class': 'form-control-sm-sm selectpicker'})),
    actvty_sctr =forms.CharField(required=False, max_length=30, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Activite Sector BRVM')}, ))
    actvty_code =forms.CharField(required=False, max_length=30, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Activity Code (CIV)')}, ))
    intrnl_actvty_code =forms.CharField(required=False, max_length=30, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Activity Code Joseph & Daniel Adv.')}, ))
    othr_bus_sctr =forms.CharField(required=False, max_length=30, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Other Business Sectors')}, ))
    #shareholder = forms.ModelChoiceField(queryset=ShareholderModel.objects.all(), empty_label='Nome de l\'actionnaire', label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker show-tick', 'data-live-search': 'true'}))

    #shrhldr_name = forms.ModelChoiceField(queryset=ShareholderModel.objects.all(), empty_label='Nome de l\'actionnaire', label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker show-tick my_dropdown'}))
    #shrhldr_name_1 = forms.CharField(max_length=30, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Nom de l\'actionnaire'}, ))
    #shrhldr_type_1 = forms.CharField(max_length=30, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Type d\'actionnaire'}, ))
    #shrs_hld_1 = forms.CharField(max_length=30, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Part detenue'}, ))
    #shrhldr_name_2 = forms.CharField(required = False,max_length=30, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Nom de l\'actionnaire'}, ))
    #shrhldr_type_2 = forms.CharField(required = False,max_length=30, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Type d\'actionnaire'}, ))
    #shrs_hld_2 = forms.CharField(required = False,max_length=30, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Part detenue'}, ))
    #shrhldr_name_3 = forms.CharField(required = False,max_length=30, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Nom de l\'actionnaire'}, ))
    #shrhldr_type_3 = forms.CharField(required = False,max_length=30, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Type d\'actionnaire'}, ))
    #shrs_hld_3 = forms.CharField(required = False,max_length=30, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Part detenue'}, ))
    #shrhldr_name_4 = forms.CharField(required = False,max_length=30, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Nom de l\'actionnaire'}, ))
    #shrhldr_type_4 = forms.CharField(required = False,max_length=30, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Type d\'actionnaire'}, ))
    #shrs_hld_4 = forms.CharField(required = False, max_length=30, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Part detenue'}, ))


    class Meta:
        model = CompanyModel
        fields = '__all__'
        #fields = ['company', 'sector', 'rpt_period']


#///////////////////////////// AddressForm /////////////////////////////////////
class AddressForm(forms.ModelForm):
    addr = forms.CharField(max_length=200, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Address')}, ))
    phone_nbr = forms.CharField(max_length=200, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Phone Number')}, ))
    fax_nbr = forms.CharField(required=False, max_length=100, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Fax Number')}, ))
    email = forms.EmailField(required=False, max_length=100, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Email')}, ))
    website = forms.URLField(required=False, max_length=200, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Website')}, ))

    class Meta:
        model = AddressModel
        fields = ['addr','phone_nbr', 'fax_nbr','email','website']


#///////////////////////////// ShareholderForm //////////////////////////////////////
class ShareholderForm(forms.ModelForm):
    shrhldr_name = forms.CharField(required=False, max_length=100, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Shareholder Name')}, ))
    shrhldr_type = forms.CharField(required=False, max_length=100, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Shareholder Type')}, ))
    shrs_hld = forms.CharField(initial=0.00, required=False, max_length=50, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Shares Held')}, ))

    class Meta:
        model = ShareholderModel
        fields = ['shrhldr_name', 'shrhldr_type','shrs_hld']

#///////////////////////////// ShareholderFormset /////////////////////////////
ShareholderFormset = modelformset_factory(ShareholderModel, form=ShareholderForm, extra=4)
ShareholderFormset_edit = modelformset_factory(ShareholderModel, form=ShareholderForm, extra=0, can_delete=True)
ShareholderFormset_edit_1 = modelformset_factory(ShareholderModel, form=ShareholderForm, extra=3, can_delete=True)
ShareholderFormset_edit_2 = modelformset_factory(ShareholderModel, form=ShareholderForm, extra=2, can_delete=True)
ShareholderFormset_edit_3 = modelformset_factory(ShareholderModel, form=ShareholderForm, extra=1, can_delete=True)
ShareholderFormset_edit_4 = modelformset_factory(ShareholderModel, form=ShareholderForm, extra=0, can_delete=True)
ShareholderFormset_edit_0 = modelformset_factory(ShareholderModel, form=ShareholderForm, extra=4, can_delete=False)

#///////////////////////////// LeadersForm //////////////////////////////////////
class LeadersForm(forms.ModelForm):
    lst_name = forms.CharField(required=False, max_length=100, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Last Name & First Name')}, ))
    func = forms.CharField(required=False, max_length=100, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Function')}, ))
    phone_nbr = forms.CharField(required=False, max_length=50, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Phone Number')}, ))
    email = forms.EmailField(required=False, max_length=50, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Email')}, ))

    class Meta:
        model = LeadersModel
        fields = ['lst_name', 'func','phone_nbr', 'email']

    def clean(self):
        cleaned_data = super(LeadersForm, self).clean()
        lst_name = cleaned_data.get('lst_name')
        func = cleaned_data.get('func')
        phone_nbr = cleaned_data.get('phone_nbr')
        email = cleaned_data.get('email')

        if lst_name and not func and not phone_nbr and not email:
            raise forms.ValidationError('Please complete leader form before proceeding!')

#///////////////////////////// LeadersFormset /////////////////////////////
LeadersFormset = modelformset_factory(LeadersModel, form=LeadersForm, extra=5)
LeadersFormset_edit = modelformset_factory(LeadersModel, form=LeadersForm, extra=0, can_delete=True)
LeadersFormset_edit_1 = modelformset_factory(LeadersModel, form=LeadersForm, extra=4, can_delete=True)
LeadersFormset_edit_2 = modelformset_factory(LeadersModel, form=LeadersForm, extra=3, can_delete=True)
LeadersFormset_edit_3 = modelformset_factory(LeadersModel, form=LeadersForm, extra=2, can_delete=True)
LeadersFormset_edit_4 = modelformset_factory(LeadersModel, form=LeadersForm, extra=1, can_delete=True)
LeadersFormset_edit_5 = modelformset_factory(LeadersModel, form=LeadersForm, extra=0, can_delete=True)
LeadersFormset_edit_0 = modelformset_factory(LeadersModel, form=LeadersForm, extra=5, can_delete=False)

#///////////////////////////// ParentCompanyForm //////////////////////////////////////
class ParentCompanyForm(forms.ModelForm):
    legl_name = forms.CharField(required=False, max_length=200, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Legal Name')}, ))
    comm_name = forms.CharField(required=False, max_length=200, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Company Name')}, ))
    cntry = CountryField(blank_label='Country').formfield(label='', widget=forms.Select(attrs={'class': 'form-control-sm selector selectpicker show-tick', 'data-live-search=': 'true', 'placeholder':ugettext_lazy('Country')}))

    class Meta:
        model = ParentCompanyModel
        fields = ['legl_name', 'comm_name','cntry']

#///////////////////////////// ParentCompanyFormset /////////////////////////////
ParentCompanyFormset = modelformset_factory(ParentCompanyModel, form=ParentCompanyForm, extra=4)
ParentCompanyFormset_edit = modelformset_factory(ParentCompanyModel, form=ParentCompanyForm, extra=0, can_delete=True)
ParentCompanyFormset_edit_1 = modelformset_factory(ParentCompanyModel, form=ParentCompanyForm, extra=3, can_delete=True)
ParentCompanyFormset_edit_2 = modelformset_factory(ParentCompanyModel, form=ParentCompanyForm, extra=2, can_delete=True)
ParentCompanyFormset_edit_3 = modelformset_factory(ParentCompanyModel, form=ParentCompanyForm, extra=1, can_delete=True)
ParentCompanyFormset_edit_4 = modelformset_factory(ParentCompanyModel, form=ParentCompanyForm, extra=0, can_delete=True)
ParentCompanyFormset_edit_0 = modelformset_factory(ParentCompanyModel, form=ParentCompanyForm, extra=4, can_delete=False)


#///////////////////////////// SubsidiaryForm //////////////////////////////////////
class SubsidiaryForm(forms.ModelForm):
    company_name = forms.CharField(required=False, max_length=200, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Company Name')}, ))
    share_amt = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Share Amount')}, ))
    url = forms.URLField(required=False, max_length=200, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Website')}, ))


    class Meta:
        model = ParentCompanyModel
        fields = ['company_name', 'share_amt','url']

#///////////////////////////// SubsidiaryFormset /////////////////////////////
SubsidiaryFormset = modelformset_factory(SubsidiaryModel, form=SubsidiaryForm, extra=4)
SubsidiaryFormset_edit = modelformset_factory(SubsidiaryModel, form=SubsidiaryForm, extra=0, can_delete=True)
SubsidiaryFormset_edit_1 = modelformset_factory(SubsidiaryModel, form=SubsidiaryForm, extra=3, can_delete=True)
SubsidiaryFormset_edit_2 = modelformset_factory(SubsidiaryModel, form=SubsidiaryForm, extra=2, can_delete=True)
SubsidiaryFormset_edit_3 = modelformset_factory(SubsidiaryModel, form=SubsidiaryForm, extra=1, can_delete=True)
SubsidiaryFormset_edit_4 = modelformset_factory(SubsidiaryModel, form=SubsidiaryForm, extra=0, can_delete=True)
SubsidiaryFormset_edit_0 = modelformset_factory(SubsidiaryModel, form=SubsidiaryForm, extra=4, can_delete=False)

# /////////////////////////// CountryForm //////////////////////////
class CountryForm(forms.ModelForm):
    country = CountryField(blank_label=ugettext_lazy('Country')).formfield(label='', widget=forms.Select(attrs={'class': 'form-control-sm selector selectpicker show-tick', 'hx-get':reverse_lazy('jdafinancialsapp_hx_country_data'), 'hx-trigger':'change', 'hx-target':'#country_data', 'hx-swap':'outerHTML','data-live-search=': 'true', 'placeholder':ugettext_lazy('Country')}))
    #name = forms.ModelChoiceField(queryset=Country.objects.order_by('name').values_list('name', flat='True').distinct(), empty_label=ugettext_lazy('Country Name'), label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker show-tick','data-live-search=': 'true'}))
    crncy = forms.CharField(required=False, max_length=200, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Currency Code')}, ))
    #forms.ModelChoiceField(queryset=Country.objects.order_by('currency_code').values_list('currency_code', flat='True').distinct(), empty_label=ugettext_lazy('Currency'), label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker show-tick','data-live-search=': 'true'}))
    prsdnt_name = forms.CharField(required=False, max_length=200, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('President Name')}, ))
    area = forms.CharField(required=False, max_length=200, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Area')}, ))
    #area = forms.ModelChoiceField(queryset=Country.objects.order_by('area').values_list('area', flat='True').all(), empty_label=ugettext_lazy('Area'), label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker show-tick','data-live-search=': 'true'}))
    ofcl_lang = forms.CharField(required=False, max_length=200, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Official Language')}, ))
    #ofcl_lang = forms.ModelChoiceField(queryset= Language.objects.all().distinct(), empty_label=ugettext_lazy('Language'), label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker show-tick','data-live-search=': 'true'}))
    #continent = forms.ModelChoiceField(required=False, queryset=Country.objects.order_by('continent').values_list('continent', flat='True').distinct(), empty_label=ugettext_lazy('Continent'), label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker show-tick','data-live-search=': 'true'}))
    continent = forms.CharField(required=False, max_length=200, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Continent')}, ))
    #area = CountryField(blank_label=ugettext_lazy('area')).formfield(label='', widget=forms.Select(attrs={'class': 'form-control-sm selector selectpicker show-tick', 'data-live-search=': 'true', 'placeholder':ugettext_lazy('Area')}))
    #crncy = CountryField(blank_label=ugettext_lazy('Currency')).formfield(label='', widget=forms.Select(attrs={'class': 'form-control-sm selector selectpicker show-tick', 'data-live-search=': 'true', 'placeholder':ugettext_lazy('Currency')}))
    #area = CountryField(blank_label=ugettext_lazy('Area')).formfield(label='', widget=forms.Select(attrs={'class': 'form-control-sm selector selectpicker show-tick', 'data-live-search=': 'true', 'placeholder':ugettext_lazy('Area')}))
    #world_region = forms.ModelChoiceField(queryset=Country.objects.values_list('capital', flat='True').all(), empty_label=ugettext_lazy('World Region'), label='', widget=forms.Select(attrs={'class': 'form-control selectpicker show-tick','data-live-search=': 'true'}))
    #capl_city = forms.ModelChoiceField(queryset=Country.objects.order_by('capital').values_list('capital', flat='True').all(), empty_label=ugettext_lazy('Capital'), label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker show-tick','data-live-search=': 'true'}))
    capl_city = forms.CharField(required=False, max_length=200, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Capital City')}, ))
    #ph_code = forms.ModelChoiceField(queryset=Country.objects.values_list('phone', flat='True').distinct(), empty_label=ugettext_lazy('Country Code'), label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker show-tick','data-live-search=': 'true'}))
    ph_code = forms.CharField(required=False, max_length=200, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Country Code')}, ))

    class Meta:
        model = CountryModel
        fields = '__all__'
        #fields = ['company', 'sector', 'rpt_period']


# /////////////////////////// EconomicDataForm //////////////////////////
class EconomicDataForm(forms.ModelForm):
    yr = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Year')}))
    popltn = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Population'}, ))
    popltn_grth_rate = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'percentInput form-control form-control-sm', 'placeholder':'Population Growth Rate'}))
    actv_popltn = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'percentInput form-control form-control-sm', 'placeholder':'Active Population'}))
    lf_exprn = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Life Expectancy'}, ))
    unemplmt_rate = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Unemployment Rate'}, ))
    poverty_rate = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Poverty Rate'}, ))
    rnkg_bus  = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Business Ranking'}, ))
    hsehold_cnsmptn = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'percentInput form-control form-control-sm', 'placeholder':'Household Consumption'}))
    idh = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'percentInput form-control form-control-sm', 'placeholder':'IDH'}))

    yr_gdp = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('GDP Year')}))
    gdp_amt = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'percentInput form-control form-control-sm', 'placeholder':'GDP (XOF billion)'}))
    gdp_rate = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'percentInput form-control form-control-sm', 'placeholder':'GDP Rate'}))
    gdp_prim_sctr = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'percentInput form-control form-control-sm', 'placeholder':'Primary GDP Sector'}))
    gdp_secy_sctr = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'percentInput form-control form-control-sm', 'placeholder':'Secondary GDP Sector'}))
    gdp_tertry_sctr = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'percentInput form-control form-control-sm', 'placeholder':'Tertiary GDP Sector'}))
    gr_ntnl_prodt = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'percentInput form-control form-control-sm', 'placeholder':'Gross National Product'}))
    mrgnl_lndg_rate = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'percentInput form-control form-control-sm', 'placeholder':'Marginal Index Rate'}))
    fixd_capl_invstmt = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'percentInput form-control form-control-sm', 'placeholder':'Fixed Capital Investment'}))
    ide = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'percentInput form-control form-control-sm', 'placeholder':'IDE'}))

    yr_dbt = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Debt Year')}))
    infltn_rate = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'percentInput form-control form-control-sm', 'placeholder':'Inflation Rate'}))
    pub_dbt = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Public Debt')}))
    forgn_dbt = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Foreign Debt')}))
    dmstc_dbt = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Domestic Debt')}))
    trd_bal = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Trade Balance')}))
    exp_amt = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Export Amount')}))
    imp_amt = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Import Amount')}))

    class Meta:
        model = EconomicDataModel
        fields = '__all__'

#///////////////////////////// EconomicDataFormset /////////////////////////////
EconomicDataFormset = modelformset_factory(EconomicDataModel, form=EconomicDataForm, extra=10)
EconomicDataFormset_edit = modelformset_factory(EconomicDataModel, form=EconomicDataForm, extra=0, can_delete=True)
EconomicDataFormset_edit_0 = modelformset_factory(EconomicDataModel, form=EconomicDataForm, extra=10, can_delete=False)
EconomicDataFormset_edit_1 = modelformset_factory(EconomicDataModel, form=EconomicDataForm, extra=9, can_delete=True)
EconomicDataFormset_edit_2 = modelformset_factory(EconomicDataModel, form=EconomicDataForm, extra=8, can_delete=True)
EconomicDataFormset_edit_3 = modelformset_factory(EconomicDataModel, form=EconomicDataForm, extra=7, can_delete=True)
EconomicDataFormset_edit_4 = modelformset_factory(EconomicDataModel, form=EconomicDataForm, extra=6, can_delete=True)
EconomicDataFormset_edit_5 = modelformset_factory(EconomicDataModel, form=EconomicDataForm, extra=5, can_delete=True)
EconomicDataFormset_edit_6 = modelformset_factory(EconomicDataModel, form=EconomicDataForm, extra=4, can_delete=True)
EconomicDataFormset_edit_7 = modelformset_factory(EconomicDataModel, form=EconomicDataForm, extra=3, can_delete=True)
EconomicDataFormset_edit_8 = modelformset_factory(EconomicDataModel, form=EconomicDataForm, extra=2, can_delete=True)
EconomicDataFormset_edit_9 = modelformset_factory(EconomicDataModel, form=EconomicDataForm, extra=1, can_delete=True)
EconomicDataFormset_edit_10 = modelformset_factory(EconomicDataModel, form=EconomicDataForm, extra=0, can_delete=True)

# /////////////////////////// ElectionForm //////////////////////////
class ElectionForm(forms.ModelForm):
    elecn_dt = forms.DateField(required=False, label='', widget=forms.DateInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Election Date')}))
    elecn_type = forms.CharField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Election Type'}, ))
    cmnts = forms.CharField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Comments'}, ))

    class Meta:
        model = ElectionModel
        fields = '__all__'

#///////////////////////////// ElectionFormset /////////////////////////////
ElectionFormset= modelformset_factory(ElectionModel, form=ElectionForm, extra=10)
ElectionFormset_edit = modelformset_factory(ElectionModel, form=ElectionForm, extra=0, can_delete=True)
ElectionFormset_edit_0 = modelformset_factory(ElectionModel, form=ElectionForm, extra=10, can_delete=False)
ElectionFormset_edit_1 = modelformset_factory(ElectionModel, form=ElectionForm, extra=9, can_delete=True)
ElectionFormset_edit_2 = modelformset_factory(ElectionModel, form=ElectionForm, extra=8, can_delete=True)
ElectionFormset_edit_3 = modelformset_factory(ElectionModel, form=ElectionForm, extra=7, can_delete=True)
ElectionFormset_edit_4 = modelformset_factory(ElectionModel, form=ElectionForm, extra=6, can_delete=True)
ElectionFormset_edit_5 = modelformset_factory(ElectionModel, form=ElectionForm, extra=5, can_delete=True)
ElectionFormset_edit_6 = modelformset_factory(ElectionModel, form=ElectionForm, extra=4, can_delete=True)
ElectionFormset_edit_7 = modelformset_factory(ElectionModel, form=ElectionForm, extra=3, can_delete=True)
ElectionFormset_edit_8 = modelformset_factory(ElectionModel, form=ElectionForm, extra=2, can_delete=True)
ElectionFormset_edit_9 = modelformset_factory(ElectionModel, form=ElectionForm, extra=1, can_delete=True)
ElectionFormset_edit_10 = modelformset_factory(ElectionModel, form=ElectionForm, extra=0, can_delete=True)

# /////////////////////////// EconomicZoneForm //////////////////////////
class EconomicZoneForm(forms.ModelForm):
    econ_zone = forms.CharField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Economic Zone')}, ))

    class Meta:
        model = EconomicZoneModel
        fields = '__all__'

#///////////////////////////// economicZoneFormset /////////////////////////////
EconomicZoneFormset= modelformset_factory(EconomicZoneModel, form=EconomicZoneForm, extra=10)
EconomicZoneFormset_edit = modelformset_factory(EconomicZoneModel, form=EconomicZoneForm, extra=0, can_delete=True)
EconomicZoneFormset_edit_0 = modelformset_factory(EconomicZoneModel, form=EconomicZoneForm, extra=10, can_delete=False)
EconomicZoneFormset_edit_1 = modelformset_factory(EconomicZoneModel, form=EconomicZoneForm, extra=9, can_delete=True)
EconomicZoneFormset_edit_2 = modelformset_factory(EconomicZoneModel, form=EconomicZoneForm, extra=8, can_delete=True)
EconomicZoneFormset_edit_3 = modelformset_factory(EconomicZoneModel, form=EconomicZoneForm, extra=7, can_delete=True)
EconomicZoneFormset_edit_4 = modelformset_factory(EconomicZoneModel, form=EconomicZoneForm, extra=6, can_delete=True)
EconomicZoneFormset_edit_5 = modelformset_factory(EconomicZoneModel, form=EconomicZoneForm, extra=5, can_delete=True)
EconomicZoneFormset_edit_6 = modelformset_factory(EconomicZoneModel, form=EconomicZoneForm, extra=4, can_delete=True)
EconomicZoneFormset_edit_7 = modelformset_factory(EconomicZoneModel, form=EconomicZoneForm, extra=3, can_delete=True)
EconomicZoneFormset_edit_8 = modelformset_factory(EconomicZoneModel, form=EconomicZoneForm, extra=2, can_delete=True)
EconomicZoneFormset_edit_9 = modelformset_factory(EconomicZoneModel, form=EconomicZoneForm, extra=1, can_delete=True)
EconomicZoneFormset_edit_10 = modelformset_factory(EconomicZoneModel, form=EconomicZoneForm, extra=0, can_delete=True)

# /////////////////////////// OtherIndicatorsForm //////////////////////////
class OtherIndicatorsForm(forms.ModelForm):
    yr = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Year')}, ))
    ind_name = forms.CharField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Index')}, ))
    ind_val = forms.CharField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Valeur')}, ))
    cmnts = forms.CharField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Comments')}, ))

    class Meta:
        model = OtherIndicatorsModel
        fields = '__all__'

#///////////////////////////// OtherIndicatorsFormset /////////////////////////////
OtherIndicatorsFormset= modelformset_factory(OtherIndicatorsModel, form=OtherIndicatorsForm, extra=10)
OtherIndicatorsFormset_edit = modelformset_factory(OtherIndicatorsModel, form=OtherIndicatorsForm, extra=0, can_delete=True)
OtherIndicatorsFormset_edit_0 = modelformset_factory(OtherIndicatorsModel, form=OtherIndicatorsForm, extra=10, can_delete=False)
OtherIndicatorsFormset_edit_1 = modelformset_factory(OtherIndicatorsModel, form=OtherIndicatorsForm, extra=9, can_delete=True)
OtherIndicatorsFormset_edit_2 = modelformset_factory(OtherIndicatorsModel, form=OtherIndicatorsForm, extra=8, can_delete=True)
OtherIndicatorsFormset_edit_3 = modelformset_factory(OtherIndicatorsModel, form=OtherIndicatorsForm, extra=7, can_delete=True)
OtherIndicatorsFormset_edit_4 = modelformset_factory(OtherIndicatorsModel, form=OtherIndicatorsForm, extra=6, can_delete=True)
OtherIndicatorsFormset_edit_5 = modelformset_factory(OtherIndicatorsModel, form=OtherIndicatorsForm, extra=5, can_delete=True)
OtherIndicatorsFormset_edit_6 = modelformset_factory(OtherIndicatorsModel, form=OtherIndicatorsForm, extra=4, can_delete=True)
OtherIndicatorsFormset_edit_7 = modelformset_factory(OtherIndicatorsModel, form=OtherIndicatorsForm, extra=3, can_delete=True)
OtherIndicatorsFormset_edit_8 = modelformset_factory(OtherIndicatorsModel, form=OtherIndicatorsForm, extra=2, can_delete=True)
OtherIndicatorsFormset_edit_9 = modelformset_factory(OtherIndicatorsModel, form=OtherIndicatorsForm, extra=1, can_delete=True)
OtherIndicatorsFormset_edit_10 = modelformset_factory(OtherIndicatorsModel, form=OtherIndicatorsForm, extra=0, can_delete=True)

# /////////////////////////// TradePartnersForm //////////////////////////
class TradePartnersForm(forms.ModelForm):
    yr = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Year')}, ))
    exp_cntry = CountryField(blank_label=ugettext_lazy('Country')).formfield(required=False, label='', widget=forms.Select(attrs={'class': 'form-control-sm selector selectpicker show-tick', 'data-live-search=': 'true', 'placeholder':ugettext_lazy('Country')}))
    exp_amt = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Export Amount')}, ))
    exp_rate = forms.DecimalField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Export Rate')}, ))
    exp_prodt_name = forms.CharField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder':ugettext_lazy('Product')}))
    imp_cntry = CountryField(blank_label=ugettext_lazy('Country')).formfield(required=False, label='', widget=forms.Select(attrs={'class': 'form-control-sm selector selectpicker show-tick', 'data-live-search=': 'true', 'placeholder':ugettext_lazy('Country')}))
    imp_amt = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Import Amount')}, ))
    imp_rate = forms.DecimalField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Import Rate')}, ))
    imp_prodt_name = forms.CharField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder':ugettext_lazy('Product')}))

    class Meta:
        model = TradePartnersModel
        fields = '__all__'

#///////////////////////////// TradePartnersFormset /////////////////////////////
TradePartnersFormset= modelformset_factory(TradePartnersModel, form=TradePartnersForm, extra=10)
TradePartnersFormset_edit = modelformset_factory(TradePartnersModel, form=TradePartnersForm, extra=0, can_delete=True)
TradePartnersFormset_edit_0 = modelformset_factory(TradePartnersModel, form=TradePartnersForm, extra=10, can_delete=False)
TradePartnersFormset_edit_1 = modelformset_factory(TradePartnersModel, form=TradePartnersForm, extra=9, can_delete=True)
TradePartnersFormset_edit_2 = modelformset_factory(TradePartnersModel, form=TradePartnersForm, extra=8, can_delete=True)
TradePartnersFormset_edit_3 = modelformset_factory(TradePartnersModel, form=TradePartnersForm, extra=7, can_delete=True)
TradePartnersFormset_edit_4 = modelformset_factory(TradePartnersModel, form=TradePartnersForm, extra=6, can_delete=True)
TradePartnersFormset_edit_5 = modelformset_factory(TradePartnersModel, form=TradePartnersForm, extra=5, can_delete=True)
TradePartnersFormset_edit_6 = modelformset_factory(TradePartnersModel, form=TradePartnersForm, extra=4, can_delete=True)
TradePartnersFormset_edit_7 = modelformset_factory(TradePartnersModel, form=TradePartnersForm, extra=3, can_delete=True)
TradePartnersFormset_edit_8 = modelformset_factory(TradePartnersModel, form=TradePartnersForm, extra=2, can_delete=True)
TradePartnersFormset_edit_9 = modelformset_factory(TradePartnersModel, form=TradePartnersForm, extra=1, can_delete=True)
TradePartnersFormset_edit_10 = modelformset_factory(TradePartnersModel, form=TradePartnersForm, extra=0, can_delete=True)


# /////////////////////////// EnergyForm //////////////////////////
class EnergyForm(forms.ModelForm):
    energy_yr = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Year')}, ))
    elec_hydro_dam_nbr = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Hydroelectric Dams')}, ))
    elec_pwr_sttn_nbr = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Central Electric')}, ))
    elec_otr_nbr = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Others')}, ))
    crude_prodtn_amt = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Production')}, ))
    crude_exp_amt = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Exports')}, ))
    crude_imp_amt = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Imports')}, ))
    crude_rsrvs_amt = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Reserves')}, ))
    refined_prodtn_amt = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Production')}, ))
    refined_cnsmptn_amt = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Consumption')}, ))
    refined_exp_amt = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Exports')}, ))
    refined_imp_amt = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Imports')}, ))
    gas_prodtn_amt = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Production')}, ))
    gas_exp_amt = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Exports')}, ))
    gas_imp_amt = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Imports')}, ))
    gas_rsrv_amt = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Reserves')}, ))

    class Meta:
        model = EnergyModel
        fields = '__all__'

#///////////////////////////// EnergyFormset /////////////////////////////
EnergyFormset= modelformset_factory(EnergyModel, form=EnergyForm, extra=10)
EnergyFormset_edit = modelformset_factory(EnergyModel, form=EnergyForm, extra=0, can_delete=True)
EnergyFormset_edit_0 = modelformset_factory(EnergyModel, form=EnergyForm, extra=10, can_delete=False)
EnergyFormset_edit_1 = modelformset_factory(EnergyModel, form=EnergyForm, extra=9, can_delete=True)
EnergyFormset_edit_2 = modelformset_factory(EnergyModel, form=EnergyForm, extra=8, can_delete=True)
EnergyFormset_edit_3 = modelformset_factory(EnergyModel, form=EnergyForm, extra=7, can_delete=True)
EnergyFormset_edit_4 = modelformset_factory(EnergyModel, form=EnergyForm, extra=6, can_delete=True)
EnergyFormset_edit_5 = modelformset_factory(EnergyModel, form=EnergyForm, extra=5, can_delete=True)
EnergyFormset_edit_6 = modelformset_factory(EnergyModel, form=EnergyForm, extra=4, can_delete=True)
EnergyFormset_edit_7 = modelformset_factory(EnergyModel, form=EnergyForm, extra=3, can_delete=True)
EnergyFormset_edit_8 = modelformset_factory(EnergyModel, form=EnergyForm, extra=2, can_delete=True)
EnergyFormset_edit_9 = modelformset_factory(EnergyModel, form=EnergyForm, extra=1, can_delete=True)
EnergyFormset_edit_10 = modelformset_factory(EnergyModel, form=EnergyForm, extra=0, can_delete=True)

#///////////////////////////// fin_stmt_dash_form //////////////////////////////////////
class FinStmtDashForm(forms.Form):

    PERIODS = (
        ('Q1', 'Quarter 1'),
        ('Q2', '1/2 Year'),
        ('Q3', 'Quarter 3'),
        ('Q4', 'Full Year'),
    )

    sector = forms.ModelChoiceField(queryset=SectorModel.objects.all(), empty_label=ugettext_lazy('Sector'), label='',
                                     widget=forms.Select(attrs={'class': 'form-control selectpicker show-tick',
                                                                'data-live-search=': 'true'}))

    company = forms.ModelChoiceField(queryset=CompanyModel.objects.all(), empty_label=ugettext_lazy('Company'), label='',
                                     widget=forms.Select(attrs={'class': 'form-control selectpicker show-tick',
                                                                'data-live-search=': 'true'}))

    statement = forms.ModelChoiceField(queryset=FinancialStatementModel.objects.all(), empty_label=ugettext_lazy('Statement'), label='',
                                     widget=forms.Select(attrs={'class': 'form-control selectpicker show-tick',
                                                                'data-live-search=': 'true'}))

    date = forms.DateField(label='', widget=forms.DateInput(attrs={'class': 'form-control selectpicker', 'placeholder':'Date'}))
    #date = forms.DateTimeField(input_formats=['%d/%m/%Y'], label='')

    """
    def clean(self):
        cleaned_data = super(FinStmtDashForm, self).clean()
        sector = cleaned_data.get('sector')
        company = cleaned_data.get('company')
        statement = cleaned_data.get('statement')
        date = cleaned_data.get('date')

        if not sector and not company and not statement and not date:
            raise forms.ValidationError('You have to write something!')
    """

#///////////////////////// BalanceSheetForm /////////////////////
class BalanceSheetForm(forms.ModelForm):
    brut_0 = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder':'0.00'}))
    brut_1 = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder':'0.00'}))
    brut_2 = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_3 = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_4 = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_5 = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_6 = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_7 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_8 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_9 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_10 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_11 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_12 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_13 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_14 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_15 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_16 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_17 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_18 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_19 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_20 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_21 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_22 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_23 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_24 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_25 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_26 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_27 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_28 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_29 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_30 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_31 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_32 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_33 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_34 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_35 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_36 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_37 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_38 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_39 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_40 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_41 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_42 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_43 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_44 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_45 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_46 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_47 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_48 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_49 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_50 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_51 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_52 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_53 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_54 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_55 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_56 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_57 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_58 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    #brut_59 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))

    amort_0 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder':'0.00'}))
    amort_1 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder':'0.00'}))
    amort_2 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_3 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_4 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_5 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_6 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_7 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_8 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_9 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_10 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_11 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_12 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_13 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_14 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_15 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_16 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_17 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_18 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_19 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_20 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_21 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_22 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_23 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_24 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_25 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_26 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_27 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_28 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_29 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_30 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_31 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_32 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_33 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_34 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_35 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_36 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_37 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_38 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_39 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_40 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_41 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_42 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_43 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_44 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_45 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_46 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_47 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_48 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_49 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_50 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_51 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_52 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_53 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_54 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_55 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_56 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_57 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_58 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    #amort_59 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))

    net_0 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder':'0.00'}))
    net_1 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder':'0.00'}))
    net_2 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_3 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_4 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_5 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_6 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_7 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_8 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_9 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_10 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_11 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_12 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_13 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_14 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_15 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_16 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_17 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_18 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_19 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_20 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_21 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_22 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_23 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_24 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_25 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_26 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_27 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_28 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_29 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_30 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_31 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_32 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_33 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_34 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_35 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_36 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_37 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_38 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_39 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_40 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_41 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_42 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_43 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_44 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_45 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_46 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_47 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_48 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_49 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_50 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_51 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_52 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_53 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_54 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_55 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_56 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_57 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_58 = forms.DecimalField(required=False, max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    #net_59 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))

    class Meta:
        model = FinancialStatementBalLinkModel
        fields = ['brut_0','brut_1','brut_2','brut_3','brut_4','brut_5','brut_6','brut_7','brut_8','brut_9','brut_10','brut_11',
                  'brut_12','brut_13','brut_14','brut_15','brut_16','brut_17','brut_18','brut_19','brut_20','brut_21',
                  'brut_22','brut_23','brut_24','brut_25','brut_26','brut_27','brut_28','brut_29','brut_30','brut_31',
                  'brut_32','brut_33','brut_34','brut_35','brut_36','brut_37','brut_38','brut_39','brut_40','brut_41',
                  'brut_42','brut_43','brut_44','brut_45','brut_46','brut_47','brut_48','brut_49','brut_50','brut_51',
                  'brut_52','brut_53','brut_54','brut_55','brut_56','brut_57','brut_58',

                  'amort_0','amort_1','amort_2','amort_3','amort_4','amort_5','amort_6','amort_7','amort_8','amort_9','amort_10','amort_11',
                  'amort_12','amort_13','amort_14','amort_15','amort_16','amort_17','amort_18','amort_19','amort_20','amort_21',
                  'amort_22','amort_23','amort_24','amort_25','amort_26','amort_27','amort_28','amort_29','amort_30','amort_31',
                  'amort_32','amort_33','amort_34','amort_35','amort_36','amort_37','amort_38','amort_39','amort_40','amort_41',
                  'amort_42','amort_43','amort_44','amort_45','amort_46','amort_47','amort_48','amort_49','amort_50','amort_51',
                  'amort_52','amort_53','amort_54','amort_55','amort_56','amort_57','amort_58',

                  'net_0','net_1','net_2','net_3','net_4','net_5','net_6','net_7','net_8','net_9','net_10','net_11',
                  'net_12','net_13','net_14','net_15','net_16','net_17','net_18','net_19','net_20','net_21',
                  'net_22','net_23','net_24','net_25','net_26','net_27','net_28','net_29','net_30','net_31',
                  'net_32','net_33','net_34','net_35','net_36','net_37','net_38','net_39','net_40','net_41',
                  'net_42','net_43','net_44','net_45','net_46','net_47','net_48','net_49','net_50','net_51',
                  'net_52','net_53','net_54','net_55','net_56','net_57','net_58'
                 ]
        #fields = '__all__'

    def clean(self):
        cleaned_data = super(BalanceSheetForm, self).clean()
        #bal_type = cleaned_data.get('bal_type')
        #bal_company = cleaned_data.get('bal_company')
        #bal_date = cleaned_data.get('bal_date')

        #if not bal_type and not bal_company and not bal_date:
        #    raise forms.ValidationError('BalanceSheetForm: Missing values!')
    """
    def clean_bal_date(self):
        date = self.cleaned_data['bal_date']
        rpt_date = self.bal_company__rpt_period
        if (rpt_date == 'Quarterly'):
            print(f"70: rpt_date{rpt_date} date.month: {date.month}")
            if date.month in range(10, 13):  # Q4 range takes 1 month out
                lst_range = [10, 13]
                print(f"73: lst_range: {lst_range}")
            elif date.month in range(7, 10):
                print(f"75: rpt_date{rpt_date}")
                lst_range = [7, 10]
            elif date.month in range(4, 7):
                print(f"78: rpt_date{rpt_date}")
                lst_range = [4, 7]
            elif date.month in range(1, 4):
                print(f"81: rpt_date{rpt_date}")
                lst_range = [1, 4]
        elif (rpt_date == 'Semi-annually'):
            pass
        elif (rpt_date == 'Annually'):
            lst_range = [1, 13]
        else:
            print("88:////////////Ukn rpt_date")
        if rpt_date is None:
            raise forms.ValidationError("Item name is a required field", code="invalid", )
        #if len(name) < 1:
        #    raise forms.ValidationError("Item name is a required field", code="invalid", )

        return self.cleaned_data['bal_date']
    """
#///////////////////////// IncomeStatementForm /////////////////////
class IncomeStatementForm(forms.ModelForm):
    brut_0 = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder':'0.00'}))
    brut_1 = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder':'0.00'}))
    brut_2 = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_3 = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_4 = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_5 = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_6 = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_7 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_8 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_9 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_10 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_11 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_12 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_13 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_14 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_15 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_16 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_17 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_18 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_19 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_20 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_21 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_22 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_23 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_24 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_25 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_26 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_27 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_28 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_29 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_30 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_31 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_32 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_33 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_34 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_35 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_36 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_37 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_38 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_39 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_40 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_41 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_42 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))

    class Meta:
        model = FinancialStatementIncLinkModel
        #fields = ['brut_0','brut_1','brut_2','brut_3','brut_4']
        fields = ['brut_0','brut_1','brut_2','brut_3','brut_4','brut_5','brut_6','brut_7','brut_8','brut_9','brut_10','brut_11',
                  'brut_12','brut_13','brut_14','brut_15','brut_16','brut_17','brut_18','brut_19','brut_20','brut_21',
                  'brut_22','brut_23','brut_24','brut_25','brut_26','brut_27','brut_28','brut_29','brut_30','brut_31',
                  'brut_32','brut_33','brut_34','brut_35','brut_36','brut_37','brut_38','brut_39','brut_40','brut_41',
                  'brut_42'
                  ]



#///////////////////////// InvestmentAccountForm /////////////////////
class InvestmentAccountForm(forms.ModelForm):
    brut_0 = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder':'0.00'}))
    brut_1 = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder':'0.00'}))
    brut_2 = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_3 = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_4 = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_5 = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_6 = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))

    amort_0 = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder':'0.00'}))
    amort_1 = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder':'0.00'}))
    amort_2 = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_3 = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_4 = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_5 = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_6 = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))


    class Meta:
        model = FinancialStatementInvAcctLinkModel
        fields = ['brut_0','brut_1','brut_2','brut_3','brut_4','brut_5','brut_6','amort_0','amort_1','amort_2','amort_3','amort_4','amort_5','amort_6']


#/////////////////////////// SecurityForm //////////////////////////
class SecurityForm(forms.ModelForm):
    CHOICES_LISTG = (
        ('','Listing Status'),
        ('Listed', 'Listed'),
        ('Unlisted', 'Unlisted'),
        ('Suspended', 'Suspended'),
        ('Deleted', 'Deleted'),
    )

    CHOICES_TITLE_TYPE = (
        ('', ugettext_lazy('Title Type')),
        ('Listed Share', 'Listed Share'),
        ('Listed Bond', 'Listed Bond'),
        ('Unlisted Share', 'Unlisted Share'),
        ('Unlisted Bond', 'Unlisted Bond'),
    )

    CHOICES_SHR_CLASS = (
        ('', ugettext_lazy('Share Class')),
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
    )

    CHOICES_ISUR_TYPE = (
        ('',ugettext_lazy('Issuer Type')),
        ('Private', 'Private'),
        ('Public', 'Public'),
    )

    CHOICES_RGSTRR = (
        ('', ugettext_lazy('Registrar')),
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
        ('', ugettext_lazy('Depository')),
        ('BCEAO','BCEAO'),
        ('DC/BR','DC/BR'),
    )





    CHOICES_SECTOR = (
        ('', ugettext_lazy('Activity Sector')),
        ('Agriculture', 'Agriculture'),
        ('Banking', 'Banking'),
        ('Manufacture', 'Manufacture'),
    )
    # Combining Country and Company -> Issuer
    # countries = merge_two_lists(list(countries)[:3], list(countries)[:3])
    #list1 = [1, 2, 3]
    #list2 = ['a', 'b', 'c']
    #for code, name in list(countries)[:3]:
    #    #print(f"{name} ({name})")
    #    country_list = merge_two_lists(name, list1)
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
    isin = forms.CharField(max_length=12, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'ISIN'}, ))
    name = forms.CharField(required=False, max_length=200, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Name'}, ))
    ticker =forms.CharField(max_length=12, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Ticker')}, ))
    desc = forms.CharField(required=False, max_length=50, label='', widget=forms.TextInput(attrs={'class':'form-control-sm', 'placeholder':'Description'},))
    # isu_dt = forms.DateField(label='', widget=forms.DateInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Issuer Date'}))
    isu_dt =forms.DateField(required=False, label='', widget=forms.DateInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Issue Date')}))
    # open_date = forms.DateField(label='', widget=forms.DateInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Open Date'}))
    open_dt = forms.DateField(required=False, label='', widget=forms.DateInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Open Date')}))
    close_dt = forms.DateField(required=False, label='', widget=forms.DateInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Close Date')}))
    # close_date = forms.DateField(label='', widget=forms.DateInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Close Date'}))
    listg_sts = forms.ChoiceField(required=False, choices=CHOICES_LISTG, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Listing Status')}))
    nmnl_amt = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':ugettext_lazy('Nominal Value')}))
    cntry = CountryField(blank=True, blank_label=ugettext_lazy('Country')).formfield(label='', widget=forms.Select(attrs={'class': 'form-control-sm selector selectpicker show-tick', 'data-live-search=': 'true', 'placeholder':ugettext_lazy('Country')}))
    # cntry = # forms.ModelChoiceField(queryset=CountryField.objects.all(), empty_label='Country', label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker show-tick my_dropdown', 'data-live-search=': 'true'}))
    currency = forms.CharField(required=False, max_length=5, label='', widget=forms.TextInput(attrs={'class':'form-control-sm', 'placeholder':ugettext_lazy('Currency')},))
    min_lot = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Lot Minimum')}, ))
    ttl_type = forms.ChoiceField(required=False, choices=CHOICES_TITLE_TYPE, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Title Type')}))
    shr_class = forms.ChoiceField(required=False, choices=CHOICES_SHR_CLASS, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Share Class')}))
    isur_type = forms.ChoiceField(required=False, choices=CHOICES_ISUR_TYPE, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Issuer Type')}))
    # actvy_sector = forms.ChoiceField(choices=CHOICES_SECTOR, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Activity Sector'}))
    sector = forms.ModelChoiceField(required=False, queryset=SectorModel.objects.all(), empty_label='Sector', label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker show-tick my_dropdown', 'data-live-search=': 'true'}))
    #issue = forms.ModelChoiceField(queryset=CompanyModel.objects.all(), empty_label='Issue', label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker show-tick my_dropdown', 'data-live-search=': 'true'})) # Drop down values from Exchange table
    issuer = forms.ChoiceField(required=False, choices=CHOICES_ISSUE_LIST, label='', widget=forms.Select(attrs={'class': 'form-control-sm selector selectpicker show-tick', 'data-live-search=': 'true', 'placeholder':ugettext_lazy('Issuer')}))
    rgstrr = forms.ChoiceField(required=False, choices=CHOICES_RGSTRR, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Security Status')}))
    exchg  = forms.ModelMultipleChoiceField(required=False, queryset=ExchangeModel.objects.all(), label='', widget=forms.SelectMultiple(attrs={'class': 'form-control-sm selectpicker show-tick my_dropdown', 'multiple':'multiple', 'data-live-search=': 'true', 'title':ugettext_lazy('Exchange')})) # Drop down values from Exchange table
    depsty = forms.ChoiceField(required=False, choices=CHOICES_DEPSTY, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Depository')}))
    cntry_tax = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':ugettext_lazy('Country Tax')}))
    invstr_cntry_tax = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':ugettext_lazy('Local Tax')}))
    txtn_code = forms.NullBooleanField(required=False, initial=True, label='', widget=forms.CheckboxInput(attrs={'class':'form-check-input my_checkbox','type':'checkbox'}))
    exchg_tax = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':ugettext_lazy('Exchange Tax')}))
    val_code = forms.NullBooleanField(required=False, initial=True, label='', widget=forms.CheckboxInput(attrs={'class':'form-check-input my_checkbox','type':'checkbox'}))
    lwst_appl_rate = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':ugettext_lazy('Lowest Applied Rate')}))
    hghst_appl_rate = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':ugettext_lazy('Highest Applied Rate')}))


    class Meta:
        model = SecurityModel
        fields = '__all__'

# ////////////////////////// StockModelForm /////////////////////////////
class StockModelForm(forms.ModelForm):
    CHOICES_SECR_STS = (
        ('', ugettext_lazy('Security Status')),
        ('Listed','Listed'),
        ('Unquoted', 'Unquoted'),
        ('Suspended', 'Suspended'),
        ('Deleted', 'Deleted'),
    )
    stock_type = forms.CharField(required=False, max_length=25, label='', widget=forms.TextInput(attrs={'class':'form-control-sm', 'placeholder':ugettext_lazy('Stock Type')},))
    under_stock_type  = forms.CharField(required=False, max_length=25, label='', widget=forms.TextInput(attrs={'class':'form-control-sm', 'placeholder':ugettext_lazy('Under Stock Type')},))
    secr_status = forms.ChoiceField(required=False, choices=CHOICES_SECR_STS, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Security Status')}))
    dvdnd = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':ugettext_lazy('Dividend Per Share')}))
    lstn_dt = forms.DateField(required=False, label='', widget=forms.DateInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Listing Date')}))

    class Meta:
        model = StockModel
        fields = ('stock_type','under_stock_type', 'secr_status','dvdnd')

# ////////////////////////// BondModelForm /////////////////////////////
class BondModelForm(forms.ModelForm):
    CHOICES_BND_TYPE = (
        ('', ugettext_lazy('Bond Type')),
        ('Redeemable in Shares', 'Redeemable in Shares'),
        ('Constant Redemption Bond', 'Constant Redemption Bond'),
        ('Deferred Constant Redemption Bond', 'Deferred Constant Redemption Bond'),
        ('In Fine Bond', 'In Fine Bond'),
    )

    CHOICES_DURATN_UNITS = (
        ('', ugettext_lazy('Duration Units')),
        ('Monthly', 'Monthly'),
        ('Quarterly', 'Quarterly'),
        ('Semi-Annually', 'Semi-Annually'),
        ('Annually', 'Annually'),
    )
    CHOICES_PPU = (
        ('', ugettext_lazy('Payment Period Units')),
        ('Monthly', 'Monthly'),
        ('Quarterly', 'Quarterly'),
        ('Semi-Annually', 'Semi-Annually'),
        ('Annually', 'Annually'),
    )

    CHOICES_DRPU = (
        ('', ugettext_lazy('Deferred Repayment Period Units')),
        ('Monthly', 'Monthly'),
        ('Quarterly', 'Quarterly'),
        ('Semi-Annually', 'Semi-Annually'),
        ('Annually', 'Annually'),
    )
    CHOICES_RPYMT_MTHD = (
        ('', ugettext_lazy('Repayment Method')),
        ('Sur Valeur', 'Sur Valeur'),
        ('Sur Valeur', 'Sur Valeur'),
    )

    CHOICES_RPYMT_TYPE = (
        ('', ugettext_lazy('Repayment Type')),
        ('Fixed rate', 'Fixed rate'),
        ('Variable rate', 'Variaible'),
    )
    CHOICES_USAGE = (
        ('', ugettext_lazy('Usage')),
        ('360', '360'),
        ('365', '365'),
    )
    auth = forms.NullBooleanField(required=False, initial=True, label='', widget=forms.CheckboxInput(attrs={'class':'form-check-input my_checkbox','type':'checkbox'}))
    gr_bnd_int_rate = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':ugettext_lazy('Gross Bond Interest Rate')}))
    net_bnd_int_rate = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':ugettext_lazy('Net Bond Interest Rate')}))
    nbr_shrs_outstg = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':ugettext_lazy('Number Shares Outstanding')}))
    bnd_type = forms.ChoiceField(required=False, choices=CHOICES_BND_TYPE, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Bond Type')}))
    duratn_amt = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Duration')}, ))
    duratn_units = forms.ChoiceField(required=False, choices=CHOICES_DURATN_UNITS, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Duration Units')}))
    pymt_perd = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Payment Period'}, ))
    pymt_perd_units = forms.ChoiceField(required=False, choices=CHOICES_PPU, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Payment Period Units')}))
    dfrrd_rpymt_perd = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Deferred Repayment Period')}, ))
    dfrrd_rpymt_perd_units = forms.ChoiceField(required=False, choices=CHOICES_DRPU, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Deferred Repayment Period Units')}))
    rpymt_mthd = forms.ChoiceField(required=False, choices=CHOICES_RPYMT_MTHD, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Repayment Method'}))
    rpymt_type = forms.ChoiceField(required=False, choices=CHOICES_RPYMT_TYPE, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Repayment Type')}))
    bnd_isu_dt = forms.DateField(required=False, label='', widget=forms.DateInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Bond Issued Date')}))
    first_pay_dt = forms.DateField(required=False, label='', widget=forms.DateInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('First Payment Date')}))
    lst_pay_dt = forms.DateField(required=False, label='', widget=forms.DateInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Last Payment Date')}))
    usage = forms.ChoiceField(required=False, choices=CHOICES_USAGE, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': ugettext_lazy('Usage')}))

    class Meta:
        model = BondModel
        fields = ('auth','gr_bnd_int_rate','net_bnd_int_rate', 'nbr_shrs_outstg','bnd_type','duratn_amt','duratn_units','pymt_perd','pymt_perd_units','dfrrd_rpymt_perd', 'dfrrd_rpymt_perd_units', 'rpymt_mthd', 'rpymt_type', 'bnd_isu_dt', 'first_pay_dt', 'lst_pay_dt', 'usage')





#////////////////////////////////////////////////////////////
class FinancialStatementFactForm(forms.ModelForm):
    value_brut = forms.DecimalField(initial=0.00, max_digits=18, decimal_places=2, label='value_brut', widget=forms.TextInput(attrs={'onBlur':'calc();', 'class': 'form-control form-control-sm', 'placeholder':'0.00'}))

    class Meta:
        model = FinancialStatementFactModel
        fields = ['value_brut']

#///////////////////////////// GuarantorForm /////////////////////////////
class GuarantorForm(forms.ModelForm):
    guarantor = forms.CharField(required=False, max_length=100, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Garant'}, ))
    guarantor_pctg = forms.DecimalField(required=False, max_digits=6, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Garant Pourcentage'}, ))
    guarantor_val = forms.DecimalField(required=False, max_digits=13, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Garant Valeur'}, ))

    class Meta:
        model = GuarantorModel
        fields = ['guarantor', 'guarantor_pctg','guarantor_val']

#///////////////////////////// GuarantorFormset /////////////////////////////
GuarantorFormset = modelformset_factory(GuarantorModel, form=GuarantorForm, extra=1)
GuarantorFormset_edit = modelformset_factory(GuarantorModel, form=GuarantorForm, extra=0, can_delete=True)


# class LanguageForm(forms.ModelForm):
#     #name = forms.ModelChoiceField(queryset=Language.objects.all(), label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder':'Language Name'}))
#     name = forms.CharField(max_length=50, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder':'Language Name'}))
#     #name = forms.CharField(max_length=50, label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sector...'}, ))
#     class Meta:
#         model = Language
#         fields =  ['name']

# class FinancialStatementFact(models.Model):
#     company = models.ForeignKey(Company, on_delete=models.CASCADE)
#     financial_statement_line = models.ForeignKey(FinancialStatementLine, on_delete=models.CASCADE)
#     value = models.DecimalField(max_digits=13, decimal_places=2)
#
#     class Meta:
#         verbose_name_plural ='FinancialStatementFact'

# ugettext_lazy('Sector') # this string will be marked for translation
# from django.core.exceptions import ValidationError

# def validate_id_exists(value):
#    company = CompanyModel.objects.filter(id=value)
#    if not company: # check if any object exists
#        raise ValidationError(f'{company} already exist in this {rpt_period}.')

# class ProductForm(forms.ModelForm):
#      class Meta:
#          model = ProductModel
#          fields = ('prod_name','prod_price')
#
#
# class ProductMetaForm(forms.ModelForm):
#     class Meta:
#         model = ProductMetaModel
#         fields = ('prod_meta_name', 'prod_meta_value')
#
# ProductMetaInlineFormset = inlineformset_factory(
#     ProductModel,
#     ProductMetaModel,
#     form=ProductMetaForm,
#     extra=5,
#     # max_num=5,
#     # fk_name=None,
#     # fields=None, exclude=None, can_order=False,
#     # can_delete=True, max_num=None, formfield_callback=None,
#     # widgets=None, validate_max=False, localized_fields=None,
#     # labels=None, help_texts=None, error_messages=None,
#     # min_num=None, validate_min=False, field_classes=None
# )


from django import forms
from .models import CompanyModel, SectorModel, FinancialStatementModel,  \
    FinancialStatementBalLinkModel, FinancialStatementIncLinkModel, FinancialStatementFactModel, \
    FinancialStatementInvAcctLinkModel, ShareholderModel, AddressModel, LeadersModel, ParentCompanyModel, SubsidiaryModel
from jdaanalyticsapp.models import SecurityModel, StockModel, BondModel, GuarantorModel, ExchangeModel
from django_countries.fields import CountryField, countries, country_to_text
from django.utils.translation import ugettext_lazy
from .utils import merge_two_lists, merge_company_lists
from django.forms import inlineformset_factory
from django.forms import modelformset_factory


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
    shrs_hld = forms.CharField(required=False, max_length=50, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('Shares Held')}, ))

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
    brut_43 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_44 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_45 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_46 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_47 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_48 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_49 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_50 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_51 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_52 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_53 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_54 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_55 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_56 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_57 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    brut_58 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    #brut_59 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))

    amort_0 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder':'0.00'}))
    amort_1 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder':'0.00'}))
    amort_2 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_3 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_4 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_5 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_6 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_7 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_8 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_9 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_10 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_11 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_12 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_13 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_14 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_15 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_16 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_17 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_18 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_19 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_20 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_21 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_22 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_23 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_24 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_25 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_26 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_27 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_28 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_29 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_30 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_31 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_32 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_33 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_34 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_35 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_36 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_37 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_38 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_39 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_40 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_41 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_42 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_43 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_44 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_45 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_46 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_47 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_48 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_49 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_50 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_51 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_52 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_53 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_54 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_55 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_56 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_57 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    amort_58 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    #amort_59 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur': 'calc();', 'class': 'form-control form-control-sm', 'placeholder': '0.00'}))

    net_0 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder':'0.00'}))
    net_1 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder':'0.00'}))
    net_2 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_3 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_4 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_5 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_6 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_7 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_8 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_9 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_10 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_11 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_12 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_13 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_14 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_15 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_16 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_17 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_18 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_19 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_20 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_21 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_22 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_23 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_24 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_25 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_26 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_27 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_28 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_29 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_30 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_31 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_32 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_33 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_34 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_35 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_36 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_37 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_38 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_39 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_40 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_41 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_42 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_43 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_44 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_45 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_46 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_47 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_48 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_49 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_50 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_51 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_52 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_53 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_54 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_55 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_56 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_57 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
    net_58 = forms.DecimalField(max_digits=19, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))
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
        ('','Title Type'),
        ('Listed Share', 'Listed Share'),
        ('Listed Bond', 'Listed Bond'),
        ('Unlisted Share', 'Unlisted Share'),
        ('Unlisted Bond', 'Unlisted Bond'),
    )

    CHOICES_SHR_CLASS = (
        ('','Share Class'),
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
    )

    CHOICES_ISUR_TYPE = (
        ('','Issuer Type'),
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





    CHOICES_SECTOR = (
        ('', 'Activity Sector'),
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
    name = forms.CharField(max_length=200, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Name'}, ))
    ticker =forms.CharField(max_length=12, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Ticker'}, ))
    desc = forms.CharField(max_length=50, label='', widget=forms.TextInput(attrs={'class':'form-control-sm', 'placeholder':'Description'},))
    # isu_dt = forms.DateField(label='', widget=forms.DateInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Issuer Date'}))
    isu_dt =forms.DateField(label='', widget=forms.DateInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Issuer Date'}))
    # open_date = forms.DateField(label='', widget=forms.DateInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Open Date'}))
    open_dt = forms.DateField(label='', widget=forms.DateInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Open Date'}))
    close_dt = forms.DateField(label='', widget=forms.DateInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Close Date'}))
    # close_date = forms.DateField(label='', widget=forms.DateInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Close Date'}))
    listg_sts = forms.ChoiceField(choices=CHOICES_LISTG, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Listing Status'}))
    nmnl_amt = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'Nominal Value'}))
    cntry = CountryField(blank_label='Country').formfield(label='', widget=forms.Select(attrs={'class': 'form-control-sm selector selectpicker show-tick', 'data-live-search=': 'true', 'placeholder':'Country'}))
    # cntry = # forms.ModelChoiceField(queryset=CountryField.objects.all(), empty_label='Country', label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker show-tick my_dropdown', 'data-live-search=': 'true'}))
    currency = forms.CharField(max_length=5, label='', widget=forms.TextInput(attrs={'class':'form-control-sm', 'placeholder':'Currency'},))
    min_lot = forms.IntegerField(label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Lot Minimum'}, ))
    ttl_type = forms.ChoiceField(choices=CHOICES_TITLE_TYPE, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Title Type'}))
    shr_class = forms.ChoiceField(choices=CHOICES_SHR_CLASS, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Share Class'}))
    isur_type = forms.ChoiceField(choices=CHOICES_ISUR_TYPE, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Issuer Type'}))
    # actvy_sector = forms.ChoiceField(choices=CHOICES_SECTOR, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Activity Sector'}))
    sector = forms.ModelChoiceField(queryset=SectorModel.objects.all(), empty_label='Sector', label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker show-tick my_dropdown', 'data-live-search=': 'true'}))
    #issue = forms.ModelChoiceField(queryset=CompanyModel.objects.all(), empty_label='Issue', label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker show-tick my_dropdown', 'data-live-search=': 'true'})) # Drop down values from Exchange table
    issuer = forms.ChoiceField(choices=CHOICES_ISSUE_LIST, label='', widget=forms.Select(attrs={'class': 'form-control-sm selector selectpicker show-tick', 'data-live-search=': 'true', 'placeholder':'Issuer'}))
    rgstrr = forms.ChoiceField(choices=CHOICES_RGSTRR, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Security Status'}))
    exchg  = forms.ModelMultipleChoiceField(queryset=ExchangeModel.objects.all(), label='', widget=forms.SelectMultiple(attrs={'class': 'form-control-sm selectpicker show-tick my_dropdown', 'multiple':'multiple', 'data-live-search=': 'true', 'title':'Exchange'})) # Drop down values from Exchange table
    depsty = forms.ChoiceField(choices=CHOICES_DEPSTY, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Depository'}))
    cntry_tax = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'Country Tax'}))
    invstr_cntry_tax = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'Invstmt Country Tax'}))
    txtn_code = forms.NullBooleanField(initial=True, label='', widget=forms.CheckboxInput(attrs={'class':'form-check-input my_checkbox','type':'checkbox'}))
    exchg_tax = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'Exchange Tax'}))
    val_code = forms.NullBooleanField(initial=True, label='', widget=forms.CheckboxInput(attrs={'class':'form-check-input my_checkbox','type':'checkbox'}))
    lwst_appl_rate = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'Lowest Applied Rate'}))
    hghst_appl_rate = forms.DecimalField(required=False, max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'Highest Applied Rate'}))


    class Meta:
        model = SecurityModel
        fields = '__all__'

# ////////////////////////// StockModelForm /////////////////////////////
class StockModelForm(forms.ModelForm):
    CHOICES_SECR_STS = (
        ('', 'Security Status'),
        ('Listed','Listed'),
        ('Unquoted', 'Unquoted'),
        ('Suspended', 'Suspended'),
        ('Deleted', 'Deleted'),
    )
    stock_type = forms.CharField(required=False, max_length=25, label='', widget=forms.TextInput(attrs={'class':'form-control-sm', 'placeholder':'Stock Type'},))
    under_stock_type  = forms.CharField(required=False, max_length=25, label='', widget=forms.TextInput(attrs={'class':'form-control-sm', 'placeholder':'Under Stock Type'},))
    secr_status = forms.ChoiceField(choices=CHOICES_SECR_STS, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Security Status'}))
    dvdnd = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'Dividend Per Share'}))

    class Meta:
        model = StockModel
        fields = ('stock_type','under_stock_type', 'secr_status','dvdnd')

# ////////////////////////// BondModelForm /////////////////////////////
class BondModelForm(forms.ModelForm):
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
    CHOICES_PPU = (
        ('', 'Payment Period Units'),
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
        ('360', '360'),
        ('365', '365'),
    )
    auth = forms.NullBooleanField(initial=True, label='', widget=forms.CheckboxInput(attrs={'class':'form-check-input my_checkbox','type':'checkbox'}))
    gr_bnd_int_rate = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'Gross Bond Interest Rate'}))
    net_bnd_int_rate = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'Net Bond Interest Rate'}))
    nbr_shrs_outstg = forms.DecimalField(max_digits=19, decimal_places=2,  label='', widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'Number Shares Outstanding'}))
    bnd_type = forms.ChoiceField(choices=CHOICES_BND_TYPE, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Bond Type'}))
    duratn_amt = forms.IntegerField(label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Duration'}, ))
    duratn_units = forms.ChoiceField(choices=CHOICES_DURATN_UNITS, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Duration Units'}))
    pymt_perd = forms.IntegerField(label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Payment Period'}, ))
    pymt_perd_units = forms.ChoiceField(choices=CHOICES_PPU, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Payment Period Units'}))
    dfrrd_rpymt_perd = forms.IntegerField(label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Deferred Repayment Period'}, ))
    dfrrd_rpymt_perd_units = forms.ChoiceField(choices=CHOICES_DRPU, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Deferred Repayment Period Units'}))
    rpymt_mthd = forms.ChoiceField(choices=CHOICES_RPYMT_MTHD, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Repayment Method'}))
    rpymt_type = forms.ChoiceField(choices=CHOICES_RPYMT_TYPE, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Repayment Type'}))
    bnd_isu_dt = forms.DateField(label='', widget=forms.DateInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Bond Issued Date'}))
    first_pay_dt = forms.DateField(label='', widget=forms.DateInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'First Payment Date'}))
    lst_pay_dt = forms.DateField(label='', widget=forms.DateInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Last Payment Date'}))
    usage = forms.ChoiceField(choices=CHOICES_USAGE, label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Usage'}))

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


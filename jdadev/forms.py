from django import forms
from .models import ClientPortfolioModel, ClientProfileModel, ClientEquityAndRightsModel, StockDailyValuesModel, BondModel, InstitutionTypeModel, ClientBondsModel, MutualFundModel, ClientMutualFundsModel, DepositaireModel, SociateDeGessionModel, TransactionFeesModel
#from django.utils.translation import ugettext_lazy
from django.urls import reverse_lazy
from django.forms import modelformset_factory
from django.db.models import Sum
from django.urls import reverse
from django.utils.html import format_html
from decimal import Decimal
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError


def validate_excel(value):
    if value.name.split('.')[-1] not in ['xls', 'xlsx']:
        raise ValidationError(_('Invalid File Type: %(value)s'), params={'value': value},)


class UploadFileForm(forms.Form):
    #excel_file = forms.FileField()
    excel_file = forms.FileField(label='', widget=forms.FileInput(attrs={'class': 'form-control'}), validators=[validate_excel])


#///////////////////////////// ClientPortfolioForm //////////////////////////////////////
class ClientPortfolioForm(forms.ModelForm):
    liquid_assets = forms.DecimalField(required=False, label='', widget=forms.NumberInput(attrs={'class': 'form-control-sm', 'placeholder': 'Liquid Assets'}, ))
    equity_and_rights = forms.DecimalField(required=False, label='', widget=forms.NumberInput(attrs={'class': 'form-control-sm', 'readonly': 'readonly', 'placeholder': 'Equity & Rights', 'onfocus': 'showEquityAndRightsForm()'}))
    bonds = forms.DecimalField(required=False, label='', widget=forms.NumberInput(attrs={'class': 'form-control-sm',  'readonly': 'readonly','placeholder': 'Bonds'}, ))
    mutual_funds = forms.DecimalField(required=False, label='', widget=forms.NumberInput(attrs={'class': 'form-control-sm',  'readonly': 'readonly','placeholder': 'Mutual Funds'}, ))

    class Meta:
        model = ClientPortfolioModel
        fields = ['liquid_assets', 'equity_and_rights','bonds','mutual_funds']


#///////////////////////////// ClientEquityAndRightsForm //////////////////////////////////////
# jdadev/forms.py
#from django import forms
#from .models import ClientEquityAndRightsModel, StockDailyValuesModel

class ClientEquityAndRightsForm(forms.ModelForm):
    stocks = forms.ModelChoiceField(queryset=StockDailyValuesModel.objects.none(), empty_label='Stocks', label='',widget=forms.Select(attrs={'class': 'form-control form-control-sm equity_right_id show-tick'}))
    nbr_of_stocks = forms.IntegerField(label='', widget=forms.TextInput(attrs={'class': 'form-control form-control-sm nbr_of_stocks_id', 'placeholder': 'Number of stocks'}))
    avg_weighted_cost = forms.DecimalField(required=False, max_digits=12, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control form-control-sm tot_purchase_value_id total_gain_or_loss_id', 'placeholder': 'Average Weighted Cost'}))
    daily_value = forms.DecimalField(required=False, max_digits=12, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Daily Value', 'readonly': 'readonly'}))
    total_current_value = forms.DecimalField(required=False, max_digits=12, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Total Current Value', 'readonly': 'readonly'}))
    total_purchase_value = forms.DecimalField(required=False, max_digits=12, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Total Purchase Value', 'readonly': 'readonly'}))
    total_gain_or_loss = forms.DecimalField(required=False, max_digits=12, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Total Gain or Loss', 'readonly': 'readonly'}))

    class Meta:
        model = ClientEquityAndRightsModel
        fields = ['stocks', 'nbr_of_stocks', 'avg_weighted_cost', 'daily_value', 'total_current_value', 'total_purchase_value', 'total_gain_or_loss']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the stocks queryset dynamically based on the latest entry date
        latest_entry_date = StockDailyValuesModel.objects.order_by('-entry_date').values_list('entry_date', flat=True).first()
        if latest_entry_date:
            self.fields['stocks'].queryset = StockDailyValuesModel.objects.filter(entry_date=latest_entry_date)
        else:
            self.fields['stocks'].queryset = StockDailyValuesModel.objects.none()  # Fallback to empty queryset
#///////////////////////////// ClientEquityAndRightsFormset /////////////////////////////
ClientEquityAndRightsFormset = modelformset_factory(ClientEquityAndRightsModel, form=ClientEquityAndRightsForm, extra=1, can_delete=True) #extra=1)
ClientEquityAndRightsFormset_edit = modelformset_factory(ClientEquityAndRightsModel, form=ClientEquityAndRightsForm, extra=0, can_delete=True)


#///////////////////////////// ClientBondsForm //////////////////////////////////////
# class InstitutionTypeModelChoiceField(forms.ModelChoiceField):
#     def label_from_instance(self, obj):
#         return obj.institution_type  # Display the institution_type instead of bond_name
#
# class ClientBondsForm(forms.ModelForm):
#     class InstitutionTypeModelChoiceField(forms.ModelChoiceField):
#         def label_from_instance(self, obj):
#             return obj.institution_type  # Display the institution_type instead of bond_name
#
class BondNameModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.bond_name  # Display the bond_name instead of bond_name
    # Get distinct institution types
distinct_institution_types = BondModel.objects.values_list('institution_type', flat=True).distinct()
institution_type_queryset = BondModel.objects.filter(institution_type__in=distinct_institution_types)

# # Get distinct bond_name
distinct_bond_names = BondModel.objects.values_list('bond_name', flat=True).distinct()
bond_name_queryset = BondModel.objects.filter(bond_name__in=distinct_bond_names)
#///////////////////////////////////////ClientBondsForm//////////////////////////////
class ClientBondsForm(forms.ModelForm):
    institution_type=forms.ModelChoiceField(queryset=InstitutionTypeModel.objects.all().distinct().order_by('inst_type'),
                                            empty_label='Institution Types',
                                            label='',
                                            widget=forms.Select(attrs={'class': 'form-control form-control-sm bonds_institution_type_id show-tick','onchange':'return triggerHtmxGet(id);',}))
    symbol = forms.ModelChoiceField(queryset=BondModel.objects.all(), empty_label='Symbol', label='', widget=forms.Select(attrs={'class': 'form-control form-control-sm bonds_symbol_id show-tick','onchange':'return triggerHtmxGet(id), triggerHtmxGet_original_value(id);',}))
    bond_name = BondNameModelChoiceField(queryset=bond_name_queryset, empty_label=('Bond Names'),label='',widget=forms.Select(attrs={'class': 'form-control form-control-sm Xbonds_institution_type_id show-tick'}))
    nbr_of_shares = forms.IntegerField(required=False, label='', widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'Number of Shares'}))
    coupon = forms.DecimalField(required=False, max_digits=12, decimal_places=4, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm','onblur':'return triggerHtmxGet_bond_coupon(id);', 'placeholder': 'Coupon', 'readonly': 'readonly'}, ))
    original_value = forms.DecimalField(required=False, max_digits=12, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Original Value', 'readonly': 'readonly'}, ))
    current_value = forms.DecimalField(required=False, max_digits=12, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm','onblur':'return triggerHtmxGet_current_value(id);', 'placeholder': 'Current Value', 'readonly': 'readonly'}, ))
    total_current_value = forms.DecimalField(required=False, max_digits=12, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm','onblur':'return get_bond_tot_curr_val(id);',  'placeholder': 'Total Current Value', 'readonly': 'readonly'}, ))
    total_purchase_value = forms.DecimalField(required=False, max_digits=12, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm','onblur':'return get_bond_tot_purchase_val(id);', 'placeholder': 'Total Purchase Value', 'readonly': 'readonly'}, ))
    total_gain_or_loss = forms.DecimalField(required=False, max_digits=12, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm','onclick':'return get_bond_tot_gain_or_loss_val(id);', 'placeholder': 'Total Gain or Loss', 'readonly': 'readonly'},))
    class Meta:
        model = ClientBondsModel
        fields = ['institution_type', 'symbol','bond_name', 'nbr_of_shares','coupon',  'original_value', 'current_value', 'total_current_value', 'total_purchase_value', 'total_gain_or_loss']

#///////////////////////////// ClientBondsFormset /////////////////////////////
ClientBondsFormset = modelformset_factory(ClientBondsModel, form=ClientBondsForm, extra=1, can_delete=True)
ClientBondsFormset_edit = modelformset_factory(ClientBondsModel, form=ClientBondsForm, extra=0, can_delete=True)


#///////////////////////////////////////ClientMutualFundForm//////////////////////////////
from django import forms
from .models import ClientMutualFundsModel, MutualFundModel, SociateDeGessionModel, DepositaireModel

class ClientMutualFundForm(forms.ModelForm):
    sociate_de_gession = forms.ModelChoiceField(
        queryset=SociateDeGessionModel.objects.all().distinct().order_by('sociate_de_gession'),
        empty_label='Societe De Gessions',
        label='',
        widget=forms.Select(attrs={'class': 'form-control form-control-sm show-tick', 'onchange': 'return mu_triggerHtmxGet(id);'})
    )
    depositaire = forms.ModelChoiceField(
        queryset=DepositaireModel.objects.all().distinct().order_by('depositaire'),
        empty_label='Depositaire',
        label='',
        widget=forms.Select(attrs={'class': 'form-control form-control-sm show-tick mu_depositaire_id', 'onchange': 'return mu_triggerHtmxGet(id);'})
    )
    opcvm = forms.ModelChoiceField(
        queryset=MutualFundModel.objects.none(),  # Empty queryset initially
        empty_label='OPCVM',
        label='',
        widget=forms.Select(attrs={'class': 'form-control form-control-sm show-tick', 'onchange': 'mu_triggerHtmxGet(id)'})
    )
    mu_original_value = forms.DecimalField(
        required=False,
        max_digits=12,
        decimal_places=2,
        label='',
        widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Original Value', 'readonly': 'readonly', 'onclick': 'mu_triggerHtmxGet_current_value(id)'})
    )
    mu_current_value = forms.DecimalField(
        required=False,
        max_digits=12,
        decimal_places=2,
        label='',
        widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Current Value', 'readonly': 'readonly', 'onclick': 'mu_triggerHtmxGet_nbr_of_share(id)'})
    )
    mu_nbr_of_share = forms.IntegerField(
        required=False,
        label='',
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Number of Shares', 'onblur': 'mu_triggerHtmxGet_tot_curr_val(id)'})
    )
    mu_total_current_value = forms.DecimalField(
        required=False,
        max_digits=12,
        decimal_places=2,
        label='',
        widget=forms.TextInput(attrs={'class': 'form-control-sm', 'onblur': 'return get_mutual_fund_tot_curr_val(id);', 'placeholder': 'Total Current Value', 'readonly': 'readonly'})
    )
    mu_total_purchase_value = forms.DecimalField(
        required=False,
        max_digits=12,
        decimal_places=2,
        label='',
        widget=forms.TextInput(attrs={'class': 'form-control-sm', 'onblur': 'return get_mutual_fund_tot_purchase_val(id);', 'placeholder': 'Total Purchase Value', 'readonly': 'readonly'})
    )
    mu_total_gain_or_loss = forms.DecimalField(
        required=False,
        max_digits=12,
        decimal_places=2,
        label='',
        widget=forms.TextInput(attrs={'class': 'form-control-sm', 'onclick': 'return get_mutual_fund_tot_gain_or_loss_val(id);', 'placeholder': 'Total Gain or Loss', 'readonly': 'readonly', 'onblur': 'updateColor(this);'})
    )

    class Meta:
        model = ClientMutualFundsModel
        fields = ['sociate_de_gession', 'depositaire', 'opcvm', 'mu_original_value', 'mu_current_value', 'mu_nbr_of_share', 'mu_total_current_value', 'mu_total_purchase_value', 'mu_total_gain_or_loss']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the opcvm queryset dynamically based on the latest entry date
        latest_entry_date = MutualFundModel.objects.order_by('-entry_date').values_list('entry_date', flat=True).first()
        if latest_entry_date:
            self.fields['opcvm'].queryset = MutualFundModel.objects.filter(entry_date=latest_entry_date).distinct().order_by('opcvm')
        else:
            self.fields['opcvm'].queryset = MutualFundModel.objects.none()  # Fallback to empty queryset

#///////////////////////////// ClientMutualFundsFormset /////////////////////////////

ClientMutualFundsFormset = modelformset_factory(ClientMutualFundsModel, form=ClientMutualFundForm, extra=1, can_delete=True)
ClientMutualFundsFormset_edit = modelformset_factory(ClientMutualFundsModel, form=ClientMutualFundForm, extra=0, can_delete=True)


# #/////////////////////////////////////// ClientProfileForm /////////////////////////////
class ClientProfileForm(forms.ModelForm):
    liquid_assets = forms.DecimalField(required=True, max_digits=4, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm centered-input','onblur':'get_custom_profile_per()',  'placeholder': '0.00%'}))
    equity_and_rights = forms.DecimalField(required=True, max_digits=4, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm centered-input', 'onblur':'get_custom_profile_per()','placeholder': '0.00%'}))
    bonds = forms.DecimalField(required=True, max_digits=4, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm centered-input', 'onblur':'get_custom_profile_per()', 'placeholder': '0.00%'}))
    mutual_funds = forms.DecimalField(required=True, max_digits=4, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm centered-input', 'onblur':'get_custom_profile_per()', 'placeholder': '0.00%'}))

    class Meta:
        model = ClientProfileModel
        fields = ['liquid_assets', 'equity_and_rights', 'bonds', 'mutual_funds']


# #/////////////////////////////////////// TransactionFeesForm /////////////////////////////
class TransactionFeesForm(forms.ModelForm):
    commission_sgi = forms.DecimalField(required=True, max_digits=8, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Commission SGI'}))
    tps = forms.DecimalField(required=True, max_digits=8, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'onblur':'get_country_sgi()', 'placeholder': 'TPS'}))
    country_sgi = forms.DecimalField(required=True, max_digits=8, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm',  'placeholder': 'Country SGI', 'readonly': 'readonly'}))
    commission_brvm = forms.DecimalField(required=True, max_digits=8, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Commission BRVM'}))
    commission_dc_br = forms.DecimalField(required=True, max_digits=8, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'onblur':'get_total_commussion()', 'placeholder': 'Commission DC/BR'}))
    total_commission = forms.DecimalField(required=True, max_digits=8, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm',  'placeholder': 'Total Commission', 'readonly': 'readonly'}))
    actual_loss = forms.DecimalField(required=True, max_digits=8, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm',  'placeholder': 'Actual Loss'}))
    potential_loss = forms.DecimalField(required=True, max_digits=8, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm',  'placeholder': 'Potential Loss'}))

    class Meta:
        model = TransactionFeesModel
        fields = ['commission_sgi', 'tps', 'country_sgi', 'commission_brvm', 'commission_dc_br','total_commission','actual_loss','potential_loss']
# #///////////////////////////// GuarantorForm /////////////////////////////
# class GuarantorForm(forms.ModelForm):
#     guarantor = forms.CharField(required=False, max_length=100, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Garant'}, ))
#     guarantor_pctg = forms.DecimalField(required=False, max_digits=6, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Garant Pourcentage'}, ))
#     guarantor_val = forms.DecimalField(required=False, max_digits=13, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Garant Valeur'}, ))
#
#     class Meta:
#         model = GuarantorModel
#         fields = ['guarantor', 'guarantor_pctg','guarantor_val']
#
# #///////////////////////////// GuarantorFormset /////////////////////////////
# GuarantorFormset = modelformset_factory(GuarantorModel, form=GuarantorForm, extra=1)
# GuarantorFormset_edit = modelformset_factory(GuarantorModel, form=GuarantorForm, extra=0, can_delete=True)

#//////////////////////////prototype below this line //////////////////////////
from .models import Client_portfolio, Daily_stock

class Client_portfolio_form(forms.ModelForm):
    class Meta:
        model = Client_portfolio
        fields = ['client', 'stock', 'number_of_stocks', 'total_value']
        widgets = {
            'total_value': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

#////////////// Testing functions //////////////
#from django.forms import modelformset_factory
from .models import Option

class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['name']

OptionFormSet = modelformset_factory(Option, form=OptionForm, extra=1)


# forms.py
from django import forms
from .models import Country, City, CountryCityModel

# class LocationForm(forms.Form):
#     country = forms.ModelChoiceField(queryset=Country.objects.all(), required=True, label='Country')
#     city = forms.ModelChoiceField(queryset=City.objects.none(), required=True, label='City')
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if 'country' in self.data:
#             try:
#                 country_id = int(self.data.get('country'))
#                 self.fields['city'].queryset = City.objects.filter(country_id=country_id).order_by('name')
#             except (ValueError, TypeError):
#                 pass  # invalid input from the client; ignore and fallback to empty City queryset
#
#
#
# class CountryForm(forms.ModelForm):
#     class Meta:
#         model = Country
#         fields = ['name']
#
# class CityForm(forms.ModelForm):
#     class Meta:
#         model = City
#         fields = ['country', 'name']
#         widgets = {
#             'country': forms.Select(attrs={
#                 'hx-get': 'load_cities/',
#                 'hx-target': '#id_city',
#                 'hx-trigger': 'change'})}
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['name'].queryset = City.objects.none()
#
#         if 'country' in self.data:
#             try:
#                 country_id = int(self.data.get('country'))
#                 self.fields['name'].queryset = City.objects.filter(country_id=country_id).order_by('name')
#             except (ValueError, TypeError):
#                 pass  # invalid input from the client; ignore and fallback to empty City queryset
class CountryCityForm(forms.ModelForm):
    country = forms.ModelChoiceField(queryset=Country.objects.all(), empty_label='Country name',label='', widget=forms.Select(attrs={'class': 'form-control', 'hx-get': reverse_lazy('load_cities'),'hx-trigger': 'change', 'hx-target': '#id_city'}))
    city = forms.ModelChoiceField(queryset=City.objects.all(),empty_label='City name',label='',widget=forms.Select(attrs={'class': 'form-controlAmee'}))
    class Meta:
        model = CountryCityModel
        fields = ['country', 'city']


from django import forms
from django.contrib.auth.models import User
from .models import PublicationModel, PublicationCompanyModel
import datetime
from django.utils.translation import ugettext_lazy



#/////////////////////////// PublicationAdminsForm //////////////////////////
class PublicationAdminsForm(forms.ModelForm):
    CATEGORY_CHOICES = (
        ('', ugettext_lazy('Category')),
        ('Models', 'Models'),
        ('Newsletters', 'Newsletters'),
        ('Commentaries', ugettext_lazy('Commentaries')),
        ('Reports', ugettext_lazy('Reports')),
    )

    RESEARCH_TYPE_CHOICES = (
        ('', ugettext_lazy('Type')),
        ('Daily Market Briefing', ugettext_lazy('Daily Market Briefing')),
        ('Research Notes', ugettext_lazy('Research Notes')),
        ('Equity Research', ugettext_lazy('Equity Research')),
        ('Quarterly Results', ugettext_lazy('Quarterly Results')),
        ('Half Year Results', ugettext_lazy('Half Year Results')),
        ('Annual Results', ugettext_lazy('Annual Results')),
        ('Sector Reports', ugettext_lazy('Sector Reports')),
        ('Strategic Reports', ugettext_lazy('Strategic Reports')),
        ('IPO Analysis', ugettext_lazy('IPO Analysis')),
        ('Economic Notes', ugettext_lazy('Economic Notes')),
        ('Annual Shareholder Meeting', ugettext_lazy('Annual Shareholder Meeting')),
        ('Valuation Models', 'Valuation Models'),
        ('Weekly comments', ugettext_lazy('Weekly comments')),
        ('Investor Conference', ugettext_lazy('Investor Conference'))
    )

    LANGUAGE_CHOICES = (
        ('', ugettext_lazy('Language')),
        ('English', ugettext_lazy('English')),
        ('French', ugettext_lazy('French')),
    )

    #auth = PublicationModel.objects.values_list('author__username', flat='True').distinct()
    #queryset = User.objects.filter(username__in=auth)
    queryset = User.objects.filter(groups__name__in=['staffs', 'admins'])

    #initial = datetime.date.today,
    author = forms.ModelChoiceField(queryset=queryset, empty_label=ugettext_lazy('Author'), label='', widget=forms.Select(attrs={'class': 'form-control form-control selectpicker show-tick'}))
    publication_date = forms.DateField(label='', widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Date'}))
    research_category = forms.ChoiceField(choices=CATEGORY_CHOICES, label='', widget=forms.Select(attrs={'class': 'form-control form-control selectpicker show-tick'}))
    research_type = forms.ChoiceField(choices=RESEARCH_TYPE_CHOICES, label='', widget=forms.Select(attrs={'class': 'form-control form-control selectpicker show-tick'}))
    subject = forms.CharField(max_length=50, label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ugettext_lazy('Subject')}, ))
    visible_flag = forms.BooleanField(label='Visible', required=False, disabled=False,widget=forms.widgets.CheckboxInput(attrs={'class': 'checkbox-inline'})),
    publication_desc = forms.CharField(label='', widget=forms.Textarea(attrs={'rows':3, 'class': 'form-control', 'Placeholder':ugettext_lazy('Publication Description')}))
    file_name = forms.FileField(label='', widget=forms.FileInput(attrs={'class': 'form-control-sm'}))
    #company = forms.ModelChoiceField(queryset=PublicationCompanyModel.objects.all(), empty_label='Company', label='', widget=forms.Select(attrs={'class': 'form-control-sm selectpicker show-tick'}))
    company = forms.ModelChoiceField(required = False, queryset=PublicationCompanyModel.objects.all().order_by('company_name'), empty_label=ugettext_lazy('Company'), label='',widget=forms.Select(attrs={'class': 'form-control selectpicker show-tick','data-live-search=': 'true'}))
    pub_language = forms.ChoiceField(required=False, choices=LANGUAGE_CHOICES, label='',widget=forms.Select(attrs={'class': 'form-control selectpicker show-tick'}))
    #research_type = forms.ChoiceField(choices=RESEARCH_TYPE_CHOICES, label='', widget=forms.Select(attrs={'class': 'form-control form-control selectpicker show-tick'}))

    class Meta:
        model = PublicationModel
        fields = '__all__'
        #exclude =['edited_by','publication_date']


#////////////////////////////////// PublicationFilterForm ////////////////////////////
class PublicationFilterForm(forms.ModelForm):
    CATEGORY_CHOICES = (
        ('', ugettext_lazy('Category')),
        ('Models', ugettext_lazy('Models')),
        ('Newsletters', 'Newsletters'),
        ('Commentaries', ugettext_lazy('Commentaries')),
        ('Reports', ugettext_lazy('Reports')),
    )

    RESEARCH_TYPE_CHOICES = (
        ('', ugettext_lazy('Type')),
        ('Daily Market Briefing', ugettext_lazy('Daily Market Briefing')),
        ('Research Notes', ugettext_lazy('Research Notes')),
        ('Equity Research', ugettext_lazy('Equity Research')),
        ('Quarterly Results', ugettext_lazy('Quarterly Results')),
        ('Half Year Results', ugettext_lazy('Half Year Results')),
        ('Annual Results', ugettext_lazy('Annual Results')),
        ('Sector Reports', ugettext_lazy('Sector Reports')),
        ('Strategic Reports', ugettext_lazy('Strategic Reports')),
        ('IPO Analysis', ugettext_lazy('IPO Analysis')),
        ('Economic Notes', ugettext_lazy('Economic Notes')),
        ('Annual Shareholder Meeting', ugettext_lazy('Annual Shareholder Meeting')),
        ('Valuation Models', 'Valuation Models'),
        ('Weekly comments', ugettext_lazy('Weekly comments')),
        ('Investor Conference', ugettext_lazy('Investor Conference'))
    )

    LANGUAGE_CHOICES = (
        ('', ugettext_lazy('Language')),
        ('English', ugettext_lazy('English')),
        ('French', ugettext_lazy('French')),
    )


    auth = PublicationModel.objects.values_list('author__username', flat='True').distinct()
    queryset = User.objects.filter(username__in=auth)

    #queryset = PublicationModel.objects.values('author__username').distinct()
    #queryset = PublicationModel.objects.values_list('author__username', flat='True').distinct()
    author = forms.ModelChoiceField(required=False, queryset=queryset, empty_label=ugettext_lazy('Author'), label='', widget=forms.Select(attrs={'class': 'form-control-sm  show-tick'}))

    from_date = forms.DateField(required=False, label='',widget=forms.DateInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('From Date')}))
    to_date = forms.DateField(required=False, label='', widget=forms.DateInput(attrs={'class': 'form-control-sm', 'placeholder': ugettext_lazy('To Date')}))
    research_category = forms.ChoiceField(required=False, choices=CATEGORY_CHOICES, label='', widget=forms.Select(attrs={'class': 'form-control form-control-sm show-tick'}))
    research_type = forms.ChoiceField(required=False, choices=RESEARCH_TYPE_CHOICES, label='', widget=forms.Select(attrs={'class': 'form-control-sm show-tick'}))
    subject = forms.CharField(required=False, max_length=50, label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}, ))
    #visible_flag = forms.BooleanField(label='Visible', required=False, disabled=False,widget=forms.widgets.CheckboxInput(attrs={'class': 'checkbox-inline'})),
    publication_desc = forms.CharField(required=False, label='', widget=forms.Textarea(attrs={'rows':3, 'class': 'form-control', 'Placeholder':'Publication Description'}))
    company = forms.ModelChoiceField(required=False, queryset=PublicationCompanyModel.objects.all().order_by('company_name'), empty_label=ugettext_lazy('Company'), label='', widget=forms.Select(attrs={'class': 'form-control form-control-sm  show-tick'}))
    file_name = forms.FileField(required=False, label='', widget=forms.FileInput(attrs={'class': 'form-control-sm'}))
    pub_language = forms.ChoiceField(required=False, choices=LANGUAGE_CHOICES, label='',widget=forms.Select(attrs={'class': 'form-control form-control-sm show-tick'}))


    class Meta:
        model = PublicationModel
        fields = '__all__'
        #exclude = ["user"]
        exclude = ['edited_by', 'publication_date']


#/////////////////////////// PublicationCompanyForm //////////////////////////
class PublicationCompanyForm(forms.ModelForm):
    company_name = forms.CharField(max_length=50, label='', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':ugettext_lazy('Company')}))

    class Meta:
        model = PublicationCompanyModel
        fields = ['company_name']



# #/////////////////////////// QuickSearchForm //////////////////////////
# class QuickSearchForm(forms.Form):
#     key_word = forms.CharField(max_length=50, label='', widget=forms.TextInput(attrs={'class':'form-control form-control-sm selectpicker', 'placeholder':'Quick Search...'},))
#
#     def clean(self):
#         cleaned_data = super(QuickSearchForm, self).clean()
#         key_word = cleaned_data.get('key_word')
#
#         if not key_word:
#             raise forms.ValidationError('Please enter search keyword!')

#/////////////////////////// FullSearchForm //////////////////////////
class FullSearchForm(forms.Form):
    CATEGORY_CHOICES = (
        ('', 'Category'),
        ('models', 'Models'),
        ('newsletters', 'Newsletters'),
        ('commentaries', 'Commentaries'),
        ('reports', 'Reports'),
    )

    TYPE_CHOICES = (
        ('', 'Type'),
        ('Valuation Models', 'Valuation Models'),
        ('Daily Market Briefing', 'Daily Market Briefing'),
        ('Weekly comments', 'Weekly comments'),
        ('Quarterly Results', 'Quarterly Results'),
        ('Half Year Results', 'Half Year Results'),
        ('Annual Results', 'Annual Results'),
        ('Annual Shareholder Meeting', 'Annual Shareholder Meeting'),
        ('IPO Analysis', 'IPO Analysis'),
        ('Research Notes', 'Research Notes'),
        ('Sector Reports', 'Sector Reports'),
        ('strategic_reports', 'Strategic Reports'),
        ('Economic Notes', 'Economic Notes'),
        ('Investor Conference', 'Investor Conference')
    )
    #from_date = forms.DateField(initial=datetime.date.today, label='', widget=forms.DateInput(attrs={'class': 'form-control-sm', 'placeholder': 'From'}))
    from_date = forms.DateField(required = False, label='', widget=forms.DateInput(attrs={'class': 'form-control-sm', 'placeholder': 'From'}))
    to_date = forms.DateField(required = False, label='', widget=forms.DateInput(attrs={'class': 'form-control-sm', 'placeholder': 'Date'}))
    author = forms.ModelChoiceField(required = False, queryset=User.objects.all(), empty_label='Author', label='', widget=forms.Select(attrs={'class': 'form-control form-control-sm selectpicker show-tick'}))
    category = forms.ChoiceField(required = False, choices=CATEGORY_CHOICES, label='', widget=forms.Select(attrs={'class': 'form-control form-control-sm selectpicker show-tick'}))
    type = forms.ChoiceField(required = False, choices=TYPE_CHOICES, label='', widget=forms.Select(attrs={'class': 'form-control form-control-sm show-tick'}))

    class Meta:
        model = PublicationModel
        fields = ('from_date', 'to_date', 'author', 'category', 'type')



# class TypeEmptyForm(forms.Form):
#     TYPE_CHOICES = (
#         ('', 'Type'),
#     )
#     type = forms.ChoiceField(choices=TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-control-sm'}))
#
# class TypeModelSearchForm(forms.Form):
#     TYPE_CHOICES = (
#         ('', 'Type'),
#         ('valuation_model', 'Valuation Model'),
#         ('thies', 'Thies'),
#     )
#     type = forms.ChoiceField(choices=TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-control  show-tick'}))
#

"""
class TypeEmptyForm(forms.Form):
    TYPE_CHOICES = (
         ('', 'City'),
    )
    type = forms.ChoiceField(choices=TYPE_CHOICES, widget=forms.Select(
            attrs={'class': 'form-control', 'id': 'jdapublicationapp_ajax_set_type_waiter'}))

"""
#/////////////////////////// TypeEmptyForm //////////////////////////
#class TypeEmptyForm(forms.Form):
#    TYPE_CHOICES = (
#        ('', 'Type'),
#    )
#    type = forms.ChoiceField(choices=TYPE_CHOICES, label='',
#                             widget=forms.Select(attrs={'class': 'form-control form-control-sm selectpicker show-tick', 'id': 'ajax_dropdown_test_waiter'}))


class CountryForm(forms.Form):
    TYPE_CHOICES = (
        ('', 'Country'),
        ('senegal', 'Senegal'),
        ('france', 'france'),
    )
    name = forms.ChoiceField(required = False, choices=TYPE_CHOICES,
                             widget=forms.Select(attrs={'class': 'form-control',
                                                        'onChange':"return jda_ajax('ajax_dropdown_test/'+id_name.value,'ajax_dropdown_test_waiter')"}))

    #class Meta:
    #    model = Country
    #    fields = '__all__'




class CitySenegalForm(forms.Form):
    TYPE_CHOICES = (
        ('', 'City'),
        ('dakar', 'Dakar'),
        ('thies', 'Thies'),
    )
    name = forms.ChoiceField(choices=TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

class CityFranceForm(forms.Form):
    TYPE_CHOICES = (
        ('', 'City'),
        ('paris', 'Paris'),
        ('nice', 'nice'),
    )
    name = forms.ChoiceField(choices=TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

class EmptyForm(forms.Form):
        TYPE_CHOICES = (
            ('', 'City'),
        )
        name = forms.ChoiceField(required = False, choices=TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-control', 'id':'ajax_dropdown_test_waiter'}))

class SimpleForm(forms.Form):
    TYPE_CHOICES = (
        ('', 'Country'),
        ('senegal', 'Senegal'),
        ('france', 'france'),
    )
    name = forms.ChoiceField(required = False, choices=TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

"""
#/////////////////////////// CompanyForm //////////////////////////
class CompanyForm(forms.ModelForm):
    CHOICES = (
        ('','Reporting Period'),
        ('Quarterly', 'Quarterly'),
        ('Semi-annually', 'Semi-Annually'),
        ('Annually', 'Annually'),
    )

    sector = forms.ModelChoiceField(queryset=SectorModel.objects.all(), empty_label='Sector', label='',
                                    widget=forms.Select(attrs={'class': 'form-control selectpicker show-tick',
                                                               'data-live-search=': 'true'}))

    company = forms.CharField(max_length=50, label='', widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Company'},))
    rpt_period = forms.ChoiceField(choices=CHOICES, label='',
                                    widget=forms.Select(attrs={'class': 'form-control selector selectpicker show-tick', 'placeholder':'Sector...'}))
    class Meta:
        model = CompanyModel
        fields = ['company', 'sector', 'rpt_period']


#///////////////////////////// fin_stmt_dash_form //////////////////////////////////////

class FinStmtDashForm(forms.Form):
    CHOICES = (
        ('', 'Statement'),
        ('balance_sheet', 'Balance Sheet'),
        ('income_statement', 'Income Statement'),
    )

    res=(
        ('res', 'res'),
        ('tes', 'tes'),
    )

    sector = forms.ModelChoiceField(queryset=SectorModel.objects.all(), empty_label='Sector', label='',
                                     widget=forms.Select(attrs={'class': 'form-control selectpicker show-tick',
                                                                'data-live-search=': 'true'}))

    company = forms.ModelChoiceField(queryset=CompanyModel.objects.all(), empty_label='Company', label='',
                                     widget=forms.Select(attrs={'class': 'form-control selectpicker show-tick',
                                                                'data-live-search=': 'true'}))

    statement = forms.ChoiceField(choices=CHOICES, label='',
                                  widget=forms.Select(attrs={'class': 'form-control selectpicker show-tick'}))

    date = forms.DateField(label='', widget=forms.DateInput(attrs={'class': 'form-control selectpicker', 'placeholder':'Date'}))
    #date = forms.DateTimeField(input_formats=['%d/%m/%Y'], label='')

    def clean(self):
        cleaned_data = super(FinStmtDashForm, self).clean()
        sector = cleaned_data.get('sector')
        company = cleaned_data.get('company')
        statement = cleaned_data.get('statement')
        date = cleaned_data.get('date')

        if not sector and not company and not statement and not date:
            raise forms.ValidationError('You have to write something!')


#///////////////////////// BalanceSheetForm /////////////////////
class BalanceSheetForm(forms.ModelForm):
    TYPE_CHOICES = (
        ('', 'Type'),
        ('Active', 'Active'),
        ('Passive', 'Passive'),
    )
    bal_type = forms.ChoiceField(choices=TYPE_CHOICES, label='',
                                    widget=forms.Select(attrs={'class': 'form-control form-control-sm selectpicker show-tick'}))
    bal_company = forms.ModelChoiceField(queryset=CompanyModel.objects.all(), empty_label='Company', label='',
                                     widget=forms.Select(attrs={'class': 'form-control form-control-sm selectpicker show-tick',
                                                                'data-live-search=': 'true'}))
    #bal_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control form-control-sm selectpicker'}))
    #bal_date = forms.DateField(label='', widget=forms.DateInput(attrs={'class': 'form-control-sm  selectpicker', 'placeholder':'Date'}))
    bal_date = forms.DateField(label='', widget=forms.DateInput(attrs={'class': 'form-control-sm selectpicker', 'placeholder': 'Date'}))
    bal_item_amt_1 = forms.DecimalField(max_digits=13, decimal_places=2, label='',  widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'0.00'}))
    bal_item_amt_2 = forms.DecimalField(max_digits=13, decimal_places=2, label='', widget=forms.TextInput(attrs={'class': 'form-control  form-control-sm', 'placeholder':'0.00'}))

    class Meta:
        model = BalanceSheetModel
        fields = '__all__'


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

#///////////////////////// BalanceSheetSearchForm /////////////////////
class BalanceSheetSearchForm(forms.ModelForm):
    TYPE_CHOICES = (
        ('', 'Type'),
        ('Active', 'Active'),
        ('Passive', 'Passive'),
    )
    bal_type = forms.ChoiceField(choices=TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    bal_company = forms.ModelChoiceField(queryset=CompanyModel.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    bal_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control'}))

    class Meta:
        model = BalanceSheetModel
        fields =  ['bal_type', 'bal_company', 'bal_date']

   
    def clean_name(self):
        name = self.cleaned_data['name']
        if name is None:
            raise forms.ValidationError("Item name is a required field", code="invalid", )
        if len(name) < 1:
            raise forms.ValidationError("Item name is a required field", code="invalid", )

        return self.cleaned_data['name']
   
    
"""
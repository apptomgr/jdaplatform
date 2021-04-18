from django import forms
from django.contrib.auth.models import User
from .models import Student, Course, TestModel, Author, jdatesterBalanceSheetModel, jdatesterLinkModel, jdatesterCompanyModel
import datetime
from django.core.exceptions import ValidationError


#///////////////////////////  //////////////////////////
class CourseForm(forms.ModelForm):
    name = forms.CharField(max_length=30, label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Course'}, ))
    #student = forms.ModelChoiceField(queryset=Course.objects.all(), label='', widget=forms.widgets.CheckboxInput(attrs={'class': 'form-control', 'placeholder':'Student'})),
    #student = FamilyMemberFormSet = inlineformset_factory(Member, FamilyMember, fields=('name', 'relationship'))


    class Meta:
        model = Course
        fields = '__all__'


#///////////////////////////  //////////////////////////
class TestModelForm(forms.ModelForm):
    x = forms.DecimalField(initial=0.00, max_digits=18, decimal_places=2, label='X', widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'0.00'}))#models.DecimalField(max_digits=13, decimal_places=2)
    y = forms.DecimalField(initial=0.00, max_digits=18, decimal_places=2, label='Y', widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'0.00'}))#models.DecimalField(max_digits=13, decimal_places=2)
    computed = forms.DecimalField(initial=0.00, max_digits=18, decimal_places=2, label='Computed', widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'0.00'}))#models.DecimalField(max_digits=13, decimal_places=2)

    class Meta:
        model = TestModel
        fields = ['x', 'y', 'computed']



class AuthorForm(forms.ModelForm):
    name = forms.CharField(max_length=30)

    class Meta:
        model = Author
        fields = '__all__'



class BalanceSheetForm(forms.ModelForm):
    brut_1 = forms.DecimalField(max_digits=10, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder':'0.00'}))
    brut_2 = forms.DecimalField(max_digits=10, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))

    amort_1 = forms.DecimalField(max_digits=10, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder':'0.00'}))
    amort_2 = forms.DecimalField(max_digits=10, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))

    net_1 = forms.DecimalField(max_digits=10, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder':'0.00'}))
    net_2 = forms.DecimalField(max_digits=10, decimal_places=2, label='', widget=forms.TextInput(attrs={'onBlur':'calc();','class': 'form-control form-control-sm', 'placeholder': '0.00'}))

    class Meta:
        model = jdatesterLinkModel
        fields = ['brut_1', 'brut_2', 'amort_1', 'amort_2','net_1','net_2']



class DashForm(forms.ModelForm):
    PERIODS = (
        ('', 'Reporting Period'),
        ('Q1', 'Quarter 1'),
        ('Q2', '1/2 Year'),
        ('Q3', 'Quarter 3'),
        ('Q4', 'Full Year'),
    )

    company = forms.ModelChoiceField(queryset=jdatesterCompanyModel.objects.all(), empty_label='Company', label='',widget=forms.Select(attrs={'class': 'form-control'}))
    pub_period =forms.ChoiceField(choices=PERIODS, label='', widget=forms.Select(attrs={'class': 'form-control selector selectpicker show-tick', 'placeholder':'Reporting Period'}))


    class Meta:
        model = jdatesterCompanyModel
        fields = ['company', 'pub_period']



    # def clean(self):
    #     cleaned_data = self.cleaned_data
    #
    #     # Find the unique_together fields
    #     field1 = cleaned_data.get('lbl')
    #     field2 = cleaned_data.get('entry_date')
    #
    #     objects = jdatesterBalanceSheetModel.objects.filter( lbl = field1, entry_date = field2)
    #     if objects.count() > 0:
    #         msg = u"This row is not unique"
    #         print(msg)
    #         self._errors["field1"] = self.error_class([msg])
    #         del cleaned_data["field1"]
    #         raise ValidationError(msg)
    #
    #     return cleaned_data
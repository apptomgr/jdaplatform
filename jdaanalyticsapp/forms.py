from django import forms
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from .models import SecurityPriceModel, IndexPriceModel
# from django.forms.models import inlineformset_factory, formset_factory, modelform_factory, modelformset_factory
from .models import Book
from django.forms.models import inlineformset_factory
from .models import Author

def validate_excel(value):
    if value.name.split('.')[-1] not in ['xls', 'xlsx']:
        raise ValidationError(_('Invalid File Type: %(value)s'), params={'value': value},)


class UploadExcelForm(forms.Form):
    excel = forms.FileField(label='', widget=forms.FileInput(attrs={'class': 'form-control'}), validators=[validate_excel])  # Custom validation called here

#
class IndexForm(forms.Form):
     excel = forms.FileField(validators=[validate_excel])  # Custom validation celled here


# ////////////////////////////////// SecurityFilterForm ////////////////////////////
class SecurityFilterForm(forms.ModelForm):
    security_date = forms.ModelChoiceField(queryset=SecurityPriceModel.objects.values_list('security_date', flat=True).distinct(), to_field_name="security_date", empty_label='Date', label='', widget=forms.Select(attrs={'class': 'form-control selectpicker show-tick form-control-sm  show-tick', 'data-live-search=': 'true'}))
    ticker = forms.ModelChoiceField(required=False, queryset=SecurityPriceModel.objects.values_list('security__ticker', flat=True).distinct(), to_field_name="security__ticker", empty_label='Ticker', label='', widget=forms.Select(attrs={'class': 'form-control selectpicker show-tick form-control-sm  show-tick', 'data-live-search=': 'true'}))
    idx = forms.ModelChoiceField(required=False, queryset=IndexPriceModel.objects.values_list('idx', flat=True).distinct(), to_field_name="idx", empty_label='Index', label='', widget=forms.Select(attrs={'class': 'form-control selectpicker show-tick form-control-sm  show-tick', 'data-live-search=': 'true'}))
    class Meta:
        model = SecurityPriceModel
        fields = ['security_date','ticker']

    class Meta:
        model = IndexPriceModel
        fields = ['idx']

# ////////////////////// Misc /////////////////////
class BookForm(forms.ModelForm):
    title = forms.CharField(max_length=100, label='', widget=forms.TextInput(attrs={'class':'form-control-sm', 'placeholder':'Title'},))
    number_of_pages = forms.IntegerField(label='', widget=forms.TextInput(attrs={'class':'form-control-sm', 'placeholder':'No. of Pages'},))
    class Meta:
        model = Book
        fields = ('title','number_of_pages')


BookFormSet = inlineformset_factory(
    Author,
    Book,
    form=BookForm,
    min_num=1,  # minimum number of forms that must be filled in
    extra=0,  # number of empty forms to display
    can_delete=False  # show a checkbox in each form to delete the row
)


from django import forms
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from .models import SecurityPriceModel, IndexPriceModel


def validate_excel(value):
    if value.name.split('.')[-1] not in ['xls', 'xlsx']:
        raise ValidationError(_('Invalid File Type: %(value)s'), params={'value': value},)


class UploadExcelForm(forms.Form):
    excel = forms.FileField(label='', widget=forms.FileInput(attrs={'class': 'form-control'}), validators=[validate_excel])  # Custom validation called here


class IndexForm(forms.Form):
    excel = forms.FileField(validators=[validate_excel])  # Custom validation celled here


# ////////////////////////////////// SecurityFilterForm ////////////////////////////
class SecurityFilterForm(forms.ModelForm):
    security_date = forms.ModelChoiceField(queryset=SecurityPriceModel.objects.values_list('security_date', flat=True).distinct(), to_field_name="security_date", empty_label='Date', label='', widget=forms.Select(attrs={'class': 'form-control selectpicker show-tick form-control-sm  show-tick', 'data-live-search=': 'true'}))
    ticker = forms.ModelChoiceField(required=False, queryset=SecurityPriceModel.objects.values_list('security__ticker', flat=True).distinct(), to_field_name="security__ticker", empty_label='Ticker', label='', widget=forms.Select(attrs={'class': 'form-control selectpicker show-tick form-control-sm  show-tick', 'data-live-search=': 'true'}))
    index = forms.ModelChoiceField(required=False, queryset=IndexPriceModel.objects.values_list('index', flat=True).distinct(), to_field_name="index", empty_label='Index', label='', widget=forms.Select(attrs={'class': 'form-control selectpicker show-tick form-control-sm  show-tick', 'data-live-search=': 'true'}))
    class Meta:
        model = SecurityPriceModel
        fields = ['security_date','ticker']

    class Meta:
        model = IndexPriceModel
        fields = ['index']


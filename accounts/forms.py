from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from django.utils.translation import ugettext_lazy


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(label='', widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder':'Email'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# Create a UserUpdateForm to update username and email
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(label='', widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder':'Email'}))

    class Meta:
        model = User
        fields = ['username', 'email']


# Create a ProfileUpdateForm to update image
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['logo']


# Create AccountAdminForm to update email, profile, logo, and User group
class AccountAdminForm(forms.Form):
    queryset_users = User.objects.all().select_related('profile')
    queryset_emails = User.objects.values_list('email', flat='True').distinct()
    queryset_grp = User.objects.values_list('groups__name', flat='True')

    username = forms.ModelChoiceField(required=True, queryset=queryset_users, empty_label=ugettext_lazy('Username'), label='', widget=forms.Select(attrs={'class': 'form-control selectpicker show-tick','data-live-search=': 'true'}))


class AccountAdminUpdateForm(forms.Form):
    queryset_grp = User.objects.values_list('groups__name', flat='True')
    user = forms.CharField(required=True, max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.CharField(required=True, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    group = forms.ModelChoiceField(required=True, queryset=queryset_grp, empty_label=ugettext_lazy('Group'), label='', widget=forms.Select(attrs={'class': 'form-control selectpicker show-tick','data-live-search=': 'true'}))
    logo = forms.ImageField()

    class Meta:
        model = User
        fields = ['user','email','group', 'logo']

    def __init__(self, data, **kwargs):
        initial = kwargs.get('initial', {})
        data = {**initial, **data}
        super().__init__(data, **kwargs)

    def clean(self):
        cleaned_data = super(AccountAdminUpdateForm, self).clean()
        user = cleaned_data.get('user')
        email = cleaned_data.get('email')
        group = cleaned_data.get('group')
        if not user and not email and not group:
            raise forms.ValidationError('You have to write something!')
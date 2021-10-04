from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from django.utils.translation import ugettext_lazy
from django.contrib.auth.models import Group


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder':'Email'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# Create a UserUpdateForm to update username and email
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder':'Email'}))

    class Meta:
        model = User
        fields = ['username', 'email']



# Create a ProfileUpdateForm to update image
class ProfileUpdateForm(forms.ModelForm):
    #email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    class Meta:
        model = Profile
        fields = ['logo']

# Create a GroupUpdateForm to update group
class GroupUpdateForm(forms.ModelForm):
    queryset_groups = Group.objects.exclude(name='admins').all().order_by('name')
    #email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    name = forms.ModelChoiceField(required=True, queryset=queryset_groups, label='Group', to_field_name='name', empty_label=ugettext_lazy('Group Name'))

    class Meta:
        model = Group
        fields = ['name']

# Create a GroupAddForm to update group
class GroupAddForm(forms.ModelForm):
    name = forms.CharField(label='Group', widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Group'}))
    class Meta:
        model = Group
        fields = ['name']

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
    #group = forms.ModelChoiceField(required=True, queryset=queryset_grp, empty_label=ugettext_lazy('Group'), label='', widget=forms.Select(attrs={'class': 'form-control selectpicker show-tick','data-live-search=': 'true'}))
    group = forms.ModelChoiceField(queryset=Group.objects.all(),required=True)
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



# Create a UserUpdateForm to update username and email
class adminTaskProfileUpdateForm(forms.ModelForm):

    TYPE_CHOICES = (
            ('', 'Country'),
            ('senegal', 'Senegal'),
            ('france', 'france'),
        )
    country = forms.ChoiceField(required=False, choices=TYPE_CHOICES)
    #grp = [('admins', 'Admins'), ('Brokers', 'brokers'), ('Customers', 'customers'),('Staffs', 'staffs'),('Managers', 'managers') ]
    queryset_grp = User.objects.values_list('groups__name', flat='True').distinct()
    username = forms.CharField(required=True, max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.CharField(required=True, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    group = forms.ModelChoiceField(required=True, queryset=queryset_grp, empty_label=ugettext_lazy('Group'), widget=forms.Select(attrs={'class': 'form-control selectpicker show-tick','data-live-search=': 'true'}))
    logo = forms.ImageField()

    class Meta:
        model = User
        fields = ['username','email','group', 'logo']

        # def __init__(self, *args, **kwargs):
        #     super(adminTaskProfileUpdateForm, self).__init__(*args, **kwargs)
        #     self.fields['group'].queryset = adminTaskProfileUpdateForm.objects.all()
        #     #self.fields['group'].queryset = User.objects.values_list('groups__name', flat='True').distinct()
        # def __init__(self, *args, **kwargs):
        #     super(adminTaskProfileUpdateForm, self).__init__(*args, **kwargs)
        #     self.fields['group'].queryset = adminTaskProfileUpdateForm.objects.all()
        #     #self.fields['group'].queryset = CountriesShortcut.objects.all()

    # def __init__(self, data, **kwargs):
    #     initial = kwargs.get('initial', {})
    #     data = {**initial, **data}
    #     super().__init__(data, **kwargs)

    # def clean(self):
    #     cleaned_data = super(AccountAdminUpdateForm, self).clean()
    #     user = cleaned_data.get('user')
    #     email = cleaned_data.get('email')
    #     group = cleaned_data.get('group')
    #     if not user and not email and not group:
    #         raise forms.ValidationError('You have to write something!')
    # #email = forms.EmailField(label='', widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder':'Email'}))
    # grp =Group.objects.all() #.select_related('profile').order_by('groups')
    # #grp = [('admins', 'Admins'), ('Brokers', 'brokers'), ('Customers', 'customers'),('Staffs', 'staffs'),('Managers', 'managers') ]
    # group_name = forms.ModelChoiceField(queryset=grp) #, initial={'group_name': 'customers'}) #forms.ChoiceField(choices = grp)
    #
    # class Meta:
    #     model = User
    #     fields = ['username', 'email', 'group_name']


class UserProfileForm(forms.ModelForm):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'group']

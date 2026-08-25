from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.urls import reverse_lazy
from django.contrib.auth.models import Group


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (existing + ' form-control').strip()

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username is not None and password:
            try:
                candidate = User.objects.get(username=username)
                if not candidate.is_active and candidate.check_password(password):
                    resend_url = reverse_lazy('resend_verification')
                    raise forms.ValidationError(
                        mark_safe(
                            str(_('Your account is not yet verified. Please check your email for the verification link.'))
                            + f' <a href="{resend_url}">' + str(_('Resend verification email')) + '</a>'
                        ),
                        code='inactive',
                    )
            except User.DoesNotExist:
                pass
        return super().clean()


class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True, label=_("First Name"),
        widget=forms.TextInput(attrs={'placeholder': _('First Name')}))
    last_name = forms.CharField(max_length=150, required=True, label=_("Last Name"),
        widget=forms.TextInput(attrs={'placeholder': _('Last Name')}))
    phone_number = forms.CharField(max_length=20, required=False, label=_("Phone Number"),
        widget=forms.TextInput(attrs={'placeholder': _('Phone Number')}))
    email = forms.EmailField(required=True, label=_('Email'),
        widget=forms.EmailInput(attrs={'placeholder': _('Email')}))
    terms_accepted = forms.BooleanField(
        required=True,
        label=_('I have read and accept the Terms and Conditions'),
        error_messages={'required': _('You must accept the Terms and Conditions to register.')},
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number',
                  'email', 'username', 'password1', 'password2']


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
    name = forms.ModelChoiceField(required=True, queryset=queryset_groups, label='Group', to_field_name='name', empty_label='Group Name')

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

    username = forms.ModelChoiceField(required=True, queryset=queryset_users, empty_label='Username', label='', widget=forms.Select(attrs={'class': 'form-control selectpicker show-tick','data-live-search=': 'true'}))


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
    group = forms.ModelChoiceField(required=True, queryset=queryset_grp, empty_label='Group', widget=forms.Select(attrs={'class': 'form-control selectpicker show-tick','data-live-search=': 'true'}))
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

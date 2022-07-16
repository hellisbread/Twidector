from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator

class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(label=_('Username'),
                                widget=(forms.TextInput(attrs={'class': 'form-control'})),
                                help_text=_('Enter a username'))
    password1 = forms.CharField(label=_('Password'),
                                widget=(forms.PasswordInput(attrs={'class': 'form-control'})),
                                help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label=_('Re-enter Password'), 
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                                help_text=_('Enter the same password to confirm'))
    email = forms.EmailField(max_length=50, help_text='Required. Inform a valid email address.',
                            widget=(forms.TextInput(attrs={'class': 'form-control'})))

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'email')
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.forms import AuthenticationForm

#from .models import CustomTwidectorUser
#from django.contrib.auth import get_user_model
#User = get_user_model()
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate

from django.forms import ModelForm
from django.core.exceptions import ValidationError

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

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists!")
        return email    

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise ValidationError("A user with this username already exists!")
        return username    

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'email')
        #abstract = True

class UserLoginForm(forms.Form):
    username = forms.CharField(label=_('Username'),
                                widget=(forms.TextInput(attrs={'class': 'form-control'})),
                                help_text=_('Enter a username'),
                                required=True)
    password = forms.CharField(label=_('Password'),
                                widget=(forms.PasswordInput(attrs={'class': 'form-control'})),
                                help_text=password_validation.password_validators_help_text_html(),
                                required=True)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user or not user.is_active:
            raise forms.ValidationError("Invalid login. Please try again.")
        return self.cleaned_data

    def login(self, request):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        return user







# class UserResetPasswordForm(auth_views.PasswordResetView):

#     email = forms.EmailField(max_length=50, help_text='Required. Inform a valid email address.',
#                             widget=(forms.TextInput(attrs={'class': 'form-control'})))

#     class Meta:
#         model = User
#         fields = ('email')
        

# #class tempForm(UserCreationForm):
#     password = None
    
#     def __init__(self, *args, **kargs):
#         super(UserResetPasswordForm, self).__init__(*args, **kargs)
#         self.fields['password1'].required = False
#         self.fields['password2'].required = False
#         del self.fields['password1']
#         del self.fields['password2']



class user_info(ModelForm):
        class Meta:
            model = User
            fields = ('username', 'email')
            labels = {
                'username' : 'Username',
                'email' : 'Email',
            }
            widget = {
                'username' : forms.TextInput(attrs={'class': 'form-control'}),
                'email': forms.TextInput(attrs={'class': 'form-control'})
            }
     
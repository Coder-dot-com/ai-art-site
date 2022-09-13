import re
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from django.contrib.auth.forms import SetPasswordForm


non_allowed_usernames = ['admin', 'administrator', 'mod', 'moderator', 'owner', 'manager']
User = get_user_model()

class RegisterForm(forms.Form):

    email = forms.EmailField(
        widget=forms.TextInput(
            attrs= {
                "class": "form-control",
                'id': 'email',
                'name': 'email',
                'type': 'email',
                'placeholder': "Enter your email",
                'field_title': 'Email',
                'icon': 'bx bx-user',

            }
        
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs= {
                "class": "form-control",
                "id": "password",
                'type': "password",
                'name': 'password',
                'placeholder': 'Add your password',
                'field_title': 'Password (min 12 chars)',
                'icon': 'bx bxs-lock-alt',


            }
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs= {
                "class": "form-control",
                "id": "password2",
                'type': "password",
                'name': 'password2',
                'placeholder': 'Confirm your password',
                'field_title': 'Confirm password',
                'icon': 'bx bxs-lock-alt',


            }
        )
    )

    promo_consent = forms.BooleanField(required=False,
        widget=forms.CheckboxInput(
            attrs= {
                'id': 'promo_consent',
                'name': 'promo_consent',
                'type': 'checkbox',
                'description': 'Check to receive news, updates and offers',
                'checked': 'Yes',
                'is_checkbox': "checkbox",

            }
    )
    )

    def clean_username(self):
        username = self.cleaned_data.get("username")
        qs = User.objects.filter(username__iexact=username)
        if qs.exists() or username in non_allowed_usernames:
            raise forms.ValidationError("Username has already been taken")
        elif not bool(re.match('^[a-zA-Z0-9]+$', username)):
            raise forms.ValidationError("Username contains invalid characters")
  
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        qs = User.objects.filter(email=email)
        if qs.exists() or email in non_allowed_usernames:
            raise forms.ValidationError("Email has already been taken")
        return email

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")        
        if password != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    # def clean_password(self):
    #     password = self.cleaned_data.get("password")
    #     try:
    #          validate_password(password)
    #     except forms.ValidationError as error:
    #         raise forms.ValidationError("Password doesn't meet requirements")
    #     return password

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if len(password) < 12:
            raise forms.ValidationError("Password doesn't meet requirements")
        return password




class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs= {
                'class': 'form-field',
                'id': 'name',
                'name': 'email',
                'type': 'email',
                'placeholder': "Enter your email address",
                'field_title': 'Email address',
                'class': 'form-control',
                'icon': 'bx bx-user',

            }
        
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs= {
                "class": "form-field",
                "id": "password",
                'type': "password",
                'name': 'password',
                'field_title': 'Password',
                'class': 'form-control',
                'icon': 'bx bxs-lock-alt',


            }
        )
    )

    # def clean(self):
    #     username = self.cleaned_data.get("username")
    #     password = self.cleaned_data.get("password")
        

    # def clean_username(self):
    #     username = self.cleaned_data.get("username")
    #     qs = User.objects.filter(Q(username__iexact=username) | Q(email__iexact=username))
    #     if not qs.exists() and username not in non_allowed_usernames:
    #         raise forms.ValidationError("Invalid username or email")
    #     return username

class ResetForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs= {
                'class': 'form-field',
                'id': 'name',
                'name': 'email',
                'type': 'email',
                'placeholder': "Enter your email address",
                'field_title': 'Email address',
                'class': 'form-control',
                'icon': 'bx bx-user',

            }
        
        )
    )


    def clean_username(self):
        username = self.cleaned_data.get("username")
        qs = User.objects.filter(Q(username__iexact=username) | Q(email__iexact=username))
        # if not qs.exists() and username not in non_allowed_usernames:
            # raise forms.ValidationError(" ")
        return username



class ChangePasswordForm(forms.Form):

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs= {
                "class": "form-control",
                "id": "password",
                'type': "password",
                'name': 'password',
                'field_title': 'New password (min 12 chars)',
                'icon': 'bx bxs-lock-alt',
                'minlength': 12,

            }
        )
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs= {
                "class": "form-control",
                "id": "password2",
                'type': "password",
                'name': 'password2',
                'placeholder': 'Confirm your password',
                'field_title': 'Confirm password',
                'icon': 'bx bxs-lock-alt',
                'minlength': 12,

            }
        )
    )


    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")        
        if password != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    # def clean_password(self):
    #     password = self.cleaned_data.get("password")
    #     try:
    #          validate_password(password)
    #     except forms.ValidationError as error:
    #         raise forms.ValidationError("Password doesn't meet requirements")
    #     return password
    def clean_password(self):
        password = self.cleaned_data.get("password")

        if len(password) < 12:
            raise forms.ValidationError("Please ensure password is atleast 12 chars")
        return password
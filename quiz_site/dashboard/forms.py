from django import forms
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class AccountDetailsForm(forms.Form):

    email = forms.EmailField(required=False,
        widget=forms.EmailInput(
        attrs = {
            'class': 'form-control',
            'id': 'email',
            'name': 'email',
            'title': "Change your email here",
            'placeholder': 'Enter new email here',
            'maxlength': 500,
            'error_message': 'Invalid email or email may have already been taken',
            
        }
    )
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        
        qs = UserModel.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("Email has already been taken")
        return email


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(required=True,
        widget=forms.PasswordInput(
        attrs = {
            'class': 'form-control',
            'id': 'current_password',
            'name': 'current_password',
            'title': "Enter your current password*",
            'required': 'required',
            
        }
    )
    )


    new_password = forms.CharField(required=True,
        widget=forms.PasswordInput(
        attrs = {
            'class': 'form-control',
            'id': 'new_password',
            'name': 'new_password',
            'title': "Add a new password (min 12 chars)*",
            'required': 'required',
            'minlength': 12,
            
        }
    )
    )
    def clean_new_password(self):
        password = self.cleaned_data.get("new_password")
        if len(password) < 12:
            raise forms.ValidationError("Password isn't long enough")
        return password
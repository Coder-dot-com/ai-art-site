from django import forms
from .models import UserEmail




class EmailForm(forms.Form):
    email = forms.CharField(
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

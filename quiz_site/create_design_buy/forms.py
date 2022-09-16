import os
from uuid import uuid4
from django import forms

from .models import ShippingOption


class ShippingForm(forms.Form):
    shipping = forms.ModelChoiceField(required=True, queryset=ShippingOption.objects.all(),
    widget=forms.Select(
            attrs= {
                'class': 'form-control',
                'id': 'shipping',
                'name': 'shipping',
                'type': 'text',
                'placeholder': "Select your shipping option",
                'field_title': "Select your shipping option",
                'error_message': 'Please check your shipping option',
                'maxlength': 50,
            }
        )
    )

    first_name = forms.CharField(required=True,
    widget=forms.TextInput(
            attrs= {
                'class': 'form-control',
                'id': 'first_name',
                'name': 'first_name',
                'type': 'text',
                'placeholder': "Enter first name",
                'field_title': "Enter recipient's name",
                'error_message': 'Please check first name',
                'maxlength': 200,
                'col_width': 'col-md-6',
            }
        )
    )


    last_name = forms.CharField(required=True,
    widget=forms.TextInput(
            attrs= {
                'class': 'form-control',
                'id': 'last_name',
                'name': 'last_name',
                'type': 'text',
                'field_title': "Last name",
                'placeholder': "Enter recipient's last name",
                'error_message': 'Please check last name',
                'maxlength': 200,
                'col_width': 'col-md-6',
            }
        )
    )

    address_line_1 = forms.CharField(required=True,
    widget=forms.TextInput(
            attrs= {
                'class': 'form-control',
                'id': 'address_line_1',
                'name': 'address_line_1',
                'type': 'text',
                'placeholder': "Address line 1",
                'field_title': "Enter recipient's address",
                'error_message': 'Please check address',
                'maxlength': 200,
            }
        )
    )
    

    address_line_2 = forms.CharField(required=False,
    widget=forms.TextInput(
            attrs= {
                'class': 'form-control',
                'id': 'address_line_2',
                'name': 'address_line_2',
                'type': 'text',
                'placeholder': "Address line 2 (optional)",
                'error_message': 'Please check address',
                'maxlength': 200,
            }
        )
    )
    

    country = forms.CharField(required=True,
    widget=forms.TextInput(
            attrs= {
                'class': 'form-control',
                'id': 'country',
                'name': 'country',
                'type': 'text',
                'placeholder': "Enter country",
                'error_message': 'Please check country',
                'maxlength': 200,
                'col_width': 'col-md-6',
            }
        )
    )

    state_county = forms.CharField(required=True,
    widget=forms.TextInput(
            attrs= {
                'class': 'form-control',
                'id': 'state_county',
                'name': 'state_county',
                'type': 'text',
                'placeholder': "Enter state or county",
                'error_message': 'Please check state or county',
                'maxlength': 200,
                'col_width': 'col-md-6',
            }
        )
    )


    city = forms.CharField(required=True,
    widget=forms.TextInput(
            attrs= {
                'class': 'form-control',
                'id': 'city',
                'name': 'city',
                'type': 'text',
                'placeholder': "Enter city",
                'error_message': 'Please check city',
                'maxlength': 200,
                'col_width': 'col-md-6',
            }
        )
    )

    postcode_zip = forms.CharField(required=True,
    widget=forms.TextInput(
            attrs= {
                'class': 'form-control',
                'id': 'postcode_zip',
                'name': 'postcode_zip',
                'type': 'text',
                'placeholder': "Enter ZIP code or Postcode",
                'error_message': 'Please check ZIP code or Postcode',
                'maxlength': 200,
                'col_width': 'col-md-6',
            }
        )
    )

    order_number = forms.CharField(
    widget=forms.TextInput(
            attrs= {
                'class': 'form-control visually-hidden',
                'hidden': True,
                'name': 'order_number',
            }
        
        )
    )

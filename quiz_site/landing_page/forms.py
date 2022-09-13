from django import forms

from emails.models import UserEmail

class EmailForm(forms.Form):
    email = forms.CharField(
        widget=forms.TextInput(
            attrs= {
                'class': 'form-field',
                'id': 'name',
                'name': 'email',
                'type': 'email',
                'placeholder': "Add your email address",
                'field_title': 'Email address',
                'class': 'form-control',

            }
        
        )
    )


    def clean_email(self):
        non_allowed_emails = ""
        email = self.cleaned_data.get("email")
        qs = UserEmail.objects.filter(email=email)
        if qs.exists() or email in non_allowed_emails:
            raise forms.ValidationError("Email has already been taken")
        return email
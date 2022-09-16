import os
from uuid import uuid4
from django import forms
from .models import Effect

orientation_choices = [
    ("Landscape", "Landscape"),
    ("Portrait", "Portrait"),
    ("Square", "Square"),
]



effect_choices = [
    ("Landscape", "Landscape"),
    ("Portrait", "Portrait"),
    ("Square", "Square"),
]

class CreateDesignForm(forms.Form):
    orientation = forms.CharField(required=True,
        widget=forms.Select(
            choices=orientation_choices,
            attrs= {
                'class': 'form-control',
                'id': 'orientation',
                'name': 'orientation',
                'type': 'text',
                'placeholder': "Select your orientation",
                'field_title': 'Select your design orientation',
                'error_message': 'Please check your orientation',
                'maxlength': 50,

            }
        
        )
    )



    image = forms.ImageField(required=True,
        widget=forms.ClearableFileInput(
        attrs = {
            'class': 'form-control',
            'id': 'image',
            'name': 'image',
            'field_title': 'Add your image',
            'field_description': 'By uploading you agree to let us your image to create personalized gift ideas',

        }
    )
    )

    effect = forms.ModelChoiceField(required=True, queryset=Effect.objects.filter(active=True),
        widget=forms.Select(
            attrs= {
                'class': 'form-control',
                'id': 'effect',
                'name': 'effect',
                'type': 'text',
                'placeholder': "Select your effect",
                'field_title': 'Select your effect',
                'error_message': 'Please check your effect',
                'maxlength': 500,

            }
        
        )
    )

    

    email = forms.EmailField(required=True,
        widget=forms.TextInput(
            attrs= {
                'class': 'form-control',
                'id': 'message_email',
                'name': 'email',
                'type': 'email',
                'placeholder': "Enter your email",
                'field_title': 'Email',
                'required': 'required',
                'error_message': 'Please check your email',

            }
        
        )
    )

    email_consent = forms.BooleanField(required=False,
        widget=forms.CheckboxInput(
            attrs= {
                'class': "form-check-input",
                'id': 'email_consent_message',
                'name': 'email_consent_message',
                'type': 'checkbox',
                'field_title': '',
                'field_description': 'Check to recieve updates, reminders, offers and personalized gift ideas',
                'checked': 'Yes',

            }
        
        
    )
    )

    def clean_image(self):
        print("image")
        image = self.cleaned_data.get("image")
        try:
            if image:
                print(image.size) #Returns file size in bytes
                if image.size < 20000000 and image.size > 100:
                    file_name = image.name
                    file_ext = os.path.splitext(file_name)[1]
                    if file_ext == '.jpeg':
                        file_ext = '.jpg'
                    image.name = f"{uuid4()}.{file_ext}"
                    print(image.name)
                    print("image valid")

        except Exception as e:
            print(e)
            raise forms.ValidationError("Error")
        return image



buy_choices = [
    ("Canvas", "Canvas"),
    ("Print", "Print"),
    ("Digital", "Digital")
]

class BuyForm(forms.Form):
    type = forms.CharField(required=True,
    widget=forms.Select(
            choices=buy_choices,
            attrs= {
                'class': 'form-control',
                'id': 'type',
                'name': 'type',
                'type': 'text',
                'placeholder': "Select your purchase option",
                'field_title': "Select your purchase option",
                'error_message': 'Please check your purchase option',
                'maxlength': 50,

            }
        
        )
    )

    design_id = forms.CharField(
    widget=forms.TextInput(
            attrs= {
                'class': 'form-control visually-hidden',
                'hidden': True,
                'name': 'design_id',
            }
        
        )
    )

    

    email = forms.EmailField(required=True,
        widget=forms.TextInput(
            attrs= {
                'class': 'form-control',
                'id': 'message_email',
                'name': 'email',
                'type': 'email',
                'placeholder': "Enter your email",
                'field_title': 'Email',
                'required': 'required',
                'error_message': 'Please check your email',
            }
        )
    )

    email_consent = forms.BooleanField(required=False,
        widget=forms.CheckboxInput(
            attrs= {
                'class': "form-check-input",
                'id': 'email_consent_message',
                'name': 'email_consent_message',
                'type': 'checkbox',
                'field_title': '',
                'field_description': 'Check to recieve updates, reminders, offers and personalized gift ideas',
                'checked': 'Yes',

            }   
    )
    )


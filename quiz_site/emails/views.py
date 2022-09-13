from django.shortcuts import redirect, render

from .tasks import API_KEY

from .models import UserEmail
from .forms import EmailForm
import requests
from django.contrib import messages
# Create your views here.



def unsubscribe(request):
    if request.method == "POST":
        print(request.POST)
        form = EmailForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            email = form.cleaned_data["email"]
            email_object = UserEmail.objects.filter(email=email)
            email_object.update(promo_consent=False)

            #Return message of successfully unsubscribed and also unsubscribe from sendinblue

            try:
                identifier = email
                url = f"https://api.sendinblue.com/v3/contacts/{identifier}"

                headers = {
                    "Accept": "application/json",
                    "api-key": API_KEY,
                }

                response = requests.request("GET", url, headers=headers)

                print(response.json())
                print(response.json()["id"])
                contact_id = response.json()['id']
                
                url = f"https://api.sendinblue.com/v3/contacts/{contact_id}"

                response = requests.request("DELETE", url, headers=headers)

                print(response.text)
                messages.success(request, "Email successfully unsubscribed from the list")
                return redirect('home')               
            except Exception as e:
                print(e)
                messages.error(request, "Error failed to unsubscribe email from the list")
                return redirect('unsubscribe')

    else:
        form = EmailForm()
        context = {'form': form}
        return render(request, 'home_site/unsubscribe.html', context=context)
from quiz_site.celery import app
from decouple import config
import requests

API_KEY = config('SENDBLUE_API_SECRET')
SENDER_SITE_EMAIL = config('SITE_EMAIL')

@app.task
def sync_email_with_sendinblue(email):


        ##ATTEMPT TO GET CONTACT FIRST ##
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
            

        #If fails then Create new contact        
        except:
            url = "https://api.sendinblue.com/v3/contacts"

            payload = {
                "attributes": {
                    # "LATEST_PREVIEW_IMAGE": preview_url,

                },
                "updateEnabled": False,
                "email": email,
            }

            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "api-key": API_KEY,
            }

            response = requests.request("POST", url, json=payload, headers=headers)
            response.raise_for_status()
            print(response.json())
            contact_id = response.json()['id']        
            ## END POST CONTACT
        
        print(f"Sendinblue contact created id: {contact_id}")
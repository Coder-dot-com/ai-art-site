import requests
import time

endpoint = "https://api.replicate.com/v1/predictions"

headers = {
        'Authorization': 'Token ',
        'Content-Type': 'application/json'
    }

data = {
    "version": "a9758cbfbd5f3c2094457d996681af52552901775aa2d6dd0b17fd15df959bef", 
    "input": {
        "prompt": "fire",
        "width": 1024,
        "height": 768,
        "init_image": "https://replicate.com/api/models/stability-ai/stable-diffusion/files/8d6a8069-b91f-4e61-8136-fa7c0775532c/out-0.png",
        'prompt_strength': 0.45,

        }
}

response = requests.post(endpoint, headers=headers, json=data)

print("Status Code", response.status_code)
print("JSON Response ", response.json())
url = response.json()['urls']['get']


def get_status_of_creation(url):
    response = requests.get(url, headers=headers)
    try:
        image_url = (response.json()['output'][0])
        print(response)
        print(image_url)
    except Exception as e:
        status = response.json()['status']
        if status == 'starting' or status =='processing':
            time.sleep(1)
            get_status_of_creation(url)
        elif status == 'failed':
            print("Failed creation")


get_status_of_creation(url)






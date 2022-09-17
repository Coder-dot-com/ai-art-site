import os
import random
from tempfile import NamedTemporaryFile
from uuid import uuid4
from quiz_site.celery import app
from decouple import config
import requests
import time
from django.core.files import File
import boto3
from PIL import Image, ImageDraw, ImageFont
from django.contrib.sites.models import Site

from create_design.models import CreateDesignRequest
from quiz_site.settings import AWS_STORAGE_BUCKET_NAME, BASE_DIR

API_KEY = config('SENDBLUE_API_SECRET')
SENDER_SITE_EMAIL = config('SITE_EMAIL')

@app.task
def create_design_task(design_request_id): 
    design_request = CreateDesignRequest.objects.get(unique_id=design_request_id)

    key = config('REPLICATE_API_KEY')
    endpoint = "https://api.replicate.com/v1/predictions"
    headers = {
            'Authorization': f'Token {key}',
            'Content-Type': 'application/json'
        }

    # Populate data using user inputs
    if design_request.orientation =="Square":
        width = 768
        height = 768
    elif design_request.orientation =="Portrait":
        width=1024
        height=768
    elif design_request.orientation =="Landscape":
        width=768
        height=1024


    data = {
        "version": "a9758cbfbd5f3c2094457d996681af52552901775aa2d6dd0b17fd15df959bef", 
        "input": {
            "prompt": design_request.effect.prompt,
            "width": width,
            "height": height,
            "init_image": f"{design_request.image.url}", #need to apss in image
            'prompt_strength': {{{design_request.effect.prompt_strength}}},
            }
    }

    response = requests.post(endpoint, headers=headers, json=data)

    print("Status Code", response.status_code)
    print("JSON Response ", response.json())
    url = response.json()['urls']['get']


    def get_status_of_creation(url):
        attempts = 0
        while attempts < 20:
            response = requests.get(url, headers=headers)
            try:
                image_url = (response.json()['output'][0])
                print(response)
                print(image_url)
                return(image_url)
            except Exception as e:
                status = response.json()['status']
                if status == 'starting' or status =='processing':
                    time.sleep(2)
                    get_status_of_creation(url)
                elif status == 'failed':
                    print("Failed creation")


    design_request.status = "created"

    design_url = get_status_of_creation(url)
    # design_url = "https://alt-img-site.s3.amazonaws.com/created_designs/4ba6940d-94a8-4864-9e28-893e026603b3.jpg"
    #Here use save from url trick

    r = requests.get(design_url, stream=True)
    
    img_temp = NamedTemporaryFile(delete=True)
    img_temp.write(r.content)
    img_temp.flush()

    design_request.created_design.save(f"{uuid4()}.jpg", File(img_temp))
    design_request.save()
    
    print((design_request.created_design.name))
    
    def clean_created_design_download(file_s3_key):

        #download cleaned image from s3
        s3 = boto3.client('s3', aws_access_key_id=config('AWS_ACCESS_KEY_ID'), aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'))
        # No need for env path with base_dir
        file_name = str(((str(file_s3_key)).split("/"))[-1])
        
        if str(BASE_DIR) == "/APP/quiz_site":
            download_path = f"/django/quiz_site/media/tmp/{file_name}"
        else:       
            download_path = f"{BASE_DIR}/media/tmp/{file_name}"
        
        def _download_from_s3():
            print(os.path.abspath(__file__))
            print("download path is", download_path)
            s3.download_file(f'{AWS_STORAGE_BUCKET_NAME}-resized', file_s3_key , download_path)

            if os.path.exists(download_path):
                pass
            else:
                try:
                    _download_from_s3()
                except:
                    print("S3 download failed")
                    print("waiting 3 seconds")
                    time.sleep(3)
                    print("retrying s3 download")
                    _download_from_s3()

        attempts = 0
        while attempts < 10:
            try:
                _download_from_s3()
                break
            except Exception as e:
                print(e)
                print(attempts)
                time.sleep(2)
                attempts +=1
        

        return download_path
    
    download_path = clean_created_design_download(design_request.created_design.name)
    create_preview.delay(design_request_id=design_request.id, download_path=download_path)

@app.task
def create_preview(design_request_id, download_path):
    design_request = CreateDesignRequest.objects.get(id=design_request_id)
    download_path = download_path

    #Open image add watermark
    #Then delete img

    def add_watermark(input, preview_output):
        img = Image.open(input)

        #Opening Image & Creating New Text Layer
        img = Image.open(input).convert("RGBA")
        txt = Image.new('RGBA', img.size, (255,255,255,0))

        #Creating Text
        text = f"{Site.objects.get_current().domain}"
        font = ImageFont.truetype('quiz_site/static/site/assets/fonts/jamie_woods_bold.otf' , 140)

        #Creating Draw Object
        draw = ImageDraw.Draw(txt)

        #Positioning of Text
        width, height = img.size 
        # textwidth, textheight = d.textsize(text, font)
        # x=width/2-textwidth/2
        # y=height-textheight-300

        # Loop for Multiple Watermarks
        y=200
        for i in range(10):
            x=random.randint(0, width-300)
            y+=random.randrange(0,int(height/8), 19)+random.randint(0,100)
            draw.text((x,y), text, fill=(255,255,255, 50), font=font)

        #Combining both layers and saving new image
        watermarked = Image.alpha_composite(img, txt)
        watermarked = watermarked.convert('RGB')
        watermarked.save(preview_output)

    add_watermark(download_path, download_path)
    image = open(download_path, 'rb')

    design_request.design_preview.save(f"{uuid4}.jpg", File(image)) 
    design_request.save()
    
    os.remove(download_path)

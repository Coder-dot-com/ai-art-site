#!/bin/bash

set -e



yes | python manage.py makemigrations
yes | python manage.py migrate 

cd ..



git add . 
git commit -m "deploy"
git push

cd quiz_site

sudo ssh -i "/home/user/Documents/DeployKey06.02.pem" ubuntu@ec2-54-219-102-210.us-west-1.compute.amazonaws.com  'cd quiz-site-template && git pull && sudo docker-compose  -f docker-compose-deploy.yml build && sudo docker-compose  -f docker-compose-deploy.yml down && sudo docker-compose  -f docker-compose-deploy.yml kill && sudo docker-compose  -f docker-compose-deploy.yml down && sudo docker-compose  -f docker-compose-deploy.yml up -d'




mv "db.sqlite3" "1db.sqlite3"
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete

yes | python manage.py makemigrations
yes | python manage.py migrate 


rm "db.sqlite3"
mv "1db.sqlite3" "db.sqlite3"

git add . 
git commit -m "flatten migrations"
git push
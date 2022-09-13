#!/bin/bash

set -e

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

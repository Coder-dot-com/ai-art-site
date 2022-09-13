#!/bin/bash

set -e

sudo ssh -i "/home/user/Documents/DeployKey06.02.pem" ubuntu@ec2-18-144-142-254.us-west-1.compute.amazonaws.com 'cd quiz-site && git pull && sudo docker-compose  -f docker-compose-deploy.yml build && sudo docker-compose  -f docker-compose-deploy.yml down && sudo docker-compose  -f docker-compose-deploy.yml kill && sudo docker-compose  -f docker-compose-deploy.yml down && sudo docker-compose  -f docker-compose-deploy.yml up -d'

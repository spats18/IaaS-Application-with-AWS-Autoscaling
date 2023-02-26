#!/bin/bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.34.0/install.sh | bash
. ~/.nvm/nvm.sh
nvm install node
sudo apt update
sudo apt install nodejs -y
sudo apt install npm -y
npm install node-ec2-metadata
npm install shelljs
npm install aws-sdk


###
cd /home/ubuntu
echo "Current dir"
pwd
echo "Listing"
ls
chmod +x run.sh
echo "Trying to run"
sh run.sh

###
sudo su - ubuntu
cd /home/ubuntu
echo "Current dir"
pwd
echo "Listing"
ls
export PYTHONPATH="/home/ubuntu/.local/lib/python3.10/site-packages"
chmod +x run.sh
echo "Trying to run"
sh run.sh
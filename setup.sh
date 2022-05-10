#!/bin/bash

# require latest gnupg

# sudo -p mkdir img
mkdir -p img/ori
mkdir -p img/out
mkdir qrcode

# require python3 and pip
pip install -r requirement.txt

sudo apt install imagemagick-6.q16  
# sudo apt install imagemagick-6.q16hdri              
# sudo apt install graphicsmagick-imagemagick-compat
sudo apt install zbar-tools

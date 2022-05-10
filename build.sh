#!/bin/bash

pip3 install pyinstaller
pyinstaller paper_backup.py --onefile
pyinstaller embedded_image.py --onefile
pyinstaller exif.py --onefile

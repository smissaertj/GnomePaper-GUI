#!/usr/bin/env python3

################################################################
# Downloads a wallpaper from Unsplash and set it as the
# background in Gnome.
################################################################
# Author: Joeri JM Smissaert
# Version: 1.0
# Repository: https://gitlab.com/joerismissaert/gnomepaper-gui
################################################################


from config import RESOLUTION , THEME, PERSISTENT
from datetime import datetime
import os
import requests
import subprocess
import urllib

# General Settings
if PERSISTENT == 'Y':
	download_path = os.environ['HOME'] + '/Pictures/GnomePaper/'
else:
	download_path = '/tmp/'

img_date = datetime.now().strftime("%Y-%m-%d_%H-%M")
img_path = download_path + img_date + '.jpg'

# Functions
def img_download(img_url):
	# Download the image to download_path
	try:
		urllib.request.urlretrieve(img_url, download_path+'/'+img_date+'.jpg')
	except urllib.error.HTTPError as http_err:
		print(f'HTTP Error occurred: {http_err}')
	except Exception as err:
		print(f'Other Error occurred: {err}')


def set_background(img_path):
	# Gnome - Set the background
	set_wallpaper = 'gsettings set org.gnome.desktop.background picture-uri file://' + img_path
	subprocess.run(set_wallpaper, shell=True)


def main():
	# Application entrypoint. 

	# Check if download_path exists, create it if not.
	if not os.path.exists(download_path):
		try:
			os.makedirs(download_path)
		except Exception as err:
			print(f'An error occurred: {err}')
	
	else:
		## Fetch the image from Unsplash Source
		if THEME:
			img_url = f'https://source.unsplash.com/{RESOLUTION}/?{THEME}'
		else:
			img_url = f'https://source.unsplash.com/{RESOLUTION}'

		img_download(img_url)
		set_background(img_path) 

main()



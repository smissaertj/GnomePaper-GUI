#!/usr/bin/env python3

#######################################################################
# Copies the files to ~/.local/bin/GnomePaper
# Copies the systemd user service and timer to ~/.config/systemd/user/
# Enables and Starts the systemd user timer unit.
#######################################################################
# Author: Joeri JM Smissaert
# Version: 1.0
# Repository: https://gitlab.com/joerismissaert/gnomepaper-gui
#######################################################################

from datetime import datetime
import os
import PySimpleGUI as sg
import re
import requests
import shutil
import subprocess
import urllib

menu_def = [ ['&Actions', ['&Uninstall Service::uninstall', '&Set Random Image::setrandom', '&Quit::exit'] ]]
resolution_list = ['3840x2160', '2560x1440', '1920x1080', '1440x900', '1280x720']
interval_list = ['30 Minutes', '60 Minutes', '4 Hours', '8 Hours', '24 Hours']
interval_values = {'30 Minutes': '*-*-* *:00/30:00', '60 Minutes':'*-*-* *:00:00', '4 Hours':'*-*-* 00/4:00:00', '8 Hours':'*-*-* 00/8:00:00', '24 Hours':'*-*-* 00:00:00'}

install_path = os.environ['HOME'] + '/.local/bin/gnomepaper-gui'
systemd_path = os.environ['HOME'] + '/.config/systemd/user'

app_files = ['gp', 'config.py']
systemd_files = ['gnomepaper-gui.service', 'gnomepaper-gui.timer']


# --- Functions ---
def write_config(resolution, interval, persistent, theme):

	# Write config.py
	with open('config.py', 'w') as config_file:
		config_file.write(f'RESOLUTION="{resolution}"\n')
		config_file.write(f'THEME="{theme}"\n')
		config_file.write(f'PERSISTENT="{persistent}"\n')


	## Search/Replace the Systemd Timer Unit
	# Read the current content of the file
	with  open('gnomepaper-gui.timer', 'r') as timer_file:
		# Read the current content of the file
		content = timer_file.read()

		# Search for a pattern in the file and replace it with the user provided interval, 
		# assign the new content of the file to a variable.
		content_new = re.sub("^OnCalendar=\*-\*-\*\s.*$", f"OnCalendar={interval}", content, flags = re.M)

	# Open the file in write mode
	with open('gnomepaper-gui.timer', 'w') as timer_file:
		# overwrite the existing content with the new content
		timer_file.write(content_new)
	## END 


def install():

	# Create the install path
	if not os.path.exists(install_path):
		os.makedirs(install_path)
	
	# Create the systemd user path
	if not os.path.exists(systemd_path):
		os.makedirs(systemd_path)
	
	# Copy app files to install and systemd path
	for file in app_files:
		shutil.copyfile(file, install_path + '/' + file)
	
	for file in systemd_files:
		shutil.copyfile(file, systemd_path + '/' + file)

	# Start and enable systemd user timer, reload the systemctl user deamon. 
	cmd = 'systemctl --user enable --now gnomepaper-gui.timer; systemctl --user daemon-reload'
	subprocess.run(cmd, shell=True)

	# If no errors, confirm the installation.
	sg.popup('GnomePaper was installed.', title='Success!')


def uninstall():
	# Disable the Systemd Timer
	cmd = 'systemctl --user disable --now gnomepaper-gui.timer'
	subprocess.run(cmd, shell=True)

	# Remove the Systemd Unit files
	for file in systemd_files:
		os.remove(systemd_path + '/' + file)

	# Remove the installation directory
	shutil.rmtree(install_path)

	# Systemd daemon-reload
	cmd = 'systemctl --user daemon-reload'
	subprocess.run(cmd, shell=True)

	# If no errors, confirm the uninstallation.
	sg.popup('GnomePaper GUI was uninstalled.', title='Success!')


def set_random(resolution):

	download_path = '/tmp/'

	img_date = datetime.now().strftime("%Y-%m-%d_%H-%M")
	img_path = download_path + img_date + '.jpg'

	# Download the image to download_path
	try:
		img_url = f'https://source.unsplash.com/{resolution}'
		urllib.request.urlretrieve(img_url, download_path+'/'+img_date+'.jpg')
		# Gnome - Set the background
		set_wallpaper = 'gsettings set org.gnome.desktop.background picture-uri file://' + img_path
		subprocess.run(set_wallpaper, shell=True)
	except urllib.error.HTTPError as http_err:
		sg.PopupError(f'HTTP Error occurred: {http_err}')
	except Exception as err:
		sg.PopupError(f'Other Error occurred: {err}')



# --- Define Window Layout ---
# ---------- ROW 1 ------------
# ----------------------------- Define Resolutions list ---------------------------------
column_1 = [
	[sg.Text("Screen Resolution:")], 
	[sg.Listbox(resolution_list, size=(15, len(resolution_list)), key='-RESOLUTION-', enable_events=True)]
]


# ----------------------------- Define Interval List ------------------------------------
column_2 = [
	[sg.Text("Interval:")],
	[sg.Listbox(interval_list, size=(15, len(resolution_list)), key='-INTERVAL-', enable_events=True)]
]

# ----------------------------- Define Theme Keywords ------------------------------------
column_3 = [
	
	[sg.Text("Comma Separated Keywords:")],
	[sg.Multiline(size=(15, len(resolution_list)), key='-THEME-', enable_events=True)]
]


# --- Main Window Layout ---
layout = [
	# ---------- ROW 1 ------------
	[
		sg.Menu(menu_def, pad=(10,10)),
		sg.Column(column_1),
		sg.VSeperator(),
		sg.Column(column_2),
		sg.VSeperator(),
		sg.Column(column_3)
	],
	# ---------- ROW 2 ------------
	[
		sg.Checkbox('Keep files?', size=(15,1), default=True, change_submits=True, key='-PERSISTENT-'),
	],
	# ---------- ROW 3 ------------
	[
		sg.Button('Configure & Install GnomePaper GUI')
	]
]
# --- End Window Layout ---


# --------------------------------- Create Main Window ---------------------------------
#sg.theme('Dark Green 5')
window = sg.Window("GnomePaper GUI", layout)



# ----- Run the Event Loop -----
# --------------------------------- Event Loop ---------------------------------
while True:
	event, values = window.read()

	resolution = ''
	interval = ''
	persistent = ''
	theme = ''


	# End program if user closes window or
	# presses the OK button
	if event == sg.WIN_CLOSED or event == 'Quit::exit':
		break

	if values['-RESOLUTION-']: # If a resolution is selected in the list
		resolution = values['-RESOLUTION-'][0]

	if values['-INTERVAL-']: # if an interval is selected in the list
		interval = interval_values[values['-INTERVAL-'][0]]

	if values['-PERSISTENT-']:
		persistent = values['-PERSISTENT-']
	else:
		persistent = values['-PERSISTENT-']

	if values['-THEME-']:
		theme = values['-THEME-'].strip() # Strip the whitespace from sg.Multiline

	if event == 'Set Random Image::setrandom':
		if not resolution: # if no resolution was selected
			sg.popup('Please select a resolution and interval.', title='Info')
		else:
			set_random(resolution)

	if event == 'Configure & Install GnomePaper GUI':
		if not resolution or not interval: # if no interval or resolution was selected
			sg.popup('Please select a resolution and interval.', title='Info')
		else:
			try:
				write_config(resolution, interval, persistent, theme)
				install()
			except Exception as err:
				sg.PopupError(f'Error: {err}', title='Error!')
				break # Break out of the event loop and close the app. 

	if event == 'Uninstall Service::uninstall':
		confirmation = sg.PopupOKCancel('Are you sure?', title='Uninstall GnomePaper GUI')
		if confirmation == 'OK' and os.path.exists(systemd_path + '/' + systemd_files[0]):
			try:
				uninstall()
			except Exception as err:
				sg.PopupError(f'Error: {err}', title='Error!')
				break # Break out of the event loop and close the app. 
		elif confirmation == 'OK' and not os.path.exists(systemd_path + '/' + systemd_files[0]):
			sg.popup('GnomePaper is not installed.', title='Info')


window.close()
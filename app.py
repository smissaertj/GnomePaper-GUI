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

import os
import PySimpleGUI as sg
import re
import shutil
import subprocess

menu_def = [ ['&Actions', ['!&Uninstall Service', '!&Set Random Image', '&Quit::exit'] ]]
resolution_list = ['3840x2160', '2560x1440', '1920x1080', '1440x900', '1280x720']
interval_list = ['30 Minutes', '60 Minutes', '4 Hours', '8 Hours', '24 Hours']
interval_values = {'30 Minutes': '*-*-* *:00/30:00', '60 Minutes':'*-*-* *:00:00', '4 Hours':'*-*-* 00/4:00:00', '8 Hours':'*-*-* 00/8:00:00', '24 Hours':'*-*-* 00:00:00'}

install_path = os.environ['HOME'] + '/.local/bin/gnomepaper-gui'
systemd_path = os.environ['HOME'] + '/.config/systemd/user'

app_files = ['gp', 'config.py']
systemd_files = ['gnomepaper-gui.service', 'gnomepaper-gui.timer']

# --- Functions ---
def write_config(resolution, interval, theme, persistent):

	try:
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

	except Exception as err:
		sg.PopupError(f'An Error occurred: {err}', title='Error!')


def install():

	try:
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
		#cmd = 'systemctl --user enable --now gnomepaper-gui.timer > /dev/null 2&>1; systemctl --user daemon-reload'
		#subprocess.run(cmd, shell=True)

	except Exception as err:
		sg.popup(f'An Error occurred: {err}', title='Error!')


# --- Define Window Layout ---
# ---------- ROW 1 ------------
# ----------------------------- Define Resolutions list ---------------------------------
column_1 = [
	[sg.Text("Screen Resolution:")], 
	[sg.Listbox(resolution_list, size=(9, len(resolution_list)), key='-RESOLUTION-', enable_events=True)]
]


# ----------------------------- Define Interval List ------------------------------------
column_2 = [
	[sg.Text("Interval:")],
	[sg.Listbox(interval_list, size=(15, len(resolution_list)), key='-INTERVAL-', enable_events=True)]
]

# ----------------------------- Define Theme Keywords ------------------------------------
column_3 = [
	[sg.Checkbox('Keep files?', size=(15,1), default=True, change_submits=True, key='-PERSISTENT-')],
	[sg.Text("Comma separated keywords:")],
	[sg.InputText(size=(15, 1), key='-THEME-', enable_events=True)]
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
	[sg.Button('Configure & Install GnomePaper GUI')]
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
	if event == sg.WIN_CLOSED:
		break

	if values['-RESOLUTION-']: # If a resolution is selected in the list
		resolution = values['-RESOLUTION-'][0]
		print(f'{resolution} was set!')

	if values['-INTERVAL-']: # if an interval is selected in the list
		interval = interval_values[values['-INTERVAL-'][0]]
		print(f"{interval} was set!")

	if values['-PERSISTENT-']:
		persistent = values['-PERSISTENT-']
		print(persistent)
	else:
		persistent = values['-PERSISTENT-']
		print(persistent)

	if values['-THEME-']:
		theme = values['-THEME-']
		print(theme)

	if event == 'Configure & Install GnomePaper GUI':
		if not resolution or not interval: # if no interval or resolution was selected
			sg.popup('Please select a resolution and interval.', title='Info')
		else:
			print('Installing...')
			try:
				write_config(resolution, interval, persistent, theme)
				install()
			except Exception as err:
				sg.PopupError(f'An Error occurred: {err}', title='Error!')

window.close()
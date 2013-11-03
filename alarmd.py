#!/usr/bin/python

import subprocess
import datetime
import time
import os 
import RPi.GPIO as io
import tweetpony

api = tweetpony.API(consumer_key = "abcd", consumer_secret = "efgh", access_token = "ijkl", access_token_secret = "mnop")

io.setmode(io.BCM)

pir_pin = 18
flashingLight_pin = 7

io.setup(pir_pin, io.IN)
io.setup(flashingLight_pin, io.OUT)
io.output(flashingLight_pin, io.LOW)

# --------- Main Program ---------
previous_pir=0

while True:
	current_pir=io.input(pir_pin)	
	if previous_pir==0 and current_pir==1:
		with open("/home/pi/Alarm/armed.txt", "r") as fo:
                    fo.seek(0, 0)
                    status = fo.read(1)
                fo.closed
                print "Motion detected, armed status: " + str(status)
		if (status == "1"):
		    subprocess.call("mpg123 /home/pi/Alarm/motiondetect.mp3", shell=True)
                    time.sleep(10)
		    with open("/home/pi/Alarm/armed.txt", "r") as fo:
                        fo.seek(0, 0)
                        status = fo.read(1)
                    fo.closed 
		    if (status == "1"):
		        print "Correct passcode not entered, emailing picture and sounding alarm."
                        grab_cam = subprocess.Popen("sudo fswebcam -r 640x480 -d /dev/video0 -q /home/pi/Alarm/pictures/%m-%d-%y-%H%M.jpg", shell=True)
                        grab_cam.wait()
                        todays_date = datetime.datetime.today()
                        image_name = todays_date.strftime('%m-%d-%y-%H%M')
                        image_path = '/home/pi/Alarm/pictures/' + image_name + '.jpg'
                        subprocess.Popen('echo "Here is your intruder:" | mail -a ' + image_path + ' -s "Intruder Alert" muddysdad@gmail.com', shell=True)

		        try:
		            api.update_status_with_media(status = ("Intruder alert: " + todays_date.strftime('%m-%d-%y-%H%M')), media= image_path)
		        except tweetpony.APIError as err:
		            print "Oops, something went wrong! Twitter returned error #%i and said: %s" % (err.code, err.description)

                        io.output(flashingLight_pin, io.HIGH)
		        subprocess.call("mpg123 /home/pi/Alarm/alarm.mp3", shell=True)
                        subprocess.call("mpg123 /home/pi/Alarm/surrender.mp3", shell=True)
                        subprocess.call("mpg123 /home/pi/Alarm/alarm.mp3", shell=True)                       
                        io.output(flashingLight_pin, io.LOW)
                        del_img = subprocess.Popen("sudo rm -rf  " + image_path, shell=True)
                        del_img.wait()
	previous_pir=current_pir
	time.sleep(1)

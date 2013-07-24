# #####################################################
# Python Library for 3x4 matrix keypad using
# 7 of the avialable GPIO pins on the Raspberry Pi. 
# 
# This could easily be expanded to handle a 4x4 but I 
# don't have one for testing. The KEYPAD constant 
# would need to be updated. Also the setting/checking
# of the colVal part would need to be expanded to 
# handle the extra column.
# 
# Written by Chris Crumpacker
# May 2013
#
# main structure is adapted from Bandono's
# matrixQPI which is wiringPi based.
# https://github.com/bandono/matrixQPi?source=cc
# #####################################################
 
import RPi.GPIO as GPIO
import time
import subprocess
 
class keypad():
    # CONSTANTS   
    KEYPAD = [
    [1,2,3],
    [4,5,6],
    [7,8,9],
    ["*",0,"#"]
    ]
     
    ROW         = [27,23,24,25]
    COLUMN      = [4,17,22]
     
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
     
    def getKey(self):
         
        # Set all columns as output low
        for j in range(len(self.COLUMN)):
            GPIO.setup(self.COLUMN[j], GPIO.OUT)
            GPIO.output(self.COLUMN[j], GPIO.LOW)
         
        # Set all rows as input
        for i in range(len(self.ROW)):
            GPIO.setup(self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)
         
        # Scan rows for pushed key/button
        # A valid key press should set "rowVal"  between 0 and 3.
        rowVal = -1
        for i in range(len(self.ROW)):
            tmpRead = GPIO.input(self.ROW[i])
            if tmpRead == 0:
                rowVal = i
                 
        # if rowVal is not 0 thru 3 then no button was pressed and we can exit
        if rowVal < 0 or rowVal > 3:
            self.exit()
            return
         
        # Convert columns to input
        for j in range(len(self.COLUMN)):
                GPIO.setup(self.COLUMN[j], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
         
        # Switch the i-th row found from scan to output
        GPIO.setup(self.ROW[rowVal], GPIO.OUT)
        GPIO.output(self.ROW[rowVal], GPIO.HIGH)
 
        # Scan columns for still-pushed key/button
        # A valid key press should set "colVal"  between 0 and 2.
        colVal = -1
        for j in range(len(self.COLUMN)):
            tmpRead = GPIO.input(self.COLUMN[j])
            if tmpRead == 1:
                colVal=j
                 
        # if colVal is not 0 thru 2 then no button was pressed and we can exit
        if colVal < 0 or colVal > 2:
            self.exit()
            return
 
        # Return the value of the key pressed
        self.exit()
        return self.KEYPAD[rowVal][colVal]
         
    def exit(self):
        # Reinitialize all rows and columns as input at exit
        for i in range(len(self.ROW)):
                GPIO.setup(self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP) 
        for j in range(len(self.COLUMN)):
                GPIO.setup(self.COLUMN[j], GPIO.IN, pull_up_down=GPIO.PUD_UP)
         
if __name__ == '__main__':
    # Initialize the keypad class
    kp = keypad()
    attempt = "0000"
    passcode = "3717"    
    haltcode = "6834"
    with open("/home/pi/Alarm/armed.txt", "r+") as fo:
        fo.seek(0, 0)
        fo.write("0")
    fo.closed

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(10, GPIO.OUT) #Green
    GPIO.output(10, GPIO.HIGH)
    GPIO.setup(9, GPIO.OUT) #Red
    GPIO.output(9, GPIO.LOW)
    GPIO.setup(7, GPIO.OUT) #Flashing Light
#    GPIO.output(7, GPIO.LOW)

    subprocess.call("mpg123 /home/pi/Alarm/ready.mp3", shell=True)

    # Loop while waiting for a keypress
    while True:
        digit = None
        while digit == None:
            digit = kp.getKey()
     
        # Print the result
        print digit
        attempt = (attempt[1:] + str(digit))  
        print attempt

        if (attempt == passcode):
            with open("/home/pi/Alarm/armed.txt", "r+") as fo:
                fo.seek(0, 0)
                status = fo.read(1)
                print "Correct Passcode, file was:" + status
            fo.closed
            if (status == "1"):
                #system was armed, disarm it
                with open("/home/pi/Alarm/armed.txt", "r+") as fo:
                    fo.seek(0, 0)
                    fo.write("0")
                fo.closed
                GPIO.output(10, GPIO.HIGH) #Green LED On
                GPIO.output(9, GPIO.LOW) #Red LED off
                GPIO.output(7, GPIO.LOW)
                subprocess.call("mpg123 /home/pi/Alarm/disarmed.mp3", shell=True)
                #subprocess.call('echo "System disarmed." | festival --tts', shell=True) 
            else:
                GPIO.output(10, GPIO.LOW) #Green LED Off
                GPIO.output(9, GPIO.HIGH) #Red LED on
#                GPIO.output(7, GPIO.HIGH)
                subprocess.call("mpg123 /home/pi/Alarm/armed.mp3", shell=True)
                time.sleep(10)
                with open("/home/pi/Alarm/armed.txt", "r+") as fo:
                    fo.seek(0, 0)
                    fo.write("1")
                fo.closed
                #subprocess.call('echo "System armed." | festival --tts', shell=True)
        elif (attempt == haltcode):
            subprocess.call("mpg123 /home/pi/Alarm/shutdown.mp3", shell=True)
            subprocess.call("halt", shell=True)
        
        # Make video alarm system voiceovers:
        elif (attempt == "0001"):
        	time.sleep(10)
        	subprocess.call("mpg123 /home/pi/Alarm/vo/0001.mp3", shell=True)
        elif (attempt == "0002"):
        	time.sleep(10)
        	subprocess.call("mpg123 /home/pi/Alarm/vo/0002.mp3", shell=True)
        elif (attempt == "1003"):
        	time.sleep(10)
        	GPIO.output(7, GPIO.HIGH)
        	time.sleep(1)
        	subprocess.call("mpg123 /home/pi/Alarm/vo/0003.mp3", shell=True)
        	time.sleep(1)
        	GPIO.output(7, GPIO.LOW)
        elif (attempt == "0004"):
        	time.sleep(10)
        	subprocess.call("mpg123 /home/pi/Alarm/vo/0004.mp3", shell=True)
        elif (attempt == "0005"):
        	time.sleep(10)
        	subprocess.call("mpg123 /home/pi/Alarm/vo/0005.mp3", shell=True)
        elif (attempt == "0006"):
        	time.sleep(3)
        	GPIO.output(7, GPIO.HIGH)
        	subprocess.call("mpg123 /home/pi/Alarm/vo/0006.mp3", shell=True)
        	subprocess.call("mpg123 /home/pi/Alarm/alarm.mp3", shell=True)
        	subprocess.call("mpg123 /home/pi/Alarm/vo/0006.mp3", shell=True)
        	GPIO.output(7, GPIO.LOW)
        elif (attempt == "0007"):
        	time.sleep(10)
        	subprocess.call("mpg123 /home/pi/Alarm/vo/0007.mp3", shell=True)
        elif (attempt == "0008"):
        	time.sleep(10)
        	subprocess.call("mpg123 /home/pi/Alarm/vo/0008.mp3", shell=True)
        elif (attempt == "0009"):
        	time.sleep(10)
        	subprocess.call("mpg123 /home/pi/Alarm/vo/0009.mp3", shell=True)
        
        time.sleep(0.5)

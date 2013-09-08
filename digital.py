import sys
import time
import re
import httplib
import pygame
import ConfigParser
import json
import subprocess
import RPi.GPIO as GPIO
from datetime import datetime

config = ConfigParser.ConfigParser()
config.read('alarm.cfg')


#Open port for communication	

pygame.init();
pygame.init();
pygame.mixer.music.load(config.get('Settings', 'doorChime'));

#GPIO.setmode(GPIO.BOARD);
GPIO.setmode(GPIO.BCM)

def getState(gpioNum): 
	response = str(GPIO.input(gpioNum));
	return response;
	
def alert(gpioNum, newstate):
	conn = httplib.HTTPConnection(config.get('Settings', 'httpHost'));
	conn.request("GET", config.get('Settings', 'httpURI') + "/doorPort/" + str(gpioNum) + "/eventType/" + newstate);
	r1 = conn.getresponse();
	jsonDecoded = json.loads(r1.read());
	return jsonDecoded;
	
def monitorStateChange(gpioNum, newstate):
	start = datetime.now();
	now = datetime.now();
	delta = now - start;
	monitorTime = 100000;
	time.sleep(.1);
	while (delta.microseconds < monitorTime) :
		tmpState = getState(gpioNum);
		if (tmpState != newstate):
			now = datetime.now();
			delta = now - start;
			print "bailed at " + str(delta.microseconds) + "  port: " + str(gpioNum) + " started: " + start.isoformat(' ');
			return False;
		now = datetime.now();
		delta = now - start;
	return True;

states = eval(config.get('Settings', 'sensors'));
shellcmd = config.get('Settings', 'shell');

for (i, state) in enumerate(states):
	GPIO.setup(state[0], GPIO.IN);

while True:
	for (i, state) in enumerate(states):
		newstate = getState(state[0]);
		if (newstate != state[1]):
			if (monitorStateChange(state[0], newstate)):
				print "State Changed to: " + newstate + " Port: " + str(state[0]) + " at: " + datetime.now().isoformat(' ');
				if (newstate == '0'):
					pygame.mixer.music.play()
				responce = alert( state[0], newstate);
#				args = ['/home/lart/alarm/event.sh', str(responce['eventID']), responce['armedStatus'], newstate]
#				p = subprocess.Popen(args)
				states[i][1] = newstate;
#	time.sleep(.1);

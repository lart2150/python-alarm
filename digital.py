import sys
import serial
import time
import re
import httplib
import pygame
import ConfigParser
from datetime import datetime

config = ConfigParser.ConfigParser()
config.read('alarm.cfg')

#portName = "/dev/ttyACM0";
portName = config.get('Settings', 'portName')

#Open port for communication	
serPort = serial.Serial(portName, 115200, timeout=1)

pygame.init();
#pygame.mixer.music.load("/home/lart/alarm/2_HutchSFX.mp3");
pygame.mixer.music.load(config.get('Settings', 'doorChime'));



def getState(serPort, gpioNum): 
	serPort.write("gpio read "+ str(gpioNum) + "\n\r");
	response = serPort.read(18);
	response = response.split("\n\r")[1];
	return response;
	
def alert(gpioNum, newstate):
#	conn = httplib.HTTPConnection("alarm.lart2150.com")
	conn = httplib.HTTPConnection(config.get('Settings', 'httpHost'))
#	conn.request("GET", "/index.php/api/door-event/doorPort/" + str(gpioNum) + "/eventType/" + newstate)
	conn.request("GET", config.get('Settings', 'httpURI') + "/doorPort/" + str(gpioNum) + "/eventType/" + newstate)
	
def monitorStateChange(serPort, gpioNum, newstate):
	start = datetime.now();
	now = datetime.now();
	delta = now - start;
	monitorTime = 100000;
	if (gpioNum == 3):
		monitorTime = 500000;
	while (delta.microseconds < monitorTime) :
		tmpState = getState(serPort, gpioNum)
		if (tmpState != newstate):
			now = datetime.now();
			delta = now - start;
			print "bailed at " + str(delta.microseconds) + " of " + str(monitorTime) + " port: " + str(gpioNum) + " started: " + start.isoformat(' ');
			return False;
		now = datetime.now();
		delta = now - start;
	return True;

#states = [[0, "apples"], [3, "appples"], [4, "apples"]];
states = eval(config.get('Settings', 'sensors'));
while True:
	for (i, state) in enumerate(states):
		newstate = getState(serPort, state[0]);
		if (newstate != state[1]):
			if (monitorStateChange(serPort, state[0], newstate)):
				print "State Changed to: " + newstate + " Port: " + str(state[0]) + " at: " + datetime.now().isoformat(' ');
				if (newstate == '1'):
					pygame.mixer.music.play()
				alert( state[0], newstate);
				states[i][1] = newstate;
serPort.close()

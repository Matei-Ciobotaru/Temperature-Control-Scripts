#!/usr/bin/python

# Author = Matei Ciobotaru
# -*- coding: utf-8 -*-

"""  This script is used to start/start the fan
 when the CPU temperature threshold is reached. """
import sys
import subprocess as sp
from time import sleep
import logging
sys.path.append('/home/pi/github/Rock64-R64.GPIO')
import R64.GPIO as GPIO

# Set up logging

logFile = '/var/log/fan.log'
logging.basicConfig(filename=logFile,
		level=logging.DEBUG,
		format='%(asctime)s [%(levelname)s]: %(message)s')

# Fan switch is on BCM pin 18, change this value for your current setup

pin = 16

# Maximum temperature threshold in degrees Celcius, change this value for custom threshold

temp_max = 65

# Setup BCM Pin to OUT

def setup():

	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(pin, GPIO.OUT)
	GPIO.setwarnings(False)

# Obtain CPU temp 

def getCPUtemp():

	temp_cmd = sp.Popen(['cat', '/etc/armbianmonitor/datasources/soctemp'],
			     stdout=sp.PIPE,
			     stderr=sp.PIPE)

	stdout, stderr = temp_cmd.communicate()

	if stdout:
		temp_val = int(stdout)/1000.0
		return round(temp_val, 1)
	else:
		logging.error('Can\'t read temp file: %s' % stderr)
		return 1

# Start/Stop fan

def fanOn(state):
	
	try:
		GPIO.output(pin, state)
	except Exception as err:
		logging.error('%s' % err)

# Compare CPU temp to max threshold and start fan if exceeded
# Stop fan only when temperature is 15'C under max threshold

def checkTemp():

	temp_cpu = getCPUtemp()
	temp_min = temp_max - 25

# Check if fan is already ON/OFF (1/0)
	fan_state = int(GPIO.input(pin))
	
	if temp_cpu >= temp_max and fan_state == 0:
		fanOn(GPIO.HIGH)
		logging.info('Started fan, CPU temperature is: %.1f\'C, '
			     'max threshold is: %.1f\'C' % (temp_cpu, temp_max))
	elif temp_cpu <= temp_min and fan_state == 1:
		fanOn(GPIO.LOW)
		logging.info('Stopped fan, CPU temperature is: %.1f\'C, '
			     'min threshold is: %.1f\'C' % (temp_cpu, temp_min))

# Check temperature every n seconds

try:
	logging.info('Started fan service...')
	setup()
	while True:
		checkTemp()
		sleep(2)
except Exception as err:
	GPIO.cleanup(pin)
	fanOn(GPIO.LOW)
	logging.error('%s' % err)
except KeyboardInterrupt:
	fanOn(GPIO.LOW)
	GPIO.cleanup(pin)
	logging.info('Stopped fan service...')

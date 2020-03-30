import RPi.GPIO as GPIO
import subprocess as sp
from time import sleep

import logging

# Set up logging
# Logging messages to file

#logFile = '/var/log/fan_switch.log'
logFile = './fan_switch.log'

logging.basicConfig(filename=logFile,
					level=logging.DEBUG,
                    format='%(asctime)s [%(levelname)s]: %(message)s')

# Fan switch is on BCM pin 12

pin = 12

# Maximum temperature threshold in degrees Celcius

temp_max = 65

# Setup BCM Pin to OUT

def setup():

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(pin, GPIO.OUT)
	GPIO.setwarnings(False)

# Obtain CPU temp, I did not use "vcgencmd measure_temp" as it always prints to stdout

def getCPUtemp():

	temp_cmd = sp.Popen(['cat', '/sys/class/thermal/thermal_zone0/temp'],
						stdout=sp.PIPE,
					    stderr=sp.PIPE)

	temp_out = temp_cmd.stdout.readline()

	if temp_out:
		temp_val = int(temp_out)/1000.0
		return round(temp_val, 1)
	else:
		temp_err = temp_cmd.stderr.readlines()
		logging.error('Can\'t read temp file: %s' % err)
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
	temp_min = temp_max - 15

# Check if fan is already ON/OFF (1/0)

	fan_state = GPIO.input(pin)

	if temp_cpu >= temp_max and fan_state == 0:
		print('Started fan')
		fanOn(True)
		logging.info('Started fan, CPU temperature is: %.1f\'C, '
					 'max threshold is: %.1f\'C' % (temp_cpu, temp_max))
	elif temp_cpu <= temp_min and fan_state == 1:
		print('Stopped fan')
		fanOn(False)
		logging.info('Stopped fan, CPU temperature is: %.1f\'C, '
					 'min threshold is: %.1f\'C' % (temp_cpu, temp_min))

# Check temperature every n seconds

try:
	setup()
	while True:
		checkTemp()
		sleep(3)
except KeyboardInterrupt as msg:
	GPIO.cleanup()
	logging.info('Received ^C from user, will exit...')
except Exception as err:
	GPIO.cleanup()
	logging.error('%s' % err)

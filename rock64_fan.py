#!/usr/bin/env python

# -*- coding: utf-8 -*-

"""

 This script is used to start/start the fan when
 the configured temperature threshold is reached.

 Author: Matei Ciobotaru
 Rock64 SBC implementation

"""

import sys
import logging
from time import sleep


try:
    sys.path.append('/root/Rock64-R64.GPIO')
    import R64.GPIO as GPIO
except ImportError as err:
    print('Could not import R64.GPIO module: %s' % err)
    sys.exit(1)


# Set up logging
LOG_FILE = '/var/log/fan.log'
logging.basicConfig(filename=LOG_FILE,
                    level=logging.INFO,
                    format='%(asctime)s [%(levelname)s]: %(message)s')

# Fan switch is on BCM pin 18, change this value according to your setup
PIN = 16

# Maximum temperature threshold ['C] (fan will start)
MAX_TEMP = 65
# Mininum temperature threshold ['C] (fan swill stop)
MIN_TEMP = 40


def setup(pin):
    """
    Setup GPIO pin
    """

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.setwarnings(False)


def get_temp():
    """
    Get current temperature
    """

    try:
        with open('/etc/armbianmonitor/datasources/soctemp', 'r') as fhandle:
            temp = int(fhandle.read())/1000
            return round(temp, 1)
    except IOError as io_err:
        logging.error('Can\'t read temp file: %s', io_err)


def fan_switch(state):
    """
    Switch fan ON or OFF
    """

    try:
        fan_state = int(GPIO.input(PIN))
        # Check if fan is already in the desired state
        if fan_state != state:
            GPIO.output(PIN, state)
    except Exception as gpio_err:
        logging.error('GPIO exception: %s', gpio_err)


def check_temp(current_temp, min_temp, max_temp):
    """
    Compare CPU temp to max threshold and start fan if exceeded
    Stop fan only when temperature is 15'C under max threshold
    """

    if current_temp >= max_temp:
        fan_switch(1)
        logging.info('Started fan, CPU temperature is: %.1f\'C, '
                     'max threshold is: %.1f\'C', current_temp, max_temp)
    else:
        fan_switch(0)
        logging.info('Stopped fan, CPU temperature is: %.1f\'C, '
                     'min threshold is: %.1f\'C', current_temp, min_temp)


def main():
    """
    Run temperature check every 3 seconds untill stopped by user
    """

    try:
        logging.info('Started fan service...')
        setup(PIN)
        while True:
            temp = get_temp()
            check_temp(temp, MIN_TEMP, MAX_TEMP)
            sleep(2)
    except KeyboardInterrupt:
        logging.info('Stopped fan service...')
    finally:
        fan_switch(GPIO.LOW)
        GPIO.cleanup(PIN)


if __name__ == '__main__':
    main()

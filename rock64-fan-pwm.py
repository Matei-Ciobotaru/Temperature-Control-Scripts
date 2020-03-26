#!/usr/bin/env python3

# -*- coding: utf-8 -*- #

# Author: Matei Ciobotaru

"""

 This script is used to control the fan on my
ROCK64 SBC using Pulse Width Modulation.

 It uses the latest version (as of 25/03/2020)
of the "R64.GPIO" library.

 Details on library installation and usage:

https://github.com/Matei-Ciobotaru/Rock64-R64.GPIO

"""

from time import sleep
from re import search
import logging
import sys

# Import R64.GPIO library

try:
    GPIO_PATH = '/root/Rock64-R64.GPIO'
    sys.path.append(GPIO_PATH)
    import R64.GPIO as GPIO
except ImportError as imp_err:
    print('\n Error: Module not found, make sure '
          'the "{0}" path exists.\n'.format(GPIO_PATH))
    sys.exit(1)


# Global variables (edit accordingy)
# Fan GPIO setup

GPIO_PIN = 16  # PWM pin on ROCK64 SBC
PWM_FREQ = 20  # [Hz] this frequency works best with my fan
MIN_SPEED = 50  # Minimum duty cycle for my fan to turn on at above frequency

# Temperature thresholds

MIN_TEMP = 39.5  # ['C] Minimun SBC temperature threshold
MAX_TEMP = 70  # ['C] Maximum SBC temperature threshold
INTERVAL = 5  # [s] the time INTERVAL for temperature checks
HYSTERESIS = 1.8  # ['C] Temperature hysteresis

# Log and temperature files

LOG_FILE = '/var/log/fan.log'  # log file
TEMP_FILE = '/etc/armbianmonitor/datasources/soctemp'  # SBC temperature file


# Set up logging config

logging.basicConfig(filename=LOG_FILE,
                    level=logging.DEBUG,
                    format='%(asctime)s [%(levelname)s]: %(message)s')


def gpio_setup():
    """
    Setup GPIO_PIN as PWM input and start fan
    """

    try:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(GPIO_PIN, GPIO.OUT)
        fan = GPIO.PWM(GPIO_PIN, PWM_FREQ)
        return fan
    except IndexError:
        print('\n Error: Pin "{0}" does not exist.\n')
        sys.exit(2)
    else:
        print('\n Error: Could not setup GPIO pin "{0}".\n'.format(GPIO_PIN))
        sys.exit(4)


def get_temp():
    """
    Read SBC temperature
    """

    try:
        with open(TEMP_FILE, 'r') as fhandle:
            output = fhandle.read()
            temp_read = search(r'\d+', output)
            temp = round(int(temp_read.group(0))/1000, 1)
            return temp
    except FileNotFoundError:
        logging.error('Temperature file "{0}" not found!')
        sys.exit(5)
    except PermissionError as per_err:
        logging.error('Couldn\'t read temperature file: %s', per_err)
        sys.exit(6)
    except AttributeError:
        logging.error('No temperature integer found in "%s" file.', TEMP_FILE)
        sys.exit(7)


def temp_ctrl(fan, old_temp, old_speed):
    """
    Check and control temperature using fan speed
    """

    temp = get_temp()

    if temp > MAX_TEMP:
        speed = 100  # Maximum temperature exceeded, max fan speed
        logging.info('Temperature %s\'C exceeded maximum threshold '
                     '(%s\'C), fan speed set to 100%%.', temp, MAX_TEMP)
    elif temp < MIN_TEMP:
        speed = MIN_SPEED  # Minimum temperature reached, min fan speed
    else:
        # Calculate speed value using linear interpolation.
        # fan_speed = (max_speed - MIN_SPEED)/ (MAX_TEMP - MIN_TEMP)
        #             * (temp - MIN_TEMP)+ MIN_SPEED
        speed = round((100 - MIN_SPEED) / (MAX_TEMP - MIN_TEMP)
                      * (temp - MIN_TEMP) + MIN_SPEED, 1)
    # Change fan speed if temperature delta > HYSTERESIS
    # and if speed is different from last one recorded
    if abs(old_temp - temp) > HYSTERESIS:
        if int(speed) != int(old_speed):
            fan.ChangeDutyCycle(speed)
    return temp, speed


def main():
    """
    Run temperature control service
    """

    try:
        old_temp, old_speed = 0, 0
        fan = gpio_setup()
        fan.start(MIN_SPEED)
        logging.info('Started temperature control service...')
        while True:
            temp, speed = temp_ctrl(fan, old_temp, old_speed)
            old_temp, old_speed = temp, speed
            sleep(INTERVAL)
    except KeyboardInterrupt:
        fan.stop()
        logging.info('Stopped temperature control service.')
    else:
        fan.stop()
        logging.error('Unexpected error occurred, please check script.')
    finally:
        GPIO.cleanup(GPIO_PIN)


if __name__ == "__main__":
    main()

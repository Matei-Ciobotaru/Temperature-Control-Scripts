# SBC temperature control scripts using a 5V fan and Python/Bash

A couple of scripts I've created to control the temperature on my Raspberry Model 3B+ and Rock64 4GB model SBCs by automatically starting a 5V fan when the temperature exceeds a specified threshold.

## Python Libraries

The above mentioned scripts use the [RPi.GPIO](https://pypi.org/project/RPi.GPIO/) (Raspberry) and [R64.GPIO](https://github.com/Matei-Ciobotaru/Rock64-R64.GPIO/blob/master/README.md) (Rock64) python libraries to control the fan.

## systemd service file

**fan.service**<br>

 A simple systemd service file to start/stop the fan script using `systemd`.

 Note: Use `systemctl enable fan.service` to start the script at boot.


## Rock64 (Armbian OS) scripts

**rock64_fan_pwm.py**<br>


 This python script uses the R64.GPIO library to start the fan, connected to BCM GPIO pin 16, and control its speed using PWM based on the temperature reading. The temperature is monitored every 5 seconds by reading the `/etc/armbianmonitor/datasources/soctemp` file. When the temperature minimum threshold is met, the script runs at minimum speed, if the maximum threshold is met the fan will run at full blown speed, otherwise the fan speed is calculated using liniar interpolation.

 The script also logs the start/stop operations of the fan, possible errors and a warning entry when the the temperature exceeds the maximum threshold in `/var/log/fan.log`

 Note: The script has been only tested on [Armbian Buster OS](https://www.armbian.com/rock64/), using my version of the [Rock64-GPIO](https://github.com/Matei-Ciobotaru/Rock64-R64.GPIO) library.


**rock64_fan.py**<br>

 This python script uses the R64.GPIO library to start the fan, connected to BCM GPIO pin 16, when a certain temperature threshlod is reached. The temperature is monitored every 2 seconds by reading the `/etc/armbianmonitor/datasources/soctemp` file. When the temperature drops 15 degrees Celsius below the maxiumum threshold, the fan is automatically stopped.

 The script also logs the start/stop of the fan along with the temperature in `/var/log/fan.log`

 Note: The script has been only tested on a [Armbian Xenial 5.42](https://www.armbian.com/rock64/) for Rock64.

**rock64_fan.sh (deprecated)**<br>

 This bash script has the same function as the aforementioned python one and was used before editing the R64.GPIO python library to make it work on my kernel version.

## Raspberry Pi 3B+ (Raspbian Strech Lite 9.4 OS) script

**raspi_fan.py**<br>

 This python script uses the RPi.GPIO library to start the fan, connected to BCM GPIO pin 12, when a certain temperature threshlod is reached. The temperature is monitored every 2 seconds by reading the `/sys/class/thermal/thermal_zone0/temp` file. When the temperature drops 15 degrees Celsius below the maxiumum threshold, the fan is automatically stopped. The script also logs the start/stop of the fan along with the temperature in `/var/log/fan.log`

 Note: The script has been only tested on [Raspbian Strech Lite](https://www.raspberrypi.org/downloads/raspbian/).

Fan circuit and implementation details [here](https://nimbus.go.ro/index.php/s/GJkNWaXBBjrQEtC).

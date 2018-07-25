#!/bin/bash

# Author = Matei Ciobotaru

### This script is used to start/start the fan
### when the CPU temperature threshold is reached.


### Min/Max temperature thresholds ('C)

max=47
min=45
pin=1101 ### Rock64 board pin #16

### Set up logging 

logFile='/var/log/fan.log'

function log
{
    echo -e "[ $(date +'%Y-%m-%d %H:%M:%S') ] INFO: $1" >> $logFile
}

#logErr {
#    echo -e "[ $(date +'%Y-%m-%d %H:%M:%S') ] ERROR: $1" >> $logFile
#}


### function to start/stop fan

fan () 
{
gpio='/sys/class/gpio'

if [[ $1 == "start" ]]; then
	echo -n '1101' | sudo tee ${gpio}/export
	echo -n 'out' | sudo tee ${gpio}/gpio${pin}/direction
	echo -n '1' | sudo tee ${gpio}/gpio${pin}/value
elif [[ $1 == "stop" ]]; then
	echo -n '0' | sudo tee ${gpio}/gpio${pin}/value
	echo -n '1101' | sudo tee ${gpio}/unexport
elif [[ $1 == "status" ]]; then
	if [[ -f ${gpio}/gpio${pin}/value ]]; then
		cat ${gpio}/gpio${pin}/value
	else
		echo 0
	fi
else
	echo -e "Please enter start/stop as function arguments."
fi
}

### Poll board temp

while true; do
	
	now=`awk '{printf("%d",$1/1000)}' /etc/armbianmonitor/datasources/soctemp`
	state=`fan status`
	if [[ $now -gt $max ]] && [[ $state -eq 0 ]]; then
		fan start
		log "Fan started, board temperature is ${now}'C, max threshold is ${max}'C."
	elif [[ $now -lt $min ]] && [[ $state -eq 1 ]]; then
		fan stop
		log "Fan stopped, board temperature is ${now}'C, max threshold is ${max}'C."
	fi
	sleep 3
done

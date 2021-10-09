#!/bin/bash

 #####################################################
##                                                   ##
##                                                   ##
##  This script is used to start/start the fan when  ##
## the configured temperature threshold is reached.  ##
##                                                   ##
##  Author: Matei Ciobotaru                          ##
##                                                   ##
##                                                   ##
 #####################################################


# Minimum and maximum temperature thresholds ('C)
MAX_TEMP=65
MIN_TEMP=45

# Check interval in seconds
INTERVAL=3

# GPIO PIN
PIN=1101  # Rock64 board pin #16 on Armbian OS
# PIN=101  # Rock64 board pin #16 on Dietpi OS

# Set up logging 
LOG_FILE='/var/log/fan.log'

log(){
    echo -e "[ $(date +'%Y-%m-%d %H:%M:%S') ] INFO: $1" >> ${LOG_FILE}
}


# Start or stop fan
fan () {
  local gpio='/sys/class/gpio'

    if [[ $1 == "start" ]]; then
      echo -n ${PIN} | sudo tee ${gpio}/export
      echo -n 'out' | sudo tee ${gpio}/gpio${PIN}/direction
      echo -n '1' | sudo tee ${gpio}/gpio${PIN}/value

    elif [[ $1 == "stop" ]]; then
      echo -n '0' | sudo tee ${gpio}/gpio${PIN}/value
      echo -n ${PIN} | sudo tee ${gpio}/unexport

    elif [[ $1 == "status" ]]; then
      if [[ -f ${gpio}/gpio${PIN}/value ]]; then
        cat ${gpio}/gpio${PIN}/value
      else
        echo 0
      fi

    else
       echo -e "Please enter start/stop as function arguments."
    fi
}


# Poll temperature every 3 seconds
while true; do

  TEMP=`awk '{printf("%d",$1/1000)}' /etc/armbianmonitor/datasources/soctemp`
  STATE=`fan status`

  if [[ ${TEMP} -gt ${MAX_TEMP} ]] && [[ ${STATE} -eq 0 ]]; then
    fan start
    log "Fan started, board temperature is ${TEMP}'C, max threshold is ${MAX_TEMP}'C."

  elif [[ ${TEMP} -lt ${MIN_TEMP} ]] && [[ ${STATE} -eq 1 ]]; then
    fan stop
    log "Fan stopped, board temperature is ${TEMP}'C, min threshold is ${MIN_TEMP}'C."
  fi
  sleep ${INTERVAL}
done


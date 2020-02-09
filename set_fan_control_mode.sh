#!/usr/bin/env bash

# for nct6775
# 5 is auto mode
# 1 is manual mode
# 0 is no speed control (full speed)
devPath=/sys/devices/platform/nct6775.2592/hwmon/hwmon0
autoMode=$1

function setMode() {
  echo $autoMode > $devPath/$1
}

setMode "pwm1_enable"
setMode "pwm2_enable"
setMode "pwm4_enable"
setMode "pwm5_enable"
setMode "pwm6_enable"

#!/usr/bin/env bash

# script input
# $1
# 0: manual mode
# 1: auto mode

# for nct6775
# 5 is auto mode
# 1 is manual mode
# 0 is no speed control (full speed)
# for amdgpu
# 1: manual
# 2: auto

set -e

gpuDevPath=$(echo /sys/devices/pci0000:00/0000:00:03.1/0000:26:00.0/0000:27:00.0/0000:28:00.0/hwmon/hwmon*)

mbDevPath=$(echo /sys/devices/platform/nct6775.2592/hwmon/hwmon*)

globalMode=$1

case $globalMode in
  0) # manual mode
    mbMode=1
    gpuMode=1
    ;;
  1) # auto mode
    mbMode=5
    gpuMode=2
    ;;
  *)
    >&2 echo "choose 0 (manual) or 1 (auto) ONLY"
    exit 1
    ;;
esac

function set_gpu_mode() {
  echo $gpuMode > $gpuDevPath/$1
}

function set_mb_mode() {
  echo $mbMode > $mbDevPath/$1
}

set_mb_mode "pwm1_enable"
set_mb_mode "pwm2_enable"
set_mb_mode "pwm3_enable"
set_mb_mode "pwm4_enable"
set_mb_mode "pwm5_enable"
set_mb_mode "pwm6_enable"

set_gpu_mode "pwm1_enable"

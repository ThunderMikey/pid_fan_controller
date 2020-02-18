#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# set to manual mode
$DIR/set_fan_control_mode.sh 1

$DIR/pid_fan_controller.py

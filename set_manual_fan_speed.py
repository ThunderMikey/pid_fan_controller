#!/usr/bin/env python3
import os, sys
from pid_fan_controller import PID_fan_controller

fan_speed = int(sys.argv[1])
DRY_RUN = os.getenv('DRY_RUN')
CONFIG_FILE = os.getenv('CONFIG_FILE')

assert fan_speed<=100 and fan_speed>=0
config_file = str(CONFIG_FILE) if CONFIG_FILE else '/etc/pid_fan_controller_config.yaml'
dry_run = True if DRY_RUN else False

controller = PID_fan_controller(config_file)

controller.set_manual_fan_speed(fan_speed, dry_run)

#!/usr/bin/env python3
import os, glob, sys, yaml

# only one argument
mode = int(sys.argv[1])
NONE_ROOT_DEBUG = bool(os.getenv('NONE_ROOT_DEBUG'))

if NONE_ROOT_DEBUG:
    CONFIG_FILE='./pid_fan_controller_config.yaml'
else:
    CONFIG_FILE='/etc/pid_fan_controller_config.yaml'

with open(CONFIG_FILE, 'r') as f:
    try:
        config = yaml.load(f, Loader=yaml.FullLoader)
    except yaml.YAMLError as exc:
        print("Error in loading the config file:", CONFIG_FILE, '\n',exc)
        exit(1)

def get_only_one_wildcard_match(wc_path):
    should_be_a_single_path = glob.glob(wc_path)
    assert len(should_be_a_single_path) == 1
    return should_be_a_single_path[0]

def override_fan_auto_control(override, fan_cfgs=config['fans']):
    for fan in fan_cfgs:
        pwm_modes = fan['pwm_modes']
        path = get_only_one_wildcard_match(pwm_modes['pwm_mode_wildcard_path'])
        mode = pwm_modes['manual'] if override else pwm_modes['auto']
        if NONE_ROOT_DEBUG:
            print(path, mode)
        else:
            with open(path, 'w') as f:
                f.write(str(mode))

if mode == 1:
    override_fan_auto_control(True)
elif mode == 0:
    override_fan_auto_control(False)
else:
    RuntimeError("invalid bool, choose between 0, 1")

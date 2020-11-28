#!/usr/bin/env python3
from simple_pid import PID
import time, glob, os, yaml, subprocess

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

class PwmFan:
    def __init__(self, name, devPath, minPwm, maxPwm, press_srcs):
        assert minPwm < maxPwm
        assert minPwm >= 0 and minPwm <= 255
        assert maxPwm >= 0 and maxPwm <= 255
        self.name = name
        self.devPath = devPath
        self.minPwm = minPwm
        self.maxPwm = maxPwm
        self.range = self.maxPwm - self.minPwm
        self.press_srcs = press_srcs

    def set_speed(self, percentage):
        """
        set fan speed, 0-100%. The PWM value will be calculated from minPwm and
        maxPwm
        """
        assert percentage >= 0.0 and percentage <= 1.0
        pwm = self.minPwm + self.range * percentage
        if NONE_ROOT_DEBUG:
            print(self.devPath, percentage)
        else:
            with open(self.devPath, 'w') as f:
                f.write(str(int(pwm)))

    def get_pressure_srcs(self):
        return self.press_srcs

class TempSensor:
    def __init__(self, devPath):
        self.devPath = devPath

    def read_temp(self):
        f = open(self.devPath, 'r')
        # integer type temperature in milli degrees
        temp = str(f.read()).strip()
        f.close()
        # convert to float degrees
        return int(temp)/1000.0

class CmdTempSensor:
    def __init__(self, temp_cmd):
        self.temp_cmd = temp_cmd

    def read_temp(self):
        completedCmd = subprocess.run(
                self.temp_cmd,
                check=True,
                shell=True,
                text=True,
                capture_output=True)
        # convert to float degrees
        return int(completedCmd.stdout)/1.0

class HeatPressureSrc:
    def __init__(self, name, path, temp_cmd, set_point, P, I, D, sample_interval):
        self.name = name
        self.path = path
        self.temp_cmd = temp_cmd
        self.set_point = set_point
        self.P = P
        self.I = I
        self.D = D
        self.sample_interval = sample_interval
        if self.temp_cmd is not None:
            self.temp_sensor = CmdTempSensor(temp_cmd)
        else:
            self.temp_sensor = TempSensor(path)
        self.pid_controller = PID(self.P, self.I, self.D,
                setpoint=self.set_point,
                output_limits=(0.0, 1.0),
                sample_time=self.sample_interval
                )

    def get_heat_pressure(self):
        temperature = self.temp_sensor.read_temp()
        heat_pressure = self.pid_controller(temperature)
        return heat_pressure

    def get_name(self):
        return self.name

def get_only_one_wildcard_match(wc_path):
    should_be_a_single_path = glob.glob(wc_path)
    assert len(should_be_a_single_path) == 1
    return should_be_a_single_path[0]

def instantiate_fan(cfg):
    name = cfg['name']
    wc_path = cfg['wildcard_path']
    min_pwm = cfg['min_pwm']
    max_pwm = cfg['max_pwm']
    press_srcs = cfg['heat_pressure_srcs']
    path = get_only_one_wildcard_match(wc_path)

    return PwmFan(name, path, min_pwm, max_pwm, press_srcs)

def instantiate_hp_src(cfg, sample_interval):
    name = cfg['name']
    PID_params = cfg['PID_params']
    if 'wildcard_path' in cfg:
        wc_path = cfg['wildcard_path']
        path = get_only_one_wildcard_match(wc_path)
    else:
        path = None
    temp_cmd = cfg['temp_cmd'] if 'temp_cmd' in cfg else None
    if (path or temp_cmd) is None:
        print(cfg)
        raise RuntimeError("Neither `temp_cmd` or `wildcard_path` exists")

    return HeatPressureSrc(name = name, path = path,
            temp_cmd = temp_cmd,
            set_point = PID_params['set_point'],
            P = PID_params['P'],
            I = PID_params['I'],
            D = PID_params['D'],
            sample_interval = sample_interval
            )

sample_interval = config['sample_interval']
heat_pressure_srcs = [ instantiate_hp_src(hp_cfg, sample_interval) for hp_cfg in config["heat_pressure_srcs"] ]
fans = [ instantiate_fan(fan_config) for fan_config in config["fans"] ]

while True:
    heat_pressures = {}
    for hp in heat_pressure_srcs:
        name = hp.get_name()
        pressure = hp.get_heat_pressure()
        heat_pressures[name] = pressure

    for fan in fans:
        press_srcs = fan.get_pressure_srcs()
        hp = [ heat_pressures[hp_src] for hp_src in press_srcs ]
        highest_pressure = max(hp)
        fan.set_speed(highest_pressure)

    time.sleep(sample_interval)

#!/usr/bin/env python3
from simple_pid import PID
import time
import glob
import os

NONE_ROOT_DEBUG = bool(os.getenv('NONE_ROOT_DEBUG'))

hwmonMbTemplate = '/sys/devices/platform/nct6775.2592/hwmon/hwmon*/'
hwmonGpuTemplate = '/sys/devices/pci0000:00/0000:00:03.1/0000:26:00.0/0000:27:00.0/0000:28:00.0/hwmon/hwmon*/'
k10tempTemplate = '/sys/devices/pci0000:00/0000:00:18.3/hwmon/hwmon*/'

hwmonMbPaths = glob.glob(hwmonMbTemplate)
hwmonGpuPaths = glob.glob(hwmonGpuTemplate)
k10tempPaths = glob.glob(k10tempTemplate)

assert len(hwmonMbPaths) == 1
assert len(hwmonGpuPaths) == 1
assert len(k10tempPaths) == 1

hwmonMb = hwmonMbPaths[0]
hwmonGpu = hwmonGpuPaths[0]
k10temp = k10tempPaths[0]

cpuTargetTemp = 63
gpuTargetTemp = 70

class pwmFan():
    def __init__(self, devPath, minPwm, maxPwm):
        assert minPwm < maxPwm
        assert minPwm >= 0 and minPwm <= 255
        assert maxPwm >= 0 and maxPwm <= 255
        self.devPath = devPath
        self.minPwm = minPwm
        self.maxPwm = maxPwm
        self.range = self.maxPwm - self.minPwm

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
            f = open(self.devPath, 'w')
            f.write(str(int(pwm)))
            f.close()

class tempSensor():
    def __init__(self, devPath):
        self.devPath = devPath

    def read_temp(self):
        f = open(self.devPath, 'r')
        # integer type temperature in milli degrees
        temp = str(f.read()).strip()
        f.close()
        # convert to float degrees
        return int(temp)/1000.0

# reverse PID mode to control temperature
gpuPidController = PID(-0.03, -0.002, -0.0005,
        setpoint=gpuTargetTemp,
        output_limits=(0.0, 1.0),
        sample_time=0.5)

# for CPU
# P: when temp = 85, 40% fan speed
#   coefficient = -0.4/(85-55) = -0.01
# I: ramp-up fan speed to 50% when temp = 65 for 10 seconds
#   coefficient = -0.005
# D: not sensitive to sudden temp change, however, when temp change of 30 degrees
#   in 0.5 sec, ramp-up the fan to 100%
#   coefficient = -1/(30/0.5) = -0.016
# further adjustments... to take into account of P, I, D each contributing to overall fan speed
cpuPidController = PID(-0.005, -0.005, -0.006,
        setpoint=cpuTargetTemp,
        output_limits=(0.0, 1.0),
        sample_time=0.5)

# fans
# default stop
fanExhaustTop = pwmFan(hwmonMb + "pwm1", 50, 255)
fanExhaustBack = pwmFan(hwmonMb + "pwm3", 80, 255)
fanCpu = pwmFan(hwmonMb + "pwm2", 70, 190)
fanIntakeTop = pwmFan(hwmonMb + "pwm5", 60, 255)
fanIntakeMid = pwmFan(hwmonMb + "pwm6", 70, 255)
fanIntakeBot = pwmFan(hwmonMb + "pwm4", 60, 255)

# GPU fan
fanGpu = pwmFan(hwmonGpu + "pwm1", 30, 120)

# sensors
# k10temp, Tdie
cpuSensor = tempSensor(k10temp + 'temp1_input')
gpuSensor = tempSensor(hwmonGpu + 'temp1_input')

while True:
    cpuTemp = cpuSensor.read_temp()
    gpuTemp = gpuSensor.read_temp()
    cpuDelta = cpuPidController(cpuTemp)
    gpuDelta = gpuPidController(gpuTemp)
    #avgDelta = 0.4*cpuDelta + 0.6*gpuDelta
    # use maxDelta for all fans
    maxDelta = max(gpuDelta, cpuDelta)

    fanCpu.set_speed(cpuDelta)
    fanGpu.set_speed(gpuDelta)

    fanIntakeTop.set_speed(maxDelta)
    fanIntakeMid.set_speed(maxDelta)
    fanIntakeBot.set_speed(maxDelta)
    fanExhaustTop.set_speed(maxDelta)
    fanExhaustBack.set_speed(maxDelta)

    #print(cpuTemp, gpuTemp, cpuDelta, gpuDelta)
    time.sleep(0.5)

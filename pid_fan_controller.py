#!/usr/bin/env python3
from simple_pid import PID
import time
import glob

hwmonMbTemplate = '/sys/devices/platform/nct6775.2592/hwmon/hwmon*/'
hwmonGpuTemplate = '/sys/devices/pci0000:00/0000:00:03.1/0000:26:00.0/0000:27:00.0/0000:28:00.0/hwmon/hwmon*/'

hwmonMbPaths = glob.glob(hwmonMbTemplate)
hwmonGpuPaths = glob.glob(hwmonGpuTemplate)

assert len(hwmonMbPaths) == 1
assert len(hwmonGpuPaths) == 1

hwmonMb = hwmonMbPaths[0]
hwmonGpu = hwmonGpuPaths[0]

cpuTargetTemp = 55
gpuTargetTemp = 65

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
cpuPidController = PID(-0.03, -0.002, -0.0005,
        setpoint=cpuTargetTemp,
        output_limits=(0.0, 1.0),
        sample_time=0.5)

# fans
# default stop
fanExhaustTop = pwmFan(hwmonMb + "pwm1", 50, 255)
fanExhaustBack = pwmFan(hwmonMb + "pwm3", 80, 255)
fanCpu = pwmFan(hwmonMb + "pwm2", 70, 255)
fanIntakeTop = pwmFan(hwmonMb + "pwm5", 60, 255)
fanIntakeMid = pwmFan(hwmonMb + "pwm6", 70, 255)
fanIntakeBot = pwmFan(hwmonMb + "pwm4", 60, 255)

# sensors
cpuSensor = tempSensor(hwmonMb + 'temp2_input')
gpuSensor = tempSensor(hwmonGpu + 'temp1_input')

while True:
    cpuTemp = cpuSensor.read_temp()
    gpuTemp = gpuSensor.read_temp()
    cpuDelta = cpuPidController(cpuTemp)
    gpuDelta = gpuPidController(gpuTemp)
    avgDelta = 0.5*cpuDelta + 0.5*gpuDelta
    fanCpu.set_speed(cpuDelta)
    fanIntakeTop.set_speed(cpuDelta)
    fanIntakeMid.set_speed(gpuDelta)
    fanIntakeBot.set_speed(gpuDelta)
    fanExhaustTop.set_speed(avgDelta)
    fanExhaustBack.set_speed(avgDelta)
    #print(cpuTemp, gpuTemp, cpuDelta, gpuDelta)
    time.sleep(1)

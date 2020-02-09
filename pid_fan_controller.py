#!/usr/bin/env python3
from simple_pid import PID
import time

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

hwmonMb = '/sys/devices/platform/nct6775.2592/hwmon/hwmon0/'
hwmonGpu = '/sys/devices/pci0000:00/0000:00:03.1/0000:26:00.0/0000:27:00.0/0000:28:00.0/hwmon/hwmon3/'

# fans
fanExhaust = pwmFan(hwmonMb + "pwm1", 80, 255)
fanCpu = pwmFan(hwmonMb + "pwm2", 70, 255)
fanIntakeTop = pwmFan(hwmonMb + "pwm5", 80, 255)
fanIntakeMid = pwmFan(hwmonMb + "pwm6", 40, 255)
fanIntakeBot = pwmFan(hwmonMb + "pwm4", 80, 255)

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
    fanIntakeMid.set_speed(avgDelta)
    fanIntakeBot.set_speed(gpuDelta)
    fanExhaust.set_speed(avgDelta)
    #print(cpuTemp, gpuTemp, cpuDelta, gpuDelta)
    time.sleep(1)

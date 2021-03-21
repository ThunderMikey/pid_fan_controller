# Motivation

The current fan control software (fancontrol from lmsensors) and BIOS built-in “smart fan control” both use linear fan control logics. The fan speed is directly proportional to temperature source.

This leads to abrupt fan speed change on bursty workloads. Usually, the heat generated can be dissipated over time without ramping up fan speed. A linear fan speed controller has no idea of the speed at which temperature changes. A PID controller solves the problem by having a Proportional, Integral and Differential of the temperature history.


# Similar works

[https://github.com/jbg/macbookfan](https://github.com/jbg/macbookfan)


# Installation

I have created
[AUR pid-fan-controller](https://aur.archlinux.org/packages/pid-fan-controller/)
for Arch Linux users.

# PID tuning

* setpoint = 65
* output_limits = 0 - 1
* expect temperature at high load to be 80
  * difference = 85 - 65 = 20
* Kp = 0.03
* Ki = 0.002
* Kd = 0.0005


# Control logic

There are two main heat sources:

*   CPU
*   GPU

In order to better utilise the fans and reduce noise, 5 fans need to be controlled differently.

| fan               | control logic                       |
|-------------------|-------------------------------------|
| CPU fan           | CPU PID controller (sp=55)          |
| bottom intake fan | GPU PID controller (sp=65)          |
| middle intake fan | 50% CPU fan + 50% bottom intake fan |
| top intake fan    | CPU fan                             |
| exhaust           | middle intake fan                   |

# Profile the controller

It is important for the system performance that the PID controller is not taking too many CPU cycles.

  python3 -m cProfile pid_fan_controller.py


```
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.001    0.001   56.848   56.848 pid_fan_controller.py:2(<module>)
      285    0.000    0.000    0.008    0.000 pid_fan_controller.py:18(set_speed)
      114    0.000    0.000    0.056    0.000 pid_fan_controller.py:33(read_temp)
       57   56.781    0.996   56.781    0.996 {built-in method time.sleep}
      114    0.000    0.000    0.001    0.000 PID.py:66(__call__)
      228    0.000    0.000    0.000    0.000 PID.py:5(_clamp)
```

We can see the logs from cProfile built-in Python that:

*   The controller spent 99.88% time sleeping (56.781/56.848)
*   There are 57 iterations of always True loop
    *   57 executions of sleep
    *   114 (57*2 temp sensors) executions of read_temp
    *   285 (57*5 fans) execution of set_speed
    *   114 (57*2 PID controllers) PID read calls
    *   228 (114*double sampling rate) PID calculations. By the time this profiling was done, the PID controllers had sample_time set to be 0.5 seconds.

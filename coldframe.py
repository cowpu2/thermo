import time
import datetime
import os
from w1thermsensor import W1ThermSensor
import RPi.GPIO as GPIO
##  ============================================================

##  GPIO Setup
##  Define GPIO pins for relays - w1thermsensor takes care of pin 4
light_pin = 36  # controls lamps
fan_pin = 38  # controls exterior ventilation fan


def GPIOsetup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(light_pin, GPIO.OUT)
    GPIO.setup(fan_pin, GPIO.OUT)
    return ()


#  Identify the sensors, assign them to locations, and get temp values
def GetRpiTemp():  #  Get onboard temp of RPI
    rpi = os.popen('vcgencmd measure_temp').readline()
    rpi = rpi.replace("temp=", " ")
    rpi = rpi.replace("'C\n", " ")
    rpi = (float(rpi) * 1.8) + 32
    return rpi


def GetTemps():
    for sensor in W1ThermSensor.get_available_sensors():
        sensor.set_precision(10)  # Read precision, not print precision - 9-12 are only acceptable values
        try:
            sand_1_id = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "041701f825ff")
            Sand_temp = sand_1_id.get_temperature(W1ThermSensor.DEGREES_F)
        except W1ThermSensorError(NoSensorFoundError) as e:  # not using e for anything at moment but might later
            Sand_temp = "NA"
            pass
        try:
            soil_2_id = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "031701d060ff")
            Soil_temp = soil_2_id.get_temperature(W1ThermSensor.DEGREES_F)
        except W1ThermSensorError as e:
            Soil_temp = "NA"
            pass
        try:
            air_3_id = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "0316c2d27eff")
            Air_temp = air_3_id.get_temperature(W1ThermSensor.DEGREES_F)
        except W1ThermSensorError as e:
            Air_temp = "NA"
            pass
        try:
            outside_4_id = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "0316c2d810ff")
            Outside_temp = outside_4_id.get_temperature(W1ThermSensor.DEGREES_F)
        except W1ThermSensorError as e:
            Outside_temp = "NA"
            pass

        return Sand_temp, Soil_temp, Air_temp, Outside_temp


##  ------------------------------------------------------------
##  Define temperatures and activity states
ThresholdTemp = int(75)
MarginCool = 10
MarginHeat = 10

SleepTime = 300

TempNone = 0
TempHeat = 1
TempCool = 2
##  ------------------------------------------------------------


##  ============================================================
##  Heat and cooling controls
def ThermaLogic():
    Sand_temp, Soil_temp, Air_temp, Outside_temp = GetTemps()
    if Air_temp > (ThresholdTemp + MarginCool):
        GPIO.output(light_pin, 1)
        GPIO.output(fan_pin, 0)
        TempStatus = TempCool
    elif Sand_temp < (ThresholdTemp - MarginHeat):
        GPIO.output(light_pin, 0)
        GPIO.output(fan_pin, 1)
        TempStatus = TempHeat
    else:
        GPIO.output(light_pin, 1)
        GPIO.output(fan_pin, 1)
        TempStatus = TempNone
    return TempStatus
# ------------------------------------------------------------


#  ============================================================
def DataLogger():  #  Create and write to log file
    TempStatus = ThermaLogic()
    rpi_temp = round(float(GetRpiTemp()), 1)
    Sand_temp, Soil_temp, Air_temp, Outside_temp = GetTemps()  # Get values from get_temps individually to
    now = datetime.datetime.now()                              # avoid 4 values in one field
    logstampdate = now.strftime("%Y-%m-%d")
    logstamptime = now.strftime("%X")
    fname = "ColdFrame_" + str(logstampdate) + ".dat"
    logfile = open(fname, 'a')
    logdatastring = str(round(Sand_temp, 2)) + ", " + str(round(Soil_temp, 2)) + ", " + str(
        round(Air_temp, 2)) + ", " + str(round(Outside_temp, 2)) + ", " + str(rpi_temp) + ", " + str(TempStatus)
    logfilestring = str(logstampdate) + ", " + str(logstamptime) + ", " + str(logdatastring) + "\n"
    logfile.write(logfilestring)
    logfile.close()
    return logfilestring

try:
    while True:
        GPIOsetup()
        GetRpiTemp()
        ThermaLogic()
        DataLogger()
        print(DataLogger())
        time.sleep(SleepTime)
except KeyboardInterrupt:
    print('keyboard interrupted')
finally:
    GPIO.cleanup()
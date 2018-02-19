import time
import datetime
from w1thermsensor import W1ThermSensor
import RPi.GPIO as GPIO

##  ============================================================
##  Define temperatures and activity states
ThresholdTemp = int(75)
MarginCool = 10
MarginHeat = 10
ReadingInterval = 30

TempNone = 0
TempHeat = 1
TempCool = 2
##  ------------------------------------------------------------

##  ============================================================
##  GPIO Setup
##  Define GPIO pins for relays - w1thermsensor takes care of pin 4
light_pin = 13  # controls lamps
fan_pin = 15  # controls exterior ventilation fan


def GPIOsetup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(light_pin, GPIO.OUT)
    GPIO.setup(fan_pin, GPIO.OUT)
    return ()


##  ------------------------------------------------------------
##  ============================================================
##  Identify the sensors, assign them to locations, and get temp values

def GetRpiTemp():  ##  Get onboard temp of RPI
    res = os.popen('vcgencmd measure_temp').readline()
    return res.replace("temp=","").replace("'C\n","")


def get_temps():
    for sensor in W1ThermSensor.get_available_sensors():
        sensor.set_precision(10)  # Read precision, not print precision - 9-12 are only acceptable values
    # print("Sensor %s has temperature %.2f" % (sensor.id, sensor.get_temperature(W1ThermSensor.DEGREES_F)))
    sand_1_id = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "041701f825ff")
    soil_2_id = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "031701d060ff")
    air_3_id = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "0316c2d27eff")
    outside_4_id = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "0316c2d810ff")
    Sand_temp = sand_1_id.get_temperature(W1ThermSensor.DEGREES_F)
    Soil_temp = soil_2_id.get_temperature(W1ThermSensor.DEGREES_F)
    Air_temp = air_3_id.get_temperature(W1ThermSensor.DEGREES_F)
    Outside_temp = outside_4_id.get_temperature(W1ThermSensor.DEGREES_F)
    # print("Sand =", Sand_temp)
    # print("Soil =", Soil_temp)
    # print("Air =", Air_temp)
    # print("Outside =", Outside_temp)
    return Sand_temp, Soil_temp, Air_temp, Outside_temp


##  ------------------------------------------------------------
##  ============================================================
##  Heat and cooling controls
if Sand_temp > (ThresholdTemp + MarginCool):
    GPIO.output(light_pin, 1)
    GPIO.output(fan_pin, 0)
    TempStatus = TempCool
elif Sand_temp < (ThresholdTemp - MarginHeat):
    GPIO.output(light_pin, 0)
    GPIO.output(fan_pin, 1)
    TempStatus = TempHeat
else:
    GPIO.output(light_pin, 0)
    GPIO.output(fan_pin, 0)
    TempStatus = TempNone


##  ------------------------------------------------------------
##  ============================================================
##  Celsius to Fahrenheit conversion - just for the RPI onboard values
##  1Wthermosensor does it for the ds18b20s
def tempconversion()  -   just do this in the function and have it returned
##  ============================================================
##  Create and write to log file
def datalogger():
    Sand_temp, Soil_temp, Air_temp, Outside_temp = get_temps()  # Get values from get_temps individually to
    logfile = open('ds18B20_log.txt', 'a')  # avoid 4 values in one field
    now = datetime.datetime.now()
    logstampdate = now.strftime("%Y/%m/%d")
    logstamptime = now.strftime("%X")
    logdatastring = str(round(Sand_temp, 2)) + ", " + str(round(Soil_temp, 2)) + ", " + str(
        round(Air_temp, 2)) + ", " + str(round(Outside_temp, 2))
    logfilestring = str(logstampdate) + ", " + str(logstamptime) + ", " + str(logdatastring) + "\n"
    logfile.write(logfilestring)
    logfile.close()
    return logfilestring


#  This needs to go in datalogger somewhere
#  myTempPiC = round(float(GetRpiTemp()),1)


##  Need a timestamp on filename and need to restart script every 24 so file size doesn't get obscene
##  ------------------------------------------------------------





try:
    while True:
        # print(get_temps())
        GPIOsetup()
        # heat_fan_control()
        # vent_fan_control()
        datalogger()
        print(datalogger())
        time.sleep(60)
except KeyboardInterrupt:
    print('keyboard interrupted')
    # finally:
    #     GPIO.cleanup()

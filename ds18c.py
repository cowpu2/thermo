import time
import datetime
# noinspection PyUnresolvedReferences
import RPi.GPIO as GPIO
# import urllib2

# Identify which pin controls the relay
heat_pin = 13  # controls heat lamp and heat_fan
vent_pin = 15  # controls exterior ventilation fan


def GPIOsetup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(heat_pin, GPIO.OUT)
    GPIO.setup(vent_pin, GPIO.OUT)
    return ()


# noinspection PyGlobalUndefined
def heat_on():
    GPIO.output(heat_pin, 0)
    global heat_status  # Assign a value to variable to indicate fan activity - used values so that
    heat_status = "1"   # thingspeak can display it in graph -  global so datalogger can use it
    print("Heat On" + " " + str(heat_status))
    return heat_status


def heat_off():
    GPIO.output(heat_pin, 1)
    global heat_status
    heat_status = "0"
    print("Heat Off" + " " + str(heat_status))
    return heat_status


# noinspection PyGlobalUndefined
def vent_on():
    GPIO.output(vent_pin, 0)
    global vent_status
    vent_status = "1"
    print("Vent on" + " " + str(vent_status))
    return vent_status


def vent_off():
    GPIO.output(vent_pin, 1)
    global vent_status
    vent_status = "0"
    print("Vent Off" + " " + str(vent_status))
    return vent_status

#  DS18B20 sensor data
temp_sensor = '/sys/bus/w1/devices/28-0316c2d810ff/w1_slave'

# Temperature check point
min_temp = float(75)  # light runs off of this temp
max_temp = float(80)


def temp_raw():
    f = open(temp_sensor, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp():
    lines = temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = temp_raw()

    temp_output = lines[1].find('t=')

    if temp_output != -1:
        temp_string = lines[1].strip()[temp_output + 2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_f


def heat_fan_control():

    if read_temp() < min_temp:
        heat_on()
        print("Heat Threshold" + " " + str(min_temp) + " : " + "Status =  " + str(heat_status))

    elif read_temp() > min_temp:
        heat_off()
        print("heat_status - " + str(heat_status))

    return read_temp()


def vent_fan_control():
    if read_temp() > max_temp:
        vent_on()
        print("Vent Threshold - " + str(max_temp) + " : " + "Status = " + str(vent_status))

    elif read_temp() < max_temp:
        vent_off()
        print("vent_status - " + str(vent_status))

    return ()


def datalogger():  # Bring in relay status here

    logfile = open('ds1820_log.txt', 'a')
    now = datetime.datetime.now()
    logstampdate = now.strftime("%Y/%m/%d")
    logstamptime = now.strftime("%X")
    logdatastring = str(read_temp()) + ", " + str(heat_status) + ", " + str(vent_status)
    logfilestring = str(logstampdate) + ", " + str(logstamptime) + ", " + str(logdatastring) + "\n"
    logfile.write(logfilestring)
    # print(logfilestring)
    logfile.close()
    # TempF = read_temp()
    # baseURL = 'https://api.thingspeak.com/update?api_key=QLWZLZSEQPTX3VNJ'
    # tspeak = urllib2.urlopen(baseURL + "&field1=%s&field2=%s&field3=%s" % (TempF, heat_status, vent_status))
    # print(tspeak.read())
    # tspeak.close()

    return logfilestring


while True:
    # print(read_temp())
    GPIOsetup()
    heat_fan_control()
    vent_fan_control()
    datalogger()
    print(datalogger())
    time.sleep(5)

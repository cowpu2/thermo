# !/usr/bin/python
# noinspection PyUnresolvedReferences
import RPi.GPIO as GPIO
# noinspection PyUnresolvedReferences
import Adafruit_DHT
import time
import datetime
import urllib2

# Identify which pin controls the relay
light_pin = 13  # controls heat lamp and heat_fan
vent_fan_pin = 15  # controls exterior ventilation fan


def GPIOsetup():
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(light_pin, GPIO.OUT)
	GPIO.setup(vent_fan_pin, GPIO.OUT)
	return ()


# Get temp from DHT11
def getdhttemperature():
	#   Check for valid data immediately and loop back if its bad
	while True:
		rh, t = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 4)
		if t:

			break
		else:
			continue
	return str(rh), str(t)


def heat_fan_on():
	GPIO.output(light_pin, 0)
	global fan_status # Assign a value to variable to indicate fan activity - used values so that
	fan_status = "1"  # thingspeak can display it in graph
	print("Heat On")
	return fan_status


def heat_fan_off():
	GPIO.output(light_pin, 1)
	fan_status = "0"
	return ()


def vent_fan_on():
	GPIO.output(vent_fan_pin, 0)
	fan_status = "-1"
	print("Vent on")
	return ()


def vent_fan_off():
	GPIO.output(vent_fan_pin, 1)
	fan_status = "0"
	print("Vent off")
	return ()

# defined dht_temp globally so that we could use it in datalogger - line 62
dht_temp = 900
RH = 199

# noinspection PyUnboundLocalVariable,PyUnboundLocalVariable
def convFahr():
	rh, t = getdhttemperature()

	try:  # Error checking here is probably redundant but left in rather than jacking something up
		if t is not None:
			global dht_temp
			global RH
			dht_temp = float(t) * 1.8 + 32
			F = str(dht_temp) + "F"
			C = str(t) + "C"
			RH = str(rh)

	except ValueError:
		dht_temp = 0
		print(str(dht_temp) + " dht error")

	return dht_temp, F, C, RH, t


# Temperature check point
min_temp = float(75)  # light runs off of this temp as well
max_temp = float(80)

# noinspection PyShadowingNames,PyShadowingNames
def heat_fan_control():
	dht_temp, F, C, RH, t = convFahr()  # Put these in the order that they are used!!!!!!!!!!!!!!!!

	if dht_temp < min_temp:
		heat_fan_on()
		print(dht_temp)
		print("Heat Threshold" + " " + str(min_temp))

	elif dht_temp > min_temp:
		heat_fan_off()
		print(dht_temp)

	return dht_temp


# noinspection PyShadowingNames,PyShadowingNames
def vent_fan_control():
	dht_temp, F, C, RH, t = convFahr()  # Put these in the order that they are used!!!!!!!!!!!!!!!!

	if dht_temp > max_temp:
		vent_fan_on()
		print(dht_temp)
		print("Vent Threshold" + " " + str(max_temp))

	elif dht_temp < max_temp:
		vent_fan_off()
		print(dht_temp)

	return()


# def datalogger():
#
# 	logfile = open('thermo_log.txt', 'a')
# 	now = datetime.datetime.now()
# 	timestamp = now.strftime("%Y/%m/%d %H:%M")
# 	global logstampdate
# 	global logstamptime
# 	logstampdate = now.strftime("%Y/%m/%d")
# 	logstamptime = now.strftime("%X")
# 	printstring = str(timestamp) + " " + str(dht_temp) + " F" + " " + str(RH) + "% RH" + "\n"
# 	print(printstring)
# 	logfilestring = str(logstampdate) + ", " + str(logstamptime) + ", " + str(dht_temp) + ", " + str(RH) + "\n"
# 	logfile.write(logfilestring)
# 	#print(logfilestring)
# 	logfile.close()
# 	baseURL = 'https://api.thingspeak.com/update?api_key=QLWZLZSEQPTX3VNJ'
# 	tspeak = urllib2.urlopen(baseURL + "&field1=%s&field2=%s&field3=%s" % (RH, dht_temp, fan_status))
# 	print(tspeak.read())
# 	tspeak.close()
#
# 	return()


def main():

	GPIOsetup()
	getdhttemperature()
	heat_fan_control()
	vent_fan_control()
	#datalogger()
	time.sleep(600)

	return ()

try:

	while True:
		main()

except KeyboardInterrupt:
	pass

finally:

	print("Finish")
	GPIO.cleanup()

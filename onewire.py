from w1thermsensor import W1ThermSensor

for sensor in W1ThermSensor.get_available_sensors():
    print("Sensor %s has temperature %.2f" % (sensor.id, sensor.get_temperature(W1ThermSensor.DEGREES_F)))

sensor3_id = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "0316c2d27eff")
temperature_in_fahrenheit = sensor3_id.get_temperature(W1ThermSensor.DEGREES_F)
print("Sensor 3 Temp F. =", temperature_in_fahrenheit)


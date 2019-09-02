#!/usr/bin/python

#git committed

# Set up imports
import RPi.GPIO as GPIO
import RPI_ADC0832
import Adafruit_DHT
import sys
import time
import mysql.connector
import datetime
import plotly.plotly as py
import plotly.graph_objs as go

# Set up the Raspberry Pi GPIO pins ================
GPIO.setmode(GPIO.BCM)
# Light Photocell ================================
GPIO.setup(4,GPIO.IN)
# Humidity ================================
GPIO.setup(11,GPIO.IN)
# Temperature ================================
GPIO.setup(18,GPIO.IN)
# LED Status Light ================================
GPIO.setup(26,GPIO.OUT)
# DC Pump ================================
GPIO.setup(23,GPIO.OUT)
# Set DC Pump as "OFF"
GPIO.output(23,GPIO.LOW)
# Reads DateTime info from the PlotlyDatabase.

# Analog->Digital MOISTURE SETUP ================================
# Set up moisture 1 sensor
adc = RPI_ADC0832.ADC0832()
adc.csPin = 17
adc.clkPin = 27
adc.doPin = 22
adc.diPin - 22
# Set up moisture 2 sensor
adc2 = RPI_ADC0832.ADC0832()
adc2.csPin = 5
adc2.clkPin = 6
adc2.doPin = 13
adc2.diPin = 13
# Go ahead and set up the second adc, given it doesn't use default values
GPIO.setup(adc2.csPin, GPIO.OUT, initial = GPIO.HIGH)
GPIO.setup(adc2.clkPin, GPIO.OUT, initial=GPIO.LOW)


# Function which fetches the X values of data from a database
def readXData(name):
	f = '%Y-%m-%d %H:%M:%S'
	# Create a dictionary which will redirect according to what we need
	switch = {"LastWaterX":0, "LastWaterY":1, "TempX":2, "TempY":3, "HumidityX":4, "HumidityY":5}
	# If we didn't get a hit, break
	index = switch.get(name, "Invalid Column")
	if (index == "Invalid Column"):
		 return
	# Set up the MYSQL connection
	mydb = mysql.connector.connect(host = "localhost", user = "root", password = "tacocat", database = "PlantData")
	mycursor = mydb.cursor()
	# Get the data
	mycursor.execute("SELECT * FROM PlotlyData")
	# Get the row value
	row = mycursor.fetchone()
	# Create an empty list to store our values in
	values = []
	# Loop through all rows, compiling any row that isn't empty
	while row is not None:
		#print (row[index])
		temp = (row[index])
		temp = temp.strftime(f)
#		print(temp)
		values.append(temp)
		row = mycursor.fetchone()
	# Close the connection
#	print(values)
	mycursor.close()
	mydb.close()
	return values
# Reads Int/Float values from the Plotly database.
# Function that fetches the Y values from the database
def readYData(name):
	f = '%Y-%m-%d %H:%M:%S'
	# Create a dictionary which will redirect according to what we need
	switch = {"LastWaterX":0, "LastWaterY":1, "TempX":2, "TempY":3, "HumidityX":4, "HumidityY":5}
	# If we didn't get a hit, break
	index = switch.get(name, "Invalid Column")
	if (index == "Invalid Column"):
		 return
	# Set up the MYSQL connection
	mydb = mysql.connector.connect(host = "localhost", user = "root", password = "tacocat", database = "PlantData")
	mycursor = mydb.cursor()
	# Get the data
	mycursor.execute("SELECT * FROM PlotlyData")
	# Get the row value
	row = mycursor.fetchone()
	# Create an empty list to store our values in
	values = []
	# Loop through all rows, compiling any row that isn't empty
	while row is not None:
		#print (row[index])
		temp = (row[index])
#		print(temp)
		values.append(temp)
		row = mycursor.fetchone()
	# Close the connection
#	print(values)
	mycursor.close()
	mydb.close()
	return values

# Main method of the program
def run():
    print("===============================================================================================================================================================================================================================")
    print("")
    print("===================================================")
    print("Program began running at %s" % datetime.datetime.today())
    print("===================================================")
    print("")
    print("============")
    print("[Heartbeat:] \t\t Setting Up")
    # 1. Set up the MySQL and Plotly Variables
    mydb = mysql.connector.connect(host = "localhost", user = "root", password = "tacocat", database = "PlantData")
    mycursor = mydb.cursor()
    sql = "INSERT INTO SensorData1 (light, Temp, Humidity, MoistureDigital, MoistureAnalog) VALUES (%s,%s,%s,%s,%s)"
    sqlPlotly = "INSERT INTO PlotlyData (LastWaterY, TempY, HumidityY) VALUES (%s,%s,%s)"
    sqlFetch = "SELECT * FROM PlotlyData"
    # 2. Load the MySQL variables into their arrays
    control_moisture_x = readXData("ControlMoistureX")
    control_moisture_y = readYData("ControlMoistureY")
    auto_moisture_x = readXData("AutoMoistureX")
    auto_moisture_y = readYData("AutoMoistureY")
    # Water
    last_water_x = readXData("LastWaterX")
    last_water_y = readYData("LastWaterY")
    # Temperature
    temp_x = readXData("TempX")
    temp_y = readyYData("TempY")
    # Humidity
    humidity_x = readXData("HumidityX")
    humidity_y = readYData("HumidityY")
    # 3. Begin program
    print("[Heartbeat:] \t\t Running")
    print(datetime.datetime.now())
    print("============")
    print("")

    while True:
        # =========[LIGHT SETUP]==========
        # Light sensor, 0 reading is light, 1 reading is dark
        Light = GPIO.input(4)
        print("========")
        print ("[Light:] \t\t %s" % GPIO.input(4))
        print("========")
        print("")
        # Moisture Left: Autowatering ================================
        auto_moisture_reading = str(adc.read_adc(0))
        # if (Moisture reading is bad):

        # Moisture Right: JustReading ================================
        control_moisture_reading = str(adc2.read_adc(0))

        # =========[TEMP/HUMIDITY SETUP]==========
        humidity, temperature = Adafruit_DHT.read_retry(11,18)
        print("===============")
        Temp = float("{0:0.1f}".format(temperature))
        Humidity = float("{0:0.1f}".format(humidity))
        if humidity is not None and temperature is not None:
            print("[Temperature:] \t\t Temp={0:0.1f}*C %".format(temperature))
            print("[Humidity:] \t\t Humidity={0:0.1f}*C %".format(humidity))
            # print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
        else:
            print('[Temp/Humidity:] \t\t Failed to get reading. Try again!')
        print("===============")
        print('')
        # Add values to your y array for plotting later
        temp_y.append(Temp)
        humidity_y.append(Humidity)

        # =========[MYSQL INFORMATION]============
        val = (Light, Temp, Humidity, Moisture1, "<Moisture2>")
        valPlotly = (last_water/60, Temp, Humidity)
        mycursor.execute(sql,val)
        mycursor.execute(sqlPlotly, valPlotly)
        mydb.commit()
        print("========")
        print("[MySQL:] \t\t Records Inserted")
        print("========")
        print("")    

        # =========[PLOTLY INFORMATION]===========
    	#Fetch the datetimes for each data
        last_water_x = readXData("LastWaterX")
        temp_x = readXData("TempX")
        humidity_x = readXData("HumidityX")
        print("=================")
        # print("[Plotly:] X Vals: \t %s" % last_water_x)
        # print("[Plotly:] Y Vals: \t %s" % last_water_y)
        print("=================")
        print("")
        time_watered = go.Scatter(
          x = last_water_x,
          y = last_water_y
        )
        temperature = go.Scatter(
          x = temp_x,
          y = temp_y
        )
        humidity =  go.Scatter(
          x = humidity_x,
          y = humidity_y
        )
        data = [time_watered, temperature, humidity]
        py.plot(data, filename = 'avg-watered-time', auto_open = False)
        print("===============================================================================================================================================================================================================================")

        # =========[REST]=========
        time.sleep(900)

run()
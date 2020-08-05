import serial
import mysql.connector


ser = serial.Serial('/dev/ttyACM0', 9600)
cnx = mysql.connector.connect(user='franco', password='mysql', database='card_game')
cursor = cnx.cursor()

while True:
	data = ser.readline()[:-2]
	if(data):
		print data
		query = "SELECT power, name FROM card WHERE id_card = " + str(data)
		cursor.execute(query)

		for(power, name) in cursor:
			print("{} has {} units of power!".format(name, power))
			#ser.write(power)

	
cursor.close()
cnx.close()

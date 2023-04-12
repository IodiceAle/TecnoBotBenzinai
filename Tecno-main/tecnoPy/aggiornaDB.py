import mysql.connector
import csv

mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
cursor = mydb.cursor()

csv_data = csv.reader(file('anagrafica_impianti_asttivi.csv.csv'))
for row in csv_data:
    cursor.execute('INSERT INTO impianto(names,classes, mark ) VALUES("%s", "%s", "%s")', row)
#close the connection to the database.
mydb.commit()
cursor.close()
print ("Done")
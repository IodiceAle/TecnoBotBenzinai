import threading
import time
import mysql.connector
import csv

class MyThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            now = time.localtime()
            if now.tm_hour == 8 and now.tm_min == 10:
                self.insert_data_from_csv()
                # Wait for 24 hours before checking again
                time.sleep(24 * 60 * 60)
            else:
                # Wait for 10 seconds before checking again
                time.sleep(10)

    def insert_data_from_csv(self):
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        cursor = mydb.cursor()

        with open('anagrafica_impianti_attivi.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                cursor.execute('INSERT INTO impianto(names,classes, mark ) VALUES("%s", "%s", "%s")', row)
            mydb.commit()
            cursor.close()
        
    
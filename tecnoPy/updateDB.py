import threading
import time
import mysql.connector
import csv
import botOSM

class MyThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.skipped_ids = []

    def run(self):
        while True:
            now = time.localtime()
            #if now.tm_hour == 8 and now.tm_min == 10:
            self.insert_data_from_csv()
                # Wait for 24 hours before checking again
            time.sleep(24 * 60 * 60)
            #else:
                # Wait for 10 seconds before checking again
            #time.sleep(10)

    def insert_data_from_csv(self):
        botOSM.Telegram.downloadBenziani(self)
        botOSM.Telegram.downloadPrezzi(self)
        
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_benzinai"
        )
        cursor = mydb.cursor()
        
        # drop foreign key constraint on prezzo table
        cursor.execute('ALTER TABLE prezzo DROP FOREIGN KEY prezzo_ibfk_1')
        # truncate impianto table
        cursor.execute('TRUNCATE TABLE impianto')
        # recreate foreign key constraint on prezzo table
        cursor.execute('ALTER TABLE prezzo ADD CONSTRAINT prezzo_ibfk_1 FOREIGN KEY (idImpianto) REFERENCES impianto (idImpianto)')

        with open('anagrafica_impianti_attivi.csv',encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            # Skip the first 2 row
            next(csv_reader)
            next(csv_reader)
            
            for row in csv_reader:
                # check if any of the fields in the row are "NULL" or ""
                if "NULL" in row or "" in row:
                    self.skipped_ids.append(row[0])  # add ID to list of skipped IDs
                    continue  # skip this row
                #get data from row
                idI=int(row[0])
                gest=row[1]
                band=row[2]
                tipoI=row[3]
                nomeI=row[4]
                ind=row[5]
                com=row[6]
                prov=row[7]
                lat=row[8]
                long=row[9]
                #insert in db
                cursor.execute('INSERT INTO impianto (idImpianto, gestore, bandiera, tipoImpianto, nomeImpianto, indirizzo, comune, provincia, latitudine, longitudine) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (idI, gest, band, tipoI, nomeI, ind, com, prov, lat, long))
            mydb.commit()
            cursor.close()
        
    
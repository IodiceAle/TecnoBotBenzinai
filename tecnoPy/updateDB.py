import threading
import time
import mysql.connector
import csv
import botOSM

class MyThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.skipped_ids = []
        self.benzina=["Benzina","Benzina WR 100","Benzina Plus 98","Benzina speciale","Benzina Energy 98 ottani","Blue Super","HiQ Perform+","F101","F-101","V-Power","Benzina Shell V Power","Benzina 100 ottani","Benzina 102 Ottani","R100","Verde speciale"]
        self.gasolio=["Gasolio","Gasolio Alpino","Gasolio speciale","Gasolio Premium","Gasolio Ecoplus","Gasolio Oro Diesel","Gasolio Gelo","Gasolio artico","Gasolio Energy D","Gasolio Prestazionale","Gasolio Plus"]
        self.diesel=["Diesel","Blue Diesel","Hi-Q Diesel","Excellium Diesel","Supreme Diesel","DieselMax","GP DIESEL","Diesel Shell V Power","E-DIESEL","Diesel e+10","S-Diesel","V-Power Diesel","HVOlution","HVO100"]
        self.metano=["Metano","GNL","L-GNC"]

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
        # botOSM.downloadBenziani()
        
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="benziani"
        )
        cursor = mydb.cursor()
        
        cursor.execute('TRUNCATE TABLE prezzi')
        # drop foreign key constraint on prezzo table
        try:
            cursor.execute('ALTER TABLE prezzi DROP FOREIGN KEY prezzi_ibfk_1')
        except:
            print("chiave già eliminata")
        # truncate impianto table
        cursor.execute('TRUNCATE TABLE impianto')
        # recreate foreign key constraint on prezzo table
        cursor.execute('ALTER TABLE prezzi ADD CONSTRAINT prezzi_ibfk_1 FOREIGN KEY (idImpianto) REFERENCES impianto (idImpianto)')

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
                cursor.execute('INSERT INTO impianto (idImpianto, Gestore, Bandiera, tipoImpianto, nomeImpianto, Indirizzo, Comune, Provincia, Latitudine, Longitudine) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (idI, gest, band, tipoI, nomeI, ind, com, prov, lat, long))
            mydb.commit()
            cursor.close()
            self.insert_data_from_csv2()
            
    def insert_data_from_csv2(self): 
        # botOSM.downloadPrezzi()
        
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="benziani"
        )
        cursor = mydb.cursor()
    # Truncate the 'prezzo' table
        cursor.execute('TRUNCATE TABLE prezzi')

        # Insert data from 'prezzo_alle_8.csv'
        with open('prezzo_alle_8.csv',encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            # Skip the header row
            next(csv_reader)
            next(csv_reader)
            
            for row in csv_reader:
                # Check if the ID is in the skipped_ids list
                idI = int(row[0])
                if row[0] in self.skipped_ids:
                    continue  # skip this row
                # if int(row[3])!=1:
                #     continue
                # Get data from row
                if row[1] in self.benzina:
                    tipoC = "benzina"
                if row[1] in self.gasolio:
                    tipoC = "gasolio"
                if row[1] in self.diesel:
                    tipoC = "diesel"
                if row[1] in self.metano:
                    tipoC = "metano"
                if row[1] == "GPL":
                    tipoC = "gpl"
                
                # descC = row[2]
                prezzo = float(row[2].replace(',', '.'))  # replace comma with dot as decimal separator
                
                if tipoC=="GPL":
                    if prezzo<=0.3:
                        continue
                
                if tipoC=="benzina":
                    if prezzo<=1.2:
                        continue
                    
                if tipoC=="gasolio":
                    if prezzo<=1.2:
                        continue
                
                if tipoC=="diesel":
                    if prezzo<=1.0:
                        continue
                    
                if tipoC=="metano":
                    if prezzo<=0.3:
                        continue
                
                # Insert into database
                try:
                    cursor.execute('INSERT IGNORE INTO prezzi ( descCarburante, tipoCarburante, prezzo, idImpianto) VALUES (%s, %s, %s, %s)', (row[1],tipoC, prezzo, idI))
                except:
                    print("An exception occurred")
                
        mydb.commit()
        cursor.close()
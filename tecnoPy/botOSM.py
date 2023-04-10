import requests
import csv
import prezzi
import benzinai

class Telegram:
    
    def __init__(self,token):
        self.token=token
        self.url="https://api.telegram.org/bot"
        
    def getUpdates(self,update_id=-1):
        if(update_id==-1):
            urlUpdate=self.url+self.token+"/getUpdates"
            response=requests.get(urlUpdate)
            print(response);
        else:
            urlUpdate=self.url+self.token+"/getUpdates?offset={update_id}"
            response=requests.get(urlUpdate)
            rep=response.json()
        return response.json()
        
    def get_chat_and_update_ids(self,response):
        chat_id = response["result"][0]["message"]["chat"]["id"]
        update_id = response["result"][0]["update_id"]
        return chat_id, update_id
    
    def downloadPrezzi(self,url):
        """Download the CSV data from the URL and save it to a file."""
        response = requests.get(url)
        with open('prezzo_alle_8.csv', 'wb') as f:
            f.write(response.content)
        """Read and process the CSV data from the file into an array."""
        recordPrezzi = []
        with open("prezzo_alle_8.csv", newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            # Skip the header row
            next(reader)
            next(reader)
            for row in reader:
                # Create a new Record object for each row and append it to the list
                record = prezzi.prezzo(row[0], row[1], float(row[2].replace(',', '.')), row[3], row[4])
                recordPrezzi.append(record)
        return recordPrezzi

    def downloadBenziani(self,url):
        """Download the CSV data from the URL and save it to a file."""
        response = requests.get(url)
        with open('anagrafica_impianti_attivi.csv', 'wb') as f:
            f.write(response.content)
        """Read and process the CSV data from the file into an array."""
        recordImpianti = []
        with open("anagrafica_impianti_attivi.csv", newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            # Skip the header row
            next(reader)
            next(reader)
            for row in reader:
                # Create a new Record object for each row and append it to the list
                record = benzinai.Impianto(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
                recordImpianti.append(record)
        return recordImpianti
# bot_token = "6295982819:AAH6Ao3BtUtzFbYoYRcyfZMXv9__9HT75oo"


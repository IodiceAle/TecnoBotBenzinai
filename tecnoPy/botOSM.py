import requests
import csv
import prezzi
import benzinai

import threading
import time
import mysql.connector

# Set your Telegram bot token here
bot_token = "6295982819:AAH6Ao3BtUtzFbYoYRcyfZMXv9__9HT75oo"

# Function to send a message to a Telegram chat using the bot API
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

# Define the handle_messages function
def handle_messages():
    # Set the initial offset to 0
    offset = 0
    # Set the initial flag for waiting for a response to False
    waiting_for_response = False
    # Set the initial dictionary for user responses to an empty dictionary
    user_responses = {}
    # Set the list of parameters to ask
    params = [
        "nome",
        "Quanto consuma il tuo veicolo in litri per 1 km?",
        "Quanta capacità ha il tuo serbatoio?",
        "Che tipo di carburante usi?",
        "Quanta strada puoi fare?",
        "Dove sei ora?"
    ]
    # Set the initial index of the parameter we are currently asking for to 0
    param_index = 0
    
    while True:
        # Set up the request payload
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        payload = {"offset": offset, "timeout": 30}
        response = requests.get(url, params=payload)
        # Extract the response data as a JSON object
        data = response.json()
        
        # Check if we received any new messages
        if(data["ok"]==True):
            if len(data["result"]) > 0:
                for result in data["result"]:
                    # Extract the chat ID and message text from the message
                    chat_id = result["message"]["chat"]["id"]
                    message_text = result["message"]["text"]
                    
                    if waiting_for_response:
                        # We are waiting for a response from the user
                        if message_text != "":
                            user_responses[params[param_index]] = message_text
                            param_index += 1
                        if param_index == len(params):
                            # We have received all the necessary responses
                            # Insert the responses into the database
                            # query = "INSERT INTO users (chat_id, user_id, nome, consumo, capacita, carburante, strada, posizione) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                            # values = (chat_id, result["message"]["from"]["id"], user_responses["nome"], user_responses["Quanto consuma il tuo veicolo in litri per 1 km?"], user_responses["Quanta capacità ha il tuo serbatoio?"], user_responses["Che tipo di carburante usi?"], user_responses["Quanta strada puoi fare?"], user_responses["Dove sei ora?"])
                            # cursor = db.cursor()
                            # Execute the query and commit the changes
                            # cursor.execute(query, values)
                            # db.commit()
                            # Send a confirmation message
                            send_message(chat_id, "Grazie per aver fornito le informazioni richieste. Se hai bisogno di aiuto in futuro, non esitare a contattarci.")
                            # Reset the flag for waiting for a response and the dictionary for user responses
                            waiting_for_response = False
                            user_responses = {}
                            param_index = 0
                        else:
                            # We still need to ask for more parameters
                            send_message(chat_id, params[param_index])
                            
                    elif message_text == "Sono un nuovo utente":
                        # We have received the command to start asking for parameters
                        send_message(chat_id, "Ciao! Per iniziare, dimmi il tuo nome.")
                        # Set the flag for waiting for a response to True
                        waiting_for_response = True
                    else:
                        # We have received a message that we don't understand
                        if waiting_for_response:
                            # We are waiting for a response from the user
                            user_responses[params[param_index]] = message_text
                            param_index += 1
                            if param_index == len(params):
                                # We have received all the necessary responses
                                # Insert the responses into the database
                                # query = "INSERT INTO users (chat_id, user_id, nome, consumo, capacita, carburante, strada, posizione) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                                # values = (chat_id, result["message"]["from"]["id"], user_responses["nome"], user_responses["Quanto consuma il tuo veicolo in litri per 1 km?"], user_responses["Quanta capacità ha il tuo serbatoio?"], user_responses["Che tipo di carburante usi?"], user_responses["Quanta strada puoi fare?"], user_responses["Dove sei ora?"])
                                # cursor = db.cursor()
                                # Execute the query and commit the changes
                                # cursor.execute(query, values)
                                # db.commit()
                                # Send a confirmation message
                                send_message(chat_id, "Grazie per aver fornito le informazioni richieste. Se hai bisogno di aiuto in futuro, non esitare a contattarci.")
                                # Reset the flag for waiting for a response and the dictionary for user responses
                                waiting_for_response = False
                                user_responses = {}
                                param_index = 0
                            else:
                                # We still need to ask for more parameters
                                send_message(chat_id, params[param_index])
                        else:
                            # We are not waiting for a response from the user, and we don't understand the message
                            send_message(chat_id, "Non ho capito. Per iniziare, digita \"Sono un nuovo utente\".")

                            
                # Set the new offset to the ID of the last message we received plus 1
                offset = data["result"][-1]["update_id"] + 1
        # Wait for 5 seconds before checking for new messages again
        time.sleep(5)
    
def downloadPrezzi(self,url="https://www.mise.gov.it/images/exportCSV/prezzo_alle_8.csv"):
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

def downloadBenziani(self,url="https://www.mise.gov.it/images/exportCSV/anagrafica_impianti_attivi.csv"):
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
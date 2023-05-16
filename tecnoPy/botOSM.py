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
    waiting_for_response2 = False
    # Set the initial dictionary for user responses to an empty dictionary
    user_responses = {}
    # Set the list of parameters to ask
    paramsUt = [
        "Ciao! Per iniziare, dimmi il tuo nome.",
        "Che tipo di carburante usi?",
        "Quanta capacità ha il tuo serbatoio? LITRI",
        "Quanti KM riesci a fare con 1 LITRO?"
    ]
    
    params2 = [
        "Inviami la posizione o scrivendo dove ti trovi o con la posizione di Telegram.",
        "Quanto carburante devi fare? (1/4, 2/4, 3,4, 4/4 di pieno)"
    ]
    # Set the initial index of the parameter we are currently asking for to 0
    param_index = 0
    param_index2 = 0
    
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
                    
                    try:
                        message_text = result["message"]["text"]
                    except:
                        message_text = result["message"]["location"]
                    
                    if waiting_for_response2:

                            if message_text != "":
                                try:
                                    if result["message"]["location"]!="":
                                        user_responses[params2[param_index2]] = str(result["message"]["location"]["latitude"])+","+str(result["message"]["location"]["longitude"])
                                        param_index2 += 1
                                except:        
                                    user_responses[params2[param_index2]] = message_text
                                    param_index2 += 1
                            
                            if param_index2 == len(params2):
                                mydb = mysql.connector.connect(
                                    host="localhost",
                                    user="root",
                                    password="",
                                    database="benziani"
                                )
                                cursor = mydb.cursor()
                                # Check if the chat ID exists in the users table
                                query = "SELECT capacita FROM users WHERE chatId = %s"
                                cursor.execute(query, (chat_id,))
                                result = cursor.fetchone()
                                capacita = result[0]
                                # posizione,fuel_required,capacita,car_efficiency,fuel_type
                                query = "SELECT efficenza FROM users WHERE chatId = %s"
                                cursor.execute(query, (chat_id,))
                                result = cursor.fetchone()
                                eff = result[0]
                                query = "SELECT tipoCarb FROM users WHERE chatId = %s"
                                cursor.execute(query, (chat_id,))
                                result = cursor.fetchone()
                                tCarb = result[0]
                                # fuel_type, km_per_liter, my_pos, max_distance, fuel_left
                                if (user_responses["Quanto carburante devi fare? (1/4, 2/4, 3,4, 4/4 di pieno)"]=="1/4"):
                                    fuel_remaining=capacita-(capacita/4)
                                if (user_responses["Quanto carburante devi fare? (1/4, 2/4, 3,4, 4/4 di pieno)"]=="2/4"):
                                    fuel_remaining=capacita/2
                                if (user_responses["Quanto carburante devi fare? (1/4, 2/4, 3,4, 4/4 di pieno)"]=="3/4"):
                                    fuel_remaining=capacita-((capacita/4)*3)
                                max_distance=fuel_remaining*eff
                                nome,distanza,prezzo=get_nearest_gas_station(tCarb,eff,user_responses["Inviami la posizione o scrivendo dove ti trovi o con la posizione di Telegram."],max_distance,fuel_remaining)
                                send_message(chat_id, ("Nome Benzianio: "+str(nome)+"\nDistanza in KM: "+str(distanza)+"\nPrezzo: "+str(prezzo)))
                            else:
                                # We still need to ask for more parameters
                                send_message(chat_id, params2[param_index2])
                    # We have received a message that we don't understand
                    else:
                            # We are waiting for a response from the user
                            if waiting_for_response2:
                                if(param_index2==0):
                                    user_responses[params2[param_index2]] = result["message"]["location"]
                                else:
                                    user_responses[params2[param_index2]] = message_text
                                    param_index += 1 
                    
                    if waiting_for_response:
                        # We are waiting for a response from the user
                        if message_text != "":
                            user_responses[paramsUt[param_index]] = message_text
                            param_index += 1
                        if param_index == len(paramsUt):
                                mydb = mysql.connector.connect(
                                    host="localhost",
                                    user="root",
                                    password="",
                                    database="benziani"
                                )
                                cursor = mydb.cursor()
                                # We have received all the necessary responses
                                # Insert the responses into the database
                                query = "INSERT INTO users (chatId, nome, user_id, tipoCarb, capacita,efficenza) VALUES (%s, %s, %s, %s, %s,%s)"
                                values = (chat_id, user_responses["Ciao! Per iniziare, dimmi il tuo nome."], result["message"]["from"]["id"], user_responses["Che tipo di carburante usi?"],user_responses["Quanta capacità ha il tuo serbatoio? LITRI"],user_responses["Quanti KM riesci a fare con 1 LITRO?"])
                                # Execute the query and commit the changes
                                cursor.execute('DELETE FROM users WHERE chatId=chatId')
                                mydb.commit()
                                cursor.execute(query, values)
                                mydb.commit()
                                cursor.close()
                                # Send a confirmation message
                                send_message(chat_id, 'Grazie per aver fornito le informazioni richieste. Ora puoi cercare il benzinaio più vicino con "/cercabenzinaio" .')
                                # Reset the flag for waiting for a response and the dictionary for user responses
                                waiting_for_response = False
                                user_responses = {}
                                param_index = 0
                        else:
                                # We still need to ask for more parameters
                                send_message(chat_id, paramsUt[param_index])
                            
                    elif message_text == "/start":
                        send_message(chat_id, "Per iniziare, digita \"/nuovoutente\" oppure \"/cercabenzinaio\" se sei già registrato.")
                    elif message_text== "/nuovoutente":
                        # We have received the command to start asking for parameters
                        send_message(chat_id, "Ciao! Per iniziare, dimmi il tuo nome.")
                        # Set the flag for waiting for a response to True
                        waiting_for_response = True
                        
                    elif message_text== "/cercabenzinaio":
                                mydb = mysql.connector.connect(
                                    host="localhost",
                                    user="root",
                                    password="",
                                    database="benziani"
                                )
                                cursor = mydb.cursor()
                                # Check if the chat ID exists in the users table
                                query = "SELECT * FROM users WHERE chatId = %s"
                                cursor.execute(query, (chat_id,))
                                result = cursor.fetchone()

                                if result:
                                    # We have received the command to start asking for parameters
                                    send_message(chat_id, "Inviami la posizione o scrivendo dove ti trovi o con la posizione di Telegram.")
                                    # Set the flag for waiting for a response to True
                                    waiting_for_response2 = True
                                else:
                                    send_message(chat_id,'Devi registrarti prima di iniziare! Digita "/nuovoutente" .')
                                    
                    else:
                        # We have received a message that we don't understand
                        if waiting_for_response:
                            # We are waiting for a response from the user
                            user_responses[paramsUt[param_index]] = message_text
                            param_index += 1   
                        else:
                            if waiting_for_response2!=True:
                            # We are not waiting for a response from the user, and we don't understand the message
                                send_message(chat_id, "Per iniziare, digita \"/start\".")

                            
                # Set the new offset to the ID of the last message we received plus 1
                offset = data["result"][-1]["update_id"] + 1
        # Wait for 5 seconds before checking for new messages again
        # time.sleep(5)
    
def downloadPrezzi(url="https://www.mise.gov.it/images/exportCSV/prezzo_alle_8.csv"):
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

def downloadBenziani(url="https://www.mise.gov.it/images/exportCSV/anagrafica_impianti_attivi.csv"):
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
from math import radians, sin, cos, sqrt,atan2

def get_nearest_gas_station(fuel_type, km_per_liter, my_pos, max_distance, fuel_left):
    def do_haversine(lat1, lon1, lat2, lon2):
        R = 6371  # Radius of the earth in km
        dLat = radians(lat2 - lat1)
        dLon = radians(lon2 - lon1)
        a = sin(dLat / 2) * sin(dLat / 2) + cos(radians(lat1)) \
            * cos(radians(lat2)) * sin(dLon / 2) * sin(dLon / 2)
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c  # Distance in km
        return distance
    
    def is_float(string):
        try:
            float(string)
            return True
        except ValueError:
            return False
    
    # Connect to MySQL database
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="benziani"
    )

    # Create a cursor
    cursor = db.cursor()

    # Get all gas stations with the desired fuel type
    query = "SELECT impianto.idImpianto, nomeImpianto, Latitudine, Longitudine, prezzo FROM impianto JOIN prezzi ON impianto.idImpianto = prezzi.idImpianto WHERE tipoCarburante = %s"
    cursor.execute(query, (fuel_type,))
    gas_stations = cursor.fetchall()
    my_posi=my_pos.split(",")
    
    # Filter gas stations by distance and fuel availability
    filtered_gas_stations = []
    for g in gas_stations:
        if(is_float(g[2])==True and is_float(g[3])==True):
            distance = do_haversine(float(my_posi[0]), float(my_posi[1]), float(g[2]), float(g[3]))
            if distance <= max_distance:
                filtered_gas_stations.append((g[0], g[1], distance, g[4]))

    # Sort gas stations by distance
    sorted_gas_stations = sorted(filtered_gas_stations, key=lambda x: (x[2],x[3]))

    # If no gas station is found within the maximum distance, return None
    if not sorted_gas_stations:
        return None

    # Return the nearest gas station and the most economic price
    return sorted_gas_stations[0][1],round(sorted_gas_stations[0][2],3),sorted_gas_stations[0][3]

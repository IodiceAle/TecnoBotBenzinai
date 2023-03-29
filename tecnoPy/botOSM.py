import requests
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
            rep=response.json();
        return response.json()
        
    def get_chat_and_update_ids(response):
        chat_id = response["result"][0]["message"]["chat"]["id"]
        update_id = response["result"][0]["update_id"]
        return chat_id, update_id

# bot_token = "6295982819:AAH6Ao3BtUtzFbYoYRcyfZMXv9__9HT75oo"


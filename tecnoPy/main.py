import botOSM
import updateDB

t=botOSM.Telegram("6295982819:AAH6Ao3BtUtzFbYoYRcyfZMXv9__9HT75oo")
# print(t.getUpdates(220270984))
# chatId, updId=t.get_chat_and_update_ids(t.getUpdates(220270984))
urlPrezzi="https://www.mise.gov.it/images/exportCSV/prezzo_alle_8.csv"
urlBenzinai="https://www.mise.gov.it/images/exportCSV/anagrafica_impianti_attivi.csv"
t.downloadPrezzi(urlPrezzi)
t.downloadBenziani(urlBenzinai)

my_thread = updateDB.MyThread()
my_thread.start()
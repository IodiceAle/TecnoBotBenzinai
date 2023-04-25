import botOSM
import updateDB

thread = botOSM.threading.Thread(target=botOSM.handle_messages)
thread.start()

# my_thread = updateDB.MyThread()
# my_thread.start()
import threading
import time

class MyThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            now = time.localtime()
            if now.tm_hour == 8 and now.tm_min == 10:
                self.do_something()
                # Wait for 24 hours before checking again
                time.sleep(24 * 60 * 60)
            else:
                # Wait for 10 seconds before checking again
                time.sleep(10)

    def do_something(self):
        # Put your code here that needs to be executed at 8:10 am
        print("It's 8:10 am! Time to do something.")
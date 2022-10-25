import threading

class Count:
    def __init__(self):
        self.count = 0
        self.lock = threading.Lock()
    
    def incr_count(self):
        self.lock.acquire()
        self.count += 1
        self.lock.release()

    def get_count(self):
        self.lock.acquire()
        val = self.count
        self.lock.release()
        return val
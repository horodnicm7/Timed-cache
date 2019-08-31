import time, threading


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Cache(object, metaclass=Singleton):
    """
        It contains a cache of the form:
            key: [value, ttl, timestamp]
    """
    def __init__(self, ttl=1):
        self.__ttl = ttl
        self.__cache = dict()
        self.__lock = threading.Lock()
        self.__clean_up()

    def __setitem__(self, key, value):
        if key in self.__cache:
            self.__cache[key][2] = int(time.time())
        else:
            self.__lock.acquire()
            self.__cache[key] = [value, self.__ttl, int(time.time())]
            self.__lock.release()

    def __delitem__(self, key):
        del self.__cache[key]

    def __len__(self):
        return len(self.__cache)

    @property
    def __dict__(self):
        return self.__cache

    @property
    def ttl(self):
        return self.__ttl

    @ttl.setter
    def ttl(self, value):
        self.__ttl = value

    def remove(self, key):
        if key not in self.__cache:
            raise KeyError

        self.__lock.acquire()
        del self.__cache[key]
        self.__lock.release()

    def set_ttl(self, key, ttl):
        if self.is_expired(key):
            del self.__cache[key]

        if key in self.__cache:
            self.__lock.acquire()
            self.__cache[key][1] = ttl
            self.__lock.release()

    def is_expired(self, key):
        cr_time = time.time()

        self.__lock.acquire()
        if cr_time - self.__cache[key][2] >= self.__cache[key][1]:
            self.__lock.release()
            return True

        self.__lock.release()
        return False

    def stop(self):
        cr_threads = threading.enumerate()  # type: threading.Thread
        for thread in cr_threads:
            if isinstance(thread, threading.Timer):
                thread.cancel()

    def printout(self):
        self.__lock.acquire()
        for key, value in self.__cache.items():
            print('{}: {}'.format(key, value))
        self.__lock.release()

    def __clean_up(self):
        print('Cleaning up cache')
        self.__lock.acquire()

        for key in self.__cache.keys():
            if self.is_expired(key):
                del self.__cache[key]

        self.__lock.release()
        threading.Timer(self.__ttl, self.__clean_up).start()


cache = Cache(2)

for i in range(100):
    cache[i] = i * 2

    if i % 50 == 0:
        cache.ttl *= 2
    time.sleep(0.1)

cache.stop()
print()
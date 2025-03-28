import threading
import time

def deadlock_thread1(lock1, lock2):
    """First deadlock thread"""
    with lock1:
        print("Thread 1 acquired lock 1")
        time.sleep(1)  # Wait a bit to ensure deadlock occurs
        print("Thread 1 waiting for lock 2...")
        with lock2:
            print("This line will never execute")

def deadlock_thread2(lock1, lock2):
    """Second deadlock thread"""
    with lock2:
        print("Thread 2 acquired lock 2")
        time.sleep(1)  # Wait a bit to ensure deadlock occurs
        print("Thread 2 waiting for lock 1...")
        with lock1:
            print("This line will never execute")

def main():
    # Create two locks
    lock1 = threading.Lock()
    lock2 = threading.Lock()

    # Create two threads that will wait for each other's locks
    t1 = threading.Thread(target=deadlock_thread1, args=(lock1, lock2))
    t2 = threading.Thread(target=deadlock_thread2, args=(lock1, lock2))

    # Start threads
    t1.start()
    t2.start()

    # Wait for threads to finish (they never will)
    t1.join()
    t2.join()

if __name__ == "__main__":
    main()
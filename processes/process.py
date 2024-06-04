import signal
import sys
import time

start = time.time()


def signal_handler(signum, frame):
    print(f"Process: {signum}")
    print(f"Process Time: {time.time()-start}s")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    print("Start")
    time.sleep(60)
    print("Stop")

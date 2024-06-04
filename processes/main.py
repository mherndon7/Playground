import pathlib
import signal
import subprocess
import sys
import time
from concurrent.futures import Future, ThreadPoolExecutor, wait

exe: ThreadPoolExecutor | None = None
start = time.time()


def signal_handler(signum, frame):
    print(f"Main: {signum}")

    # if exe is not None:
    #     print("Shutting down")
    #     exe.shutdown(wait=False, cancel_futures=True)
    print(f"Main Time: {time.time()-start}s")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def process_popen(cmds: list[str]):
    p = subprocess.Popen(cmds, shell=True)
    stdout, stderr = p.communicate(timeout=60)
    print(stdout)
    print(stderr)


def process_run(cmds: list[str]) -> None:
    p = subprocess.run(cmds, check=True, timeout=60)
    print(p.stdout.decode())
    print(p.stderr.decode())


if __name__ == "__main__":
    file = pathlib.Path(__file__).parent.joinpath("process.py")
    cmds = ["python", f"{file}"]

    futures: list[Future] = []
    with ThreadPoolExecutor(1) as executor:
        exe = executor
        # futures.append(executor.submit(process_popen, cmds))
        futures.append(executor.submit(process_run, cmds))

    wait(futures)
    print("Finished")

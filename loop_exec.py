import os
import sys
from time import sleep
import subprocess

args = sys.argv

i = 0
while True:
    i = i + 1
    print('execute! count >> ' + str(i))
    subprocess.call( ["/bin/sh", "/usr/src/app/exec.sh", args[1]])
    sleep(int(args[1]))
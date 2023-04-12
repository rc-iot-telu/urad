from itertools import permutations
import serial
import time
import matplotlib.pyplot as plt
import numpy as np
import math
import csv
from datetime import datetime

sekarang = datetime.now().strftime("%Y%m%d-%H%M%S")
ser = serial.Serial('COM6', 9800, timeout=1)
time.sleep(2)
N=1000
num=np.zeros(N)
data=[]
data1 = np.zeros(100)
data2 = np.zeros(100)

try:
    while True:
        line = ser.readline()

        if line:
            string = line.decode().strip("\n")
            #  num[i] = string
            print(string, end="\r")
            data.append(float(string))

    ser.close()
except KeyboardInterrupt:
    pass

ser.close()

with open("data_"+sekarang+".csv", "w", newline="") as f:
    writer = csv.writer(f)
    for d in data:
        writer.writerow([d])
    print ("save.......")

print("DONE SCANNING")

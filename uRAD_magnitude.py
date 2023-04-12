import uRAD_USB_SDK11		# import uRAD libray
import serial

import matplotlib.pyplot as plt

import numpy as np
from numpy.fft import fft,fftshift

from time import time, sleep

import datetime
import csv

def annot_max(x,y, ax=None):
    xmax = x[np.argmax(y)]
    ymax = y.max()
    text= "x={}, y={:.3f}".format(xmax, ymax)
    if not ax:
        ax=plt.gca()
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    arrowprops=dict(arrowstyle="-",connectionstyle="angle,angleA=0,angleB=60")
    kw = dict(xycoords='data',textcoords="axes fraction",
             bbox=bbox_props, ha="right", va="top")
    ax.annotate(text, xy=(xmax, ymax), xytext=(0.94,0.96), **kw)

# True if USB, False if UART
usb_communication = True

# input parameters
mode = 2					# sawtooth mode
f0 = 5						# starting at 24.005 GHz
BW = 240					# using all the BW available = 240 MHz
Ns = 200					# 200 samples
Ntar = 3					# 3 target of interest
Rmax = 100					# searching along the full distance range
MTI = 0						# MTI mode disable because we want information of static and moving targets
Mth = 0						# parameter not used because "movement" is not requested
Alpha = 10					# signal has to be 10 dB higher than its surrounding
distance_true = True 		# request distance information
velocity_true = False		# mode 2 does not provide velocity information
SNR_true = True 			# Signal-to-Noise-Ratio information requested
I_true = True 				# In-Phase Component (RAW data) not requested
Q_true = True				# Quadrature Component (RAW data) not requested
movement_true = False 		# not interested in boolean movement detection

# Serial Port configuration
ser = serial.Serial()
if (usb_communication):
	ser.port = 'COM10'
	ser.baudrate = 1e6
else:
	ser.port = '/dev/serial0'
	ser.baudrate = 115200

# Sleep Time (seconds) between iterations
timeSleep = 5e-3

# Other serial parameters
ser.bytesize = serial.EIGHTBITS
ser.parity = serial.PARITY_NONE
ser.stopbits = serial.STOPBITS_ONE

# Method to correctly turn OFF and close uRAD
def closeProgram():
	# switch OFF uRAD
	return_code = uRAD_USB_SDK11.turnOFF(ser)
	if (return_code != 0):
		exit()

# Open serial port
try:
	ser.open()
except:
	closeProgram()

# switch ON uRAD
return_code = uRAD_USB_SDK11.turnON(ser)
if (return_code != 0):
	closeProgram()

if (not usb_communication):
	sleep(timeSleep)

# loadConfiguration uRAD
return_code = uRAD_USB_SDK11.loadConfiguration(ser, mode, f0, BW, Ns, Ntar, Rmax, MTI, Mth, Alpha, distance_true, velocity_true, SNR_true, I_true, Q_true, movement_true)
if (return_code != 0):
	closeProgram()

if (not usb_communication):
	sleep(timeSleep)

fig, ax = plt.subplots()
plt.ion()
plt.ylim([0, 0.6])

hasil_fft = []
hasil_i = []
hasil_q = []
hasil_phase = []

#fft_file = open(f"./{datetime.datetime.today().strftime('%A, %d-%m-%y - %H.%M')}_hasil_fft.csv", "w+", newline="")
#i_file = open(f"./{datetime.datetime.today().strftime('%A, %d-%m-%y - %H.%M')}_hasil_i.csv", "w+", newline="")
#q_file = open(f"./{datetime.datetime.today().strftime('%A, %d-%m-%y - %H.%M')}_hasil_q.csv", "w+", newline="")

fft_file = open(f"./hasil_fft_aldi1.csv", "w+", newline="")
i_file = open(f"./hasil_i_aldi1.csv", "w+", newline="")
q_file = open(f"./hasil_q_aldi1.csv", "w+", newline="")


fft_csv = csv.writer(fft_file)
i_csv = csv.writer(i_file)
q_csv = csv.writer(q_file)

# infinite detection loop
while True:

	# target detection request
	return_code, results, raw_results = uRAD_USB_SDK11.detection(ser)
	if (return_code != 0):
		closeProgram()

	# Extract results from outputs
	NtarDetected = results[0]
	distance = results[1]
	SNR = results[3]
	I = raw_results[0]
	Q = raw_results[1]
    
	# Iterate through desired targets
	for i in range(NtarDetected):
		# If SNR is big enough
		if (SNR[i] > 0):
			# Prints target information
			# print("Target: %d, I: %1.2f, Q: %1.1f" % (i+1, I[i], Q[i]))
			# print(I, Q)
			#print("Target: %d, Distance: %1.2f m, SNR: %1.1f dB" % (i+1, distance[i], SNR[i]))
			#print(results)
			# FFT Processing
			data_i = np.array(I)
			data_q = np.array(Q)

			max_voltage = 3.3
			ADC_intervals = 4096
			Ns = np.size(data_i)
			Fs = 2

			data_i = np.subtract(np.multiply(I, max_voltage/ADC_intervals), np.mean(np.multiply(I, max_voltage/ADC_intervals)))
			data_q = np.subtract(np.multiply(Q, max_voltage/ADC_intervals), np.mean(np.multiply(Q, max_voltage/ADC_intervals)))
			ComplexVector = data_i + 1j*data_q
			ComplexVector = ComplexVector * np.hanning(Ns) * 2 / 3.3

			i_csv.writerow(I)
			q_csv.writerow(Q)

			N_FFT = 4096
			#c = 299792458
			#max_distance = c/(2*BW_actual) * Fs/2 * RampTimeReal
			#x_axis = c/(2*BW_actual)*f_axis*RampTimeReal

			#ComplexVectorFFT = fft(ComplexVector)
			#Magnitude = 2 * np.abs(ComplexVectorFFT) / Ns

			#FrequencyDomainComplex = 2*np.absolute(fftshift(fft(ComplexVector / Ns, N_FFT)))
			#FrequencyDomainComplex =fftshift(fft(ComplexVector / Ns, N_FFT))
			FrequencyDomainComplex =2*np.absolute(fft(ComplexVector))

			max_fft = max(FrequencyDomainComplex)
			index_fft = np.where(FrequencyDomainComplex == max_fft)[0][0]

			Phase = np.angle(fft(ComplexVector))
			with open(f"./pasa_testing.csv", "a", newline="") as f:
				phase_csv = csv.writer(f)
				phase_csv.writerow([Phase[index_fft]])

			#FrequencyDomainComplex = 20 * np.log10(FrequencyDomainComplex1)
			ukuran = np.size(FrequencyDomainComplex)
			hasil_phase.append(Phase[index_fft])
			#print(hasil_phase[-1])

			# print(ukuran)

			ax.plot(FrequencyDomainComplex)
			#print([float(Phase[index_fft])], end="\r")


			# plt.plot(FrequencyDomainComplex)

			fft_csv.writerow(FrequencyDomainComplex)

			# print(len([Phase[index_fft]]))
			# np.savetxt("phasa.csv", np.array(Phase[index_fft]), delimiter=",")


			annot_max([i + 1 for i in range(np.size(FrequencyDomainComplex))],FrequencyDomainComplex, ax)
			plt.pause(0.05)
			plt.cla()
			plt.ylim([-0.2, 3])

	# If number of detected targets is greater than 0 prints an empty line for a smarter output
	if (NtarDetected > 0):
		pass

	# Sleep during specified time
	if (not usb_communication):
		sleep(timeSleep)
	

plt.show()
print(hasil_fft)

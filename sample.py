'''
ft-710 cat control manual: https://www.simarud.no/files/simarud/Documents/FT-710_CAT_OM_ENG_2211-A.pdf
'''
import time
import math
import csv
import requests
import serial

'''
send command to FT-710 and return response
'''
def ft710_command(command):
    ft710.write(command)
    response = ft710.read_until(expected=b';', size=None)
    return response

'''
sample and return FWDMV for 25, 50 and 75 Watt
'''
def getMv(p, f):
    ft710_command(bytes(f'PC{p:03};', 'utf-8')) # b'PC005;' Power Control (PC)
    ft710_command(bytes(f'VS0;', 'utf-8'))      # set VFO A (VFO Switch)
    ft710_command(bytes(f'FA{f:09};', 'utf-8')) # set Frequency VFO A freq
    ft710_command(bytes(f'MD03;', 'utf-8'))     # main band (VFO A) mode CW
    print(f'Sample power setting {p:03} Watt at Frequency {f:09} with Nanny')

    ft710_ptt.setRTS(True)
    time.sleep(1)
    r = requests.get(url = "http://powernanny.local/power")
    nanny = r.json()
    ft710_ptt.setRTS(False)
    return nanny["FWDMV"]

'''
sample and return FWDMV for 25, 50 and 75 Watt
'''
def sample(f):
    csv_writer.writerow([f, getMv(25, f), getMv(50, f), getMv(75, f)])

ft710       = serial.Serial('/dev/cu.SLAB_USBtoUART', 38400, timeout=2, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_TWO, xonxoff=0, rtscts=0)
ft710_ptt   = serial.Serial('/dev/cu.SLAB_USBtoUART5', 4800, timeout=0)
ft710_ptt.setRTS(False)

# set power to 5 watt and wait (for checking control active before key-up)
ft710_command(b'PC005;')
print(ft710_command(b'PC;'))
input("Press Enter to continue...")

# === sample on several frequencies ===

file = open(f'./data/ft710-Nanny.csv', 'w', newline='')
csv_writer = csv.writer(file)
csv_writer.writerow(['frequency', '25Watt', '50Watt', '75Watt'])

sample(14000000)
sample(14050000)
sample(14100000)
sample(14150000)
sample(14200000)
sample(14240000)

file.close()

# ========================================

ft710_ptt.close()
ft710.close()

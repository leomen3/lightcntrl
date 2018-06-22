 ###########################################################################
# Setup code goes below, this is called once at the start of the program: #
# client side of the lighcontroller
# steps
# 1) try to connect to 3RPi server
# 2) if successfull, sync time, download and udpate configurations
# 3) if time within LIGHTS ON interval and enough battery, set lights to on
# 4) otherwise, go to sleep mode for SLEEP interval
###########################################################################
import time
import machine
from machine import RTC

COMMANDS_PORT = 5640
RPi_HOST = "10.0.0.5"
DEEP_SLEEP_INTERVAL = 10  # second
#TODO add time from RPi server when connection is possible

def toggleGPIO(p):
    p.value(not p.value())

def GPIO_On(p):
    p.value(0)

def GPIO_Off(p):
    p.value(1)

def lightOn():
    GPIO_On(pinLED)
    time.sleep(DEEP_SLEEP_INTERVAL)

def lightOff():
    ledOff(GPIO_light_cntrol)


def initTime(hour=6, minute=7, second=8, day=18, month=7, year=1980):
    # The 8-tuple has the following format:
    #(year, month, day, weekday, hours, minutes, seconds, subseconds)
    # weekday is 1-7 for Monday through Sunday.
    #subseconds counts down from 255 to 0
    rtc.datetime((year, month, day, 1, hour, minute, second, 0))    # set /
                                        #a specific  date and time
    return None


def getDateTime():
    return rtc.datetime()   # get date and time


#Connect to home router
def netConnect():
    import network
    print('Establishing WiFi connection to home router')
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect('leonet', 'leo567567567')
    time.sleep(5.0)

    # while not sta_if.isconnected():
    #     pass

    print('Connected to network')
    print(sta_if.ifconfig())

    #Disable AP interface
    #ap_if.active(False)
    return None


def reqCommands():
    import socket
    addr = socket.getaddrinfo(RPi_HOST, COMMANDS_PORT)[0][-1]
    s = socket.socket()
    print("Connecting to RPi: ", RPi_HOST)
    try:
    #TODO Something wrong here, the socket does not connect. \
    # Important, after failed connection need to open a new socket.
        s.connect(addr)
        s.send("Ready")
    except:
        print("Error connecting to RPi server")

    while True:
        print("waiting for commad")
        data = s.recv(100)
        if data:
            print('commad received')
            print(str(data, 'utf8'), end='')
        else:
            break
    s.close()
    return None


def saveState(payload):
    #Save irrigation state to RTC memory, persistant after DeepSleep mode
    rtc.memory(payload)
    return None


def getState():
    #Extract irrigation state from RTC memory after deep sleep, persistant \
    # after DeepSleep mode
    return rtc.memory()


#Generic Init
GPIO_light_cntrol = machine.Pin(2, machine.Pin.OUT)
rtc = RTC()
#netConnect()
curr_tm = getDateTime()  #TODO need to do proper time setting here, from internet
current_year = str(curr_tm[0])
print("current year: ", current_year)
if str(current_year) != '2018':
    print("time not initialize - setting")
    initTime(22, 23, 24, 20, 4, 2018)

#TODO Add OTA bootloader

while True:
    
    # (1)attempt connecting to server to get status, commands and send log
    
    # (2) if successful, log and update configuration
    curr_tm = getDateTime()
    #time_rep = curr_tm
    # time_rep = str(curr_tm[0])+'-'+str(curr_tm[1])+'-'+str(curr_tm[2])+'->'+
    #             str(curr_tm[3])+':'+str(curr_tm[4])+':'+str(curr_tm[5])
    #print(curr_tm)
    print("Current time: ", time_rep)
    
    # Retrieve state from RTC memory
    state = getState()
    print("Retrieved state (last irrigation ended): ", state)

    # check if irrigation is needed
    
    # if needed, irrigate
    print("Irrigation is needed -> Starting for ", IRRIGATION_DURATION, "[s]")
    irrigationStart()
    
    # STOP irrigation TODO this code must be extra safe
    # toggle OFF pin for testing
    print("Stopping irrigaiton")
    irrgationStop()
    curr_tm = getDateTime()
    
    # save state to RTC memory
    print("Saving state")
    saveState(str(curr_tm))
    
    # safety sleep to allow multitasking between ESP core and WiFI
    print("10 seconds sleep before DEEP SLEEP")
    time.sleep(10)
    
    # go to DEEP SLEEP 
    # configure RTC.ALARM0 to be able to wake the device
    print("Configure trigger")
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

    # set RTC.ALARM0 to fire after 10 seconds (waking the device)
    sleep_ms = DEEP_SLEEP_INTERVAL*1000
    print("set alarm")
    rtc.alarm(rtc.ALARM0, sleep_ms)

    # put the device to sleep
    print("going to sleep for: ", DEEP_SLEEP_INTERVAL, "seconds") 
    machine.deepsleep()

    #LOG

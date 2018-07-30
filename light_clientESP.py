 ###########################################################################
# Setup code goes below, this is called once at the start of the program: #
# client side of the lighcontroller
# steps
# 1) try to connect to 3RPi server
# 2) if successfull, sync time, download and udpate configurations
# 3) if time within LIGHTS ON interval and enough battery, set lights to on
# 4) otherwise, go to sleep mode for SLEEP interval
###########################################################################

DEBUG = False

if not DEBUG:
    import machine
    import utime
    import ntptime
else:
    import time


UTC_OFFSET = 3
START_TIME = 20
END_TIME = 6
COMMANDS_PORT = 5641
RPi_HOST = "10.0.0.17"
DEEP_SLEEP_INTERVAL = 1  # second


def toggleGPIO(p):
    p.value(not p.value())


def GPIO_On(p):
    p.value(0)


def GPIO_Off(p):
    p.value(1)


def lightOn():
    if not DEBUG:
        GPIO_On(GPIO_light_cntrl)
        utime.sleep(DEEP_SLEEP_INTERVAL)
    else:
        print("Issue light ON command")


def lightOff():
    if not DEBUG:
        GPIO_Off(GPIO_light_cntrl)
    else:
        print("Issue light OFF command")


def getDateTime():
    if DEBUG:
        return time.localtime()
    else:
        ntptime.settime()
        t = rtc.datetime()
        return t     

def sleepStart(sleepInterval):
    if DEBUG:
        time.sleep(sleepInterval)
    else:
        machine.deepsleep()


def getRPiTime():
    import socket
    addr = socket.getaddrinfo(RPi_HOST, COMMANDS_PORT)[0][-1]
    s = socket.socket()
    print("Connecting to RPi: ", RPi_HOST)
    try:
    #TODO Something wrong here, the socket does not connect. \
    # Important, after failed connection need to open a new socket.
        s.connect(addr)
    except:
        print("Error connecting to RPi server")
        s.close()
        return None

    if DEBUG: 
        print("Handshaking with RPi")
    s.send("time".encode("utf8"))
    time.sleep(3)
    data = s.recv(1024)
    payload = data.decode("utf8")
    if data:
        print('commad received: ' + payload)
    else:
        print('No data received')
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
if not DEBUG:
    GPIO_light_cntrl = machine.Pin(2, machine.Pin.OUT)
    rtc = machine.RTC()


def time_in_range(start, end, utc_time_hour):
    """Return true if x is in the range [start, end]"""
    x = (utc_time_hour + 3) % 24
    print("Current hour is: ", x)
    if start <= end:
        return start <= x and x <= end
    else:
        return start <= x or x <= end


def main():

    while True:
        # (1)attempt connecting to server to get status, commands and send log
        #getRPiTime()
        
        # (2) if successful, log and update configuration
        curr_tm = getDateTime()
        print(curr_tm)

 #       time_rep = str(curr_tm[0])+'-'+str(curr_tm[1])+'-'+str(curr_tm[2])+'->' + \
 #                         str(curr_tm[3])+':'+str(curr_tm[4])+':'+str(curr_tm[5])
 #       print("Current time: ", time_rep)
        

        # check if lighting is needed - if needed, turn on the light
        if time_in_range(START_TIME, END_TIME, curr_tm[4]):
            print("Light should be ON -> Turning ON ")
            lightOn()
        else:
            print("Light should be OFF -> Turning OFF ")
            lightOff()

        # safety sleep to allow multitasking between ESP core and WiFI
        print("10 seconds sleep before DEEP SLEEP")
        utime.sleep(10)
        
        # go to DEEP SLEEP 
        # configure RTC.ALARM0 to be able to wake the device
        if not DEBUG:
            print("Configure trigger")
            rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

        # set RTC.ALARM0 to fire after DEEP_SLEEP_INTERVAL  (waking the device)
        sleep_ms = DEEP_SLEEP_INTERVAL*1000
        if not DEBUG:
            print("set alarm")
            rtc.alarm(rtc.ALARM0, sleep_ms)

        # put the device to sleep
        print("going to sleep for: ", DEEP_SLEEP_INTERVAL, "seconds") 
        sleepStart(DEEP_SLEEP_INTERVAL)

if DEBUG:
    if __name__ == "__main__":
        main() 
else:
    main()
    
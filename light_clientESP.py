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

DEBUG = True

if not DEBUG:
    import machine
    from machine import RTC


START_TIME = time.strptime('19:00', '%H:%M')
END_TIME = time.strptime('06:00', '%H:%M')
COMMANDS_PORT = 5641
RPi_HOST = "10.0.0.17"
DEEP_SLEEP_INTERVAL = 10  # second
#TODO add time from RPi server when connection is possible


def toggleGPIO(p):
    p.value(not p.value())


def GPIO_On(p):
    p.value(0)


def GPIO_Off(p):
    p.value(1)


def lightOn():
    if not DEBUG:
        GPIO_On(GPIO_light_cntrl)
        time.sleep(DEEP_SLEEP_INTERVAL)
    else:
        print("Issue light ON command")


def lightOff():
    if not DEBUG:
        ledOff(GPIO_light_cntrl)
    else:
        print("Issue light OFF command")


def initTime(hour=6, minute=7, second=8, day=18, month=7, year=1980):
    # The 8-tuple has the following format:
    #(year, month, day, weekday, hours, minutes, seconds, subseconds)
    # weekday is 1-7 for Monday through Sunday.
    #subseconds counts down from 255 to 0
    rtc.datetime((year, month, day, 1, hour, minute, second, 0))    # set /
                                        #a specific  date and time
    return None


def getDateTime():
    if DEBUG:
        return time.localtime()
    else:
        return rtc.datetime()   # get date and time


#Connect to home router
def netConnect():
    if DEBUG:
        pass
        return None
    else:
        import network
        print('Establishing WiFi connection to home router')
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        sta_if.connect('leonet', 'leo567567567')  ##\TODO removice hardcoding of the login
        time.sleep(5.0)
        print('Connected to network')
        print(sta_if.ifconfig())
        return None


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
        print('commad received: '+ payload)
    else:
        print('No data received')
    s.close()
    return None


# def reqCommands():
#     import socket
#     addr = socket.getaddrinfo(RPi_HOST, COMMANDS_PORT)[0][-1]
#     s = socket.socket()
#     print("Connecting to RPi: ", RPi_HOST)
#     try:
#     #TODO Something wrong here, the socket does not connect. \
#     # Important, after failed connection need to open a new socket.
#         s.connect(addr)
#         s.send("Ready")
#     except:
#         print("Error connecting to RPi server")

#     while True:
#         print("waiting for commad")
#         data = s.recv(100)
#         if data:
#             print('commad received')
#             print(str(data, 'utf8'), end='')
#         else:
#             break
#     s.close()
#     return None


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
    rtc = RTC()

netConnect()
curr_tm = getDateTime()  #TODO need to do proper time setting here, from internet
current_year = str(curr_tm[0])
print("current year: ", current_year)
if str(current_year) != '2018':
    print("time not initialize - setting")
    initTime(22, 23, 24, 20, 4, 2018)

#TODO Add OTA bootloader


def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


def main():

    while True:
        # (1)attempt connecting to server to get status, commands and send log
        getRPiTime()
        
        # (2) if successful, log and update configuration
        curr_tm = getDateTime()
        #time_rep = curr_tm
        time_rep = str(curr_tm[0])+'-'+str(curr_tm[1])+'-'+str(curr_tm[2])+'->'+ \
                    str(curr_tm[3])+':'+str(curr_tm[4])+':'+str(curr_tm[5])
        #print(curr_tm)
        print("Current time: ", time_rep)
        
        # Retrieve state from RTC memory
        if not DEBUG:
            state = getState()
            print("Retrieved state (last irrigation ended): ", state)

        # check if lighting is needed - if needed, turn on the light
        if time_in_range(START_TIME, END_TIME, curr_tm):
            print("Light should be on -> Turning on ")
            lightOn()
        else:
            lightOff()

        curr_tm = getDateTime()
        
        # save state to RTC memory
        if not DEBUG:
            print("Saving state")
            saveState(str(curr_tm))
        
        # safety sleep to allow multitasking between ESP core and WiFI
        print("10 seconds sleep before DEEP SLEEP")
        time.sleep(10)
        
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

        #LOG

if DEBUG:
    if __name__ == "__main__":
        main() 
else:
    main()
    
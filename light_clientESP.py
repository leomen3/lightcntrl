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
    import network
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
    p.value(1)


def GPIO_Off(p):
    p.value(0)


def lightOn():
    if not DEBUG:
        GPIO_On(GPIO_light_cntrl)
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
        utime.sleep(5)  # Sleep for 5 seconds, to make sure WiFi is connected
        if sta_if.isconnected():
            print("Connected to internet, setting time from NTP")
            ntptime.settime()
        t = rtc.datetime()
        print("RTC time is: ", t)
        year = t[0]
        print("year is: ",year)
        gotTime = year > 2016
        if gotTime:
            print(t)
        else:
            print("Could not get time")
        return gotTime, t 

        
def sleepStart():
    """ set RTC.ALARM0 to fire after DEEP_SLEEP_INTERVAL seconds
    put the ESP8266 to deep sleep """
    print("going to sleep for: ", DEEP_SLEEP_INTERVAL, "seconds") 
    if DEBUG:
        time.sleep(DEEP_SLEEP_INTERVAL)
    else:
        rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
        rtc.alarm(rtc.ALARM0, DEEP_SLEEP_INTERVAL*1000)
        machine.deepsleep()


def batteryCharged():
    """ read the ADC value from the battery output, and convert to 
    volts"""
    pass
    adc = machine.ADC(0)  #   return value 0 to 1023
    adcVal = adc.read()
    volts = adcVal/1023*5 #   assuming 1:5 voltage divider
    #return charged, volts

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


def time_in_range(start, end, utc_time_hour):
    """Return true if x is in the range [start, end]"""
    x = (utc_time_hour + 3) % 24
    print("Current hour is: ", x)
    if start <= end:
        return start <= x and x <= end
    else:
        return start <= x or x <= end


def main():
    GPIO_On(GPIO_light_cntrl)
    utime.sleep(3)
    GPIO_Off(GPIO_light_cntrl)
    utime.sleep(6)
    GPIO_On(GPIO_light_cntrl)
    utime.sleep(3)
    GPIO_Off(GPIO_light_cntrl)
    utime.sleep(6)

    while True:
        gotTime, curr_tm = getDateTime()  # get time 

        # check if lighting is needed - if needed, turn on the light
        if gotTime and time_in_range(START_TIME, END_TIME, curr_tm[4]):
            print("Light should be ON -> Turning ON ")
            lightOn()
        else:
            print("Light should be OFF -> Turning OFF ")
            lightOff()

        # safety sleep to allow multitasking between ESP core and WiFI
        print("10 seconds sleep before DEEP SLEEP")
        utime.sleep(10)
        sleepStart()   # put the device to sleep

#Generic Init
if not DEBUG:
    GPIO_light_cntrl = machine.Pin(4, machine.Pin.OUT)
    rtc = machine.RTC()
    sta_if = network.WLAN(network.STA_IF)

if DEBUG:
    if __name__ == "__main__":
        main() 
else:
    main()
    

#TODO
# Add logging
# Add ADC reading

# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import gc
import webrepl
import network
webrepl.start()

gc.collect()
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('leonet', 'leo567567567')

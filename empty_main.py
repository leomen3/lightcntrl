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
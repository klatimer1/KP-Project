

import requests
import time
from phue import Bridge

# declare global constants

starttime=time.time()
red = 0
green = 25500
yellow = 12750
orange  = 5000
_sleep = 60 * 20       # calculates the time between runs in mins 
flash_seq = 3	       # number  times Kp alert flashes
kp_light = 1           # set light 1 as the lab light
bridge_IP = '<place your bridge IP address here as string>'         # change bridge IP address here
user_name = '<create username and place here as string>'          #user name for the bridge - see implementation guide for details
str_colour=' '
kp_mean=0

def choose_light_source():
# light selection process was separated from the main function for expandablility if more than one light source 
# is added
        light_source = kp_light
        return light_source

def kp_hue_process(light_source):
   #  bridge IP will change for every new wifi router.
   #  user name can be created using the bridge API - see implementation guide for instructions

        b = Bridge(bridge_IP, user_name) 
        b.connect()
        b.get_api()
        kp_mean=0
	colour = None
        #  get the data from NOAA
	r=requests.get('https://services.swpc.noaa.gov/json/planetary_k_index_1m.json')
	entries = r.json()[-11:]
	kp_total_sum = 0
	kp_num_entries=  0
	# take an average of the readings from the file
	for i in entries:
		kp_total_sum+=float(i['kp_index'])
		kp_num_entries += 1
		
	kp_mean = kp_total_sum/kp_num_entries
	if(kp_mean < 2):
		colour=red
		str_colour='red'
	elif(kp_mean >= 2 and kp_mean < 3):
		colour=orange
		str_colour='orange'
	elif(kp_mean >= 3 and kp_mean < 4):
		colour=yellow
		str_colour='yellow'
	elif(kp_mean >= 4):
		colour=green
		str_colour='green'
		
	
	light_default_brightness = b.get_light(light_source,'bri') # KL save previous settings
	light_default_colour = b.get_light(light_source,'hue')	
	light_default_saturation = b.get_light(light_source, 'sat')
    
	
        # print to log
	print("Cycle every " + str(_sleep/60) + " min ------------------")
	print("		Changing colour to: " + str_colour + " " + str(colour))
	print("		The average KP value is: " + str(round(kp_mean)))
	print("		Timestamps from " + str(entries[0]['time_tag']) + " to " + str(entries[-1]['time_tag'])+ " UTC")
	
	
        print("Type Ctrl-C to end program  -  this may take a moment")
        
        # change light colour, brightness and saturation
	b.set_light(light_source, 'bri', 0)
	b.set_light(light_source, 'sat', 255)
	b.set_light(light_source, 'hue', colour) #Darken
	
	# light pulses 3 times
	for i in range(0,flash_seq):
	   b.set_light(light_source, 'bri', 255) 
	   time.sleep(0.6)
	   print("flash")
	   b.set_light(light_source, 'bri', 0) 
           time.sleep(0.6)
           
        #  set lights back to previous settings
	b.set_light(light_source, 'bri', light_default_brightness)
        b.set_light(light_source,'hue', light_default_colour)
        b.set_light(light_source,'sat', light_default_saturation)	
        
	time.sleep(1)


try:
    
    light_source = choose_light_source()
    while True:
        kp_hue_process(light_source)
        time.sleep(_sleep)
except KeyboardInterrupt:
    # Use ctrol - C to end program
    print('Manual break by user')
    print('Program ended')
except Exception as error:
    print('Something else went wrong... Check logs.')
    print(error)
	

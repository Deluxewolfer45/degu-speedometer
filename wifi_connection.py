import time
import machine
import network
import json
import os
import uasyncio
from request_parser import RequestParser
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2, PEN_P4

async def handle_request(reader, writer):
    try:
        file = open("index_wifi.html")
        body = file.read()

        raw_request = await reader.read(2048)
        request = RequestParser(raw_request)

        response = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n'
        response += "Content-Length: " + str(len(body)) + "\r\n"
        response += "Connection: Closed\r\n\r\n"
        response += body
        
        if request.query_params != {}:
            with open("wifi_config.json", "w") as file:
                json.dump(request.query_params, file)
            machine.reset()
            
        writer.write(response)
        await writer.drain()
        await writer.wait_closed()
        
    except OSError as e:
        print('connection error ' + str(e.errno) + " " + str(e))

def clear():
    display.set_pen(BLACK)
    display.clear()
    display.update()
        
def wifi_connect():
    display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2, pen_type=PEN_P4, rotate=0)

    display.set_backlight(0.5)
    display.set_font("bitmap8")
    WHITE = display.create_pen(255, 255, 255)
    BLACK = display.create_pen(0, 0, 0)

    json_file = 'wifi_config.json'
    os.chdir("/") # Make sure working from root directory
    dir_contents = os.listdir("/")  # Get directory listing
        
    # Setting Variable Values: Distances in m, times in s, speeds in km/h and calories in kcal
    if json_file in dir_contents:
        wifi_config = json.load(open(json_file, 'r'))
    
    ssid = wifi_config['ssid']
    password = wifi_config['password']

    network.hostname('speedydegus') # Set Network Hostname for device
    
    wlan = network.WLAN(network.STA_IF) # Set WiFi to station interface
    wlan.active(True) # Activate the network interface
    wlan.config(pm = 0xa11140)
    wlan.connect(ssid, password) # Connect to WiFi network
    
    max_wait = 20
    
    # Wait for connection
    while max_wait > 0:
        print("Waiting for connection..." + str(max_wait))
        """
            0   STAT_IDLE -- no connection and no activity,
            1   STAT_CONNECTING -- connecting in progress,
            -3  STAT_WRONG_PASSWORD -- failed due to incorrect password,
            -2  STAT_NO_AP_FOUND -- failed because no access point replied,
            -1  STAT_CONNECT_FAIL -- failed due to other problems,
            3   STAT_GOT_IP -- connection successful.
        """
        
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.text("Waiting for connection..." + str(max_wait), 10, 10, 320, 4)
        display.update()
        
        if wlan.status() < 0 or wlan.status() >= 3:
            # Finish connection attempt
            break
        
        max_wait -= 1
        time.sleep(1)
    
    # Check connection
    if wlan.status() == 3:
        # Connection successful
        config = wlan.ifconfig()
        ip = config[0]
        print('Connected on ' + str(ip) + "\n")
        
        display.set_pen(WHITE)
        display.text('Connected to ' + ssid + ' on ' + str(ip), 10, 100, 320, 4)
        display.update()
    
    elif wlan.status() == -3 or wlan.status() == -2:
        print("Incorrect Wifi Details")
        
        ap = network.WLAN(network.AP_IF)
        ap.config(essid='speedydegus', security=0)
        ap.active(True)

        # wait for wifi to go active
        wait_counter = 0
        while ap.active() == False:
            print("waiting " + str(wait_counter))
            time.sleep(0.5)
            pass

        print('WiFi active')
        
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.text("Unable to connect to WiFi Network", 10, 00, 320, 4)
        display.text("Please connect to the speedydegus wifi network and enter " + str(ap.ifconfig()[0]) +  " into your browser to reset wifi details.", 10, 100, 300, 2.5)
        display.update()
        
        print(ap.ifconfig())
        
        loop = uasyncio.get_event_loop()
        loop.create_task(uasyncio.start_server(handle_request, "0.0.0.0", 80, 20))
        loop.run_forever()
     
    else:
        print("Connection Failed")

wifi_connect()
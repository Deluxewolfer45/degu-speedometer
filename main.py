import gc
import uasyncio
import _thread
import network
import math
import time
import os
import array
from request_parser import RequestParser
from wifi_connection import wifi_connect
from hall_effect_monitor_v5 import hallEffectStats
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2, PEN_P4

display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2, pen_type=PEN_P4, rotate=0)
display.set_backlight(1)
display.set_font("bitmap8")
WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)
GOLD = display.create_pen(255,215,0)
   
protocol = b"HTTP/1.1"
server = b"speedydegus"
    
wifi_connect()

hall_effect_stats  = hallEffectStats()
second_thread = _thread.start_new_thread(hall_effect_stats.monitor, ())

check = array.array('I', [0, 0, 0, 0])

def formatTime(value):
    if value < 60:
        return str(round(value)) + ' s'
    elif value < 3600:
        return str(math.floor(value / 60)) + 'm ' + str(round(value % 60)) + 's'
    elif value < 360000:
        return str(math.floor(value / 3600)) + 'h ' + str(round((value / 60) % 60)) + 'm'

async def lcd_screen(hall_effect_stats, check):
    while True:
        try:
            if hall_effect_stats.rot_time > 0:
                check[1] = 0
                check[2] = 0
                check[3] = 0
                current_speed = round((hall_effect_stats.wheel_distance / (hall_effect_stats.rot_time/1e6)) * 3600 / 1000, 1)
                run_distance = str(round((hall_effect_stats.wheel_distance * hall_effect_stats.run_rots)))
                run_duration = formatTime(hall_effect_stats.run_duration/1e6)
                
                if check[0] == 0:
                    display.set_pen(BLACK)
                    display.clear()
                
                if current_speed < 10:
                    speed_x = 30
                else:
                    speed_x = 10
                    
                display.set_pen(BLACK)
                display.rectangle(10, 40, 180, 100)
                display.rectangle(30, 170, 180, 100)
                display.rectangle(180, 170, 180, 100)
                display.set_pen(WHITE)
                display.text("Current Speed", 100, 12, 320, 2)
                display.text("km/h", 190, 70, 320, 6)
                display.text("Distance", 30, 145, 320, 2)
                display.text("Duration", 180, 145, 320, 2)
                display.text(str(current_speed), speed_x, 42, 320, 10)
                display.text(run_distance + " m", 30, 172, 320, 5)
                display.text(run_duration, 180, 172, 320, 5)
                display.update()
                time.sleep(1)
                check[0] += 1
                
            elif check[0] > 0:
                check[0] = 0
                display.set_pen(BLACK)
                display.clear()
                
                if hall_effect_stats.new_record == ["", "", "", "", "", "", ""]:
                    check[2] = 1
                    display.set_pen(WHITE)
                    display.text("Last Run", 85, 10, 320, 4)
                    display.text("Distance:", 10, 75, 320, 3)
                    display.text(str(round(hall_effect_stats.run_distance)) + " m", 180, 75, 320, 3)
                    display.text("Duration:", 10, 130, 320, 3)
                    display.text(formatTime(hall_effect_stats.run_duration), 180, 130, 320, 3)
                    display.text("Top Speed:", 10, 185, 320, 3)
                    display.text(str(round(hall_effect_stats.run_top_speed, 1)) + " km/h", 180, 185, 320, 3)
                    display.update()
                    start_time = time.ticks_ms()
                else:
                    check[3] = 1
                    new_record = hall_effect_stats.new_record
                    record_count = len([element for element in new_record if element != ""])
                    
                    for i in range(len(new_record)):
                        if record_count > 1:
                            new_record_string1 = "Multiple"
                            new_record_string2 = "New Records Set"
                            string1_x = 105
                            string2_x = 55
                            break
                        elif new_record[i] == "top_speed":
                            new_record_string1 = "Top Speed:"
                            new_record_string2 = str(round(hall_effect_stats.top_speed_record[0], 1)) + "km/h"
                            string1_x = 90
                            string2_x = 105
                        elif new_record[i] == "10m_record":
                            new_record_string1 = "Fastest 10m:"
                            new_record_string2 = str(round(hall_effect_stats.fastest_10m_record[0], 2)) + " s"
                            string1_x = 80
                            string2_x = 125
                        elif new_record[i] == "100m_record":
                            new_record_string1 = "Fastest 100m:"
                            new_record_string2 = str(round(hall_effect_stats.fastest_100m_record[0], 2)) + " s"
                            string1_x = 75
                            string2_x = 120
                        elif new_record[i] == "longest_run_dist":
                            new_record_string1 = "Longest Run Distance:"
                            new_record_string2 = str(round(hall_effect_stats.longest_run_record[0])) + " m"
                            string1_x = 15
                            string2_x = 120
                        elif new_record[i] == "longest_run_time":
                            new_record_string1 = "Longest Run Duration:"
                            new_record_string2 = formatTime(hall_effect_stats.longest_run_record[2])
                            string1_x = 15
                            string2_x = 120
                        elif new_record[i] == "longest_run":
                            new_record_string1 = "Longest Run:"
                            new_record_string2 = str(round(hall_effect_stats.longest_run_record[0])) + "m (" + formatTime(hall_effect_stats.longest_run_record[2]) + ")"
                            string1_x = 80
                            string2_x = 105
                        elif new_record[i] == "max_distance_day":
                            new_record_string1 = "Furthest Day Distance:"
                            new_record_string2 = str(round(hall_effect_stats.max_distance_day_record[0])) + "m"
                            string1_x = 10
                            string2_x = 130
                    
                    display.set_pen(GOLD)
                    display.rectangle(0, 0, 320, 240)
                    display.set_pen(WHITE)
                    display.text("NEW", 100, 10, 320, 8)
                    display.text("RECORD", 45, 80, 320, 8)
                    display.text(new_record_string1, string1_x, 170, 320, 3)
                    display.text(new_record_string2, string2_x, 200, 320, 3)
                    display.update()
                    start_time = time.ticks_ms()
                    
            elif check[2] == 1:
                if (time.ticks_ms() - start_time)/1e3 > 10:
                    check[2] = 0
            elif check[3] == 1:
                if (time.ticks_ms() - start_time)/1e3 > 10:
                    check[3] = 0
                    check[2] = 1
                    display.set_pen(BLACK)
                    display.clear()
                    display.set_pen(WHITE)
                    display.text("Last Run", 85, 10, 320, 4)
                    display.text("Distance:", 10, 75, 320, 3)
                    display.text(str(round(hall_effect_stats.run_distance)) + " m", 180, 75, 320, 3)
                    display.text("Duration:", 10, 130, 320, 3)
                    display.text(formatTime(hall_effect_stats.run_duration), 180, 130, 320, 3)
                    display.text("Top Speed:", 10, 185, 320, 3)
                    display.text(str(round(hall_effect_stats.run_top_speed, 1)) + " km/h", 180, 185, 320, 3)
                    display.update()
                    start_time = time.ticks_ms()
            else:
                check[0] = 0
                
                if check[1] == 0:
                    display.set_pen(BLACK)
                    display.clear()
                    
                display.set_pen(BLACK)
                display.rectangle(10, 40, 200, 20)
                display.set_pen(WHITE)
                display.text("Today", 110, 10, 320, 4)
                display.text("Distance:", 10, 60, 320, 3)
                display.text(str(round(hall_effect_stats.distance_today)) + " m", 180, 60, 320, 3)
                display.text("Time:", 10, 105, 320, 3)
                display.text(formatTime(hall_effect_stats.time_today), 180, 105, 320, 3)
                display.text("Runs:", 10, 150, 320, 3)
                display.text(str(round(hall_effect_stats.runs_today)), 180, 150, 320, 3)
                display.text("Top Speed:", 10, 195, 320, 3)
                display.text(str(round(hall_effect_stats.top_speed_today, 1)) + " km/h", 180, 195, 320, 3)
                display.text("Visit speedydegus/ for more stats", 85, 230, 320, 1)
                display.update()
                check[1] += 1
                
            await uasyncio.sleep(0)
             
        except KeyboardInterrupt:
            machine.reset()    

async def handle_request(reader, writer):
    try:
        raw_request = await reader.read(2048)
        request = RequestParser(raw_request)

        gc.collect()
        print(request.method, request.url)
        if request.method == 'POST':
            if request.url == "/readData":
                request.url = "/data.json"
                content_type = b"application/json"
                status_msg = b"200 OK"
                
                if hall_effect_stats.rot_time > 0:
                    current_speed = str(round((hall_effect_stats.wheel_distance / (hall_effect_stats.rot_time/1e6)) * 3600 / 1000, 1))
                else:
                    current_speed = str(0)
                
                last_run_time = str(round(hall_effect_stats.last_run_time/1e3))
                    
                additional_data = b', "current_speed": ' + current_speed + b', "last_run_time": ' + last_run_time

                with open('data.json', 'rb') as file:
                    response = file.read()
                    closing_bracket_index = response.rindex(b']')
                    response = response[:closing_bracket_index+1] + additional_data + response[closing_bracket_index+1:]
                
        elif request.method == 'GET':
            # Try to serve static file
            status_msg = b"200 OK"
            if request.url == "/":
                request.url = "/index v5.html"
                content_type = b"text/html"
            elif request.url == "/mystyle.css":
                content_type = b"text/css"
            elif request.url == "/website_scripts.js":
                content_type = b"text/javascript"
            elif request.url == "/favicon.ico":
                content_type = b"image/x-icon"
            elif request.url == "/degu_running_tiles.png":
                content_type = b"image/x-icon"
            elif request.url == "/degu_sleep_tiles.png":
                content_type = b"image/x-icon"
            elif request.url == "/apple-touch-icon.png":
                content_type = b"image/x-icon"
            else:
                status_msg = b"404 Not Found"
                content_type = b"text/plain"
                
            with open(request.url, 'rb') as file:
                response = file.read()
            
        content_length = str(len(response))
            
        responseText = b""
        responseText += protocol + b" " + status_msg + b"\r\n"
        responseText += b"Server: " + server + b"\r\n"
        responseText += b"Content-Type: " + content_type + b"\r\n"
        responseText += b"Content-Length: " + content_length + b"\r\n"
        responseText += b"Connection: Closed\r\n"
        responseText += b"\r\n"																				
        response = responseText + response
                
        gc.collect()
        writer.write(response)
        await writer.drain()
        await writer.wait_closed()
    
    except OSError as e:
        print('connection error ' + str(e.errno) + " " + str(e))

loop = uasyncio.get_event_loop()
loop.create_task(uasyncio.start_server(handle_request, "0.0.0.0", 80))
loop.create_task(lcd_screen(hall_effect_stats, check))
loop.run_forever()
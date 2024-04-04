import machine
import time
import math
import gc
import json
import os
import array
import ntptime

class hallEffectStats:
    def __init__(self):
        # Setting Default Variable Values
        self.date = time.localtime()
        self.new_record = ["", "", "", "", "", "", ""] # Checks if new record was set after run
        
        # Runs
        self.rot_time = 0
        self.run_rots = 0
        self.run_distance = 0
        self.run_duration = 0
        self.run_top_speed = 0
        self.run_min_rot_time = 1000000000
        self.last_run_time = 0 # Time since last run in s
        
        # Data File
        self.json_file = 'data.json'
        os.chdir("/") # Make sure working from root directory
        dir_contents = os.listdir("/")  # Get directory listing
        
        # Setting Variable Values: Distances in m, times in s, speeds in km/h and calories in kcal
        if self.json_file in dir_contents:
            with open(self.json_file, 'r') as file:
                data = json.load(file)
            
            for key, value in data.items():
                setattr(self, key, value)
        
        else:
            # Setting Default Stats Values
            self.start_date = "{:02d}/{:02d}/{:02d}".format(self.date[2], self.date[1], self.date[0] % 100) # Start Date of Stats
            self.start_date_time = time.time()
            self.days_active = 1
            
            # Last Recorded Date: Hour, Day, Month, Year
            self.old_date = [self.date[3], self.date[2], self.date[1], self.date[0]]
            
            # Stats Today
            self.distance_today = 0
            self.time_today = 0
            self.top_speed_today = 0
            self.runs_today = 0
            
            # All Time Stats Lists: All Time Total, Averages Per Day, Week, Month, Year
            self.distance_all_time = [0, 0]
            self.time_all_time = [0, 0]
            self.avg_speed_all_time = 0
            self.runs_all_time = [0, 0]
            self.calories_all_time = [0, 0]
            self.rotations_all_time = [0, 0]
            self.peanuts_all_time = [0, 0]
            
            # Records: Value, Date Set
            self.new_record_day = ["", "", "", "", ""] # Stores new records that day
            self.top_speed_record = [0, "-"] 
            self.fastest_10m_record = [10000, "-"]
            self.fastest_100m_record = [10000, "-"]
            self.longest_run_record = [0, "-", 0, "-"]
            self.max_distance_day_record = [0, "-"]
            
            # Distance History
            self.distance_hour = [0]*24 # By hour all time
            self.distance_month = [0]*12 # By month all time
            
            # Frequency Distributions
            self.speed_frequency = [0]*26
            self.run_distance_frequency = [0]*31
            self.run_time_frequency = [0]*13
            
            # Run Averages
            self.avg_run_distance = 0
            self.avg_run_duration = 0
            
            self.json_save(self.json_file)
            
    def json_save(self, json_file):
        # Saving Stats to File:
        with open(json_file, "w") as file:
            json.dump(
                {
                    "start_date": self.start_date,
                    "start_date_time": self.start_date_time,
                    "days_active": self.days_active,
                    "old_date": [n for n in self.old_date],
                    
                    "distance_today": round(self.distance_today, 0),
                    "time_today": round(self.time_today, 0),
                    "top_speed_today": round(self.top_speed_today, 1),
                    "runs_today": self.runs_today,
                    
                    "distance_all_time": [ round(n, 0) for n in self.distance_all_time],
                    "time_all_time": [ round(n, 0) for n in self.time_all_time],
                    "avg_speed_all_time": round(self.avg_speed_all_time, 1),
                    "runs_all_time": [ round(n, 1) for n in self.runs_all_time],
                    "calories_all_time": [ round(n, 2) for n in self.calories_all_time],
                    "rotations_all_time": [ round(n, 0) for n in self.rotations_all_time],
                    "peanuts_all_time": [ round(n, 1) for n in self.peanuts_all_time],
                    
                    "new_record_day": self.new_record_day,
                    "top_speed_record": [round(self.top_speed_record[0], 1), self.top_speed_record[1]],
                    "fastest_10m_record": [round(self.fastest_10m_record[0], 2), self.fastest_10m_record[1]],
                    "fastest_100m_record": [round(self.fastest_100m_record[0], 2), self.fastest_100m_record[1]],
                    "longest_run_record": [round(self.longest_run_record[0], 0), self.longest_run_record[1], round(self.longest_run_record[2], 0), self.longest_run_record[3]],
                    "max_distance_day_record": [round(self.max_distance_day_record[0], 0), self.max_distance_day_record[1]],
                    
                    "distance_hour": [ round(n, 1) for n in self.distance_hour],
                    "distance_month": [ round(n, 1) for n in self.distance_month],
                    
                    "speed_frequency": [ round(n, 1) for n in self.speed_frequency],
                    "run_distance_frequency": [ round(n, 1) for n in self.run_distance_frequency],
                    "run_time_frequency": [ round(n, 1) for n in self.run_time_frequency],
                    
                    "avg_run_distance": round(self.avg_run_distance, 1),
                    "avg_run_duration": round(self.avg_run_duration, 1)
                }, file)
  
        print("Data Recorded")
        
    def monitor(self):
        # Input Variables:
        wheel_diameter = 0.3 # Wheel diameter in m
        degu_mass = 250 # Degu average mass in g
        min_speed = 1 # Minimum speed in km/h
        run_threshold = 2.52 # Speed at which walking becomes running for calorie calculation
        peanut_calories = 2.95 # Assuming 1 peanut is 0.5g
        self.wheel_distance = wheel_diameter * math.pi
        no_speeds = 26 # Number of speeds to record in frequency array
        dst_check = "" # Check for changing time for daylight savings time
        
        # Hall Effect
        hall_effect = machine.Pin(22, machine.Pin.IN)
        hall_effect_prv = 1
        
        # Starts
        start_run_time = 0 # Start run time measurement
        end_run_time = 0 # End run time measurement
        start_time = 0 # Start RPM measurement
        
        # Run Variables
        self.run_rots = 0
        self.rot_time = 0
        run_rot_time_threshold = (self.wheel_distance / (run_threshold * 1000 / 3600)) * 1e6
        run_walk_time = array.array('I', [0, 0]) # Stores walking and running time for run
        run_walk_rot = array.array('I', [0, 0]) # Stores walking and running rotations for run
        run_calories = 0
        run_peanuts = 0
        run_top_speed = 0
        speed_rot_times = array.array('I', [round(self.wheel_distance * 1e6 / (i * 1000 / 3600)) for i in range(1, no_speeds)])
        run_speed_frequency = array.array('I', [0]*no_speeds)
        
        # Threshold
        time_elap = 0
        threshold = int(self.wheel_distance * 1e6 / (min_speed * 1000 / 3600))
        
        # Record Variables
        min_rot = bytes([math.ceil(10/self.wheel_distance), math.ceil(100/self.wheel_distance)]) # Rotations required to cover 10m
        fract_rot = array.array('f', [(10/self.wheel_distance) / min_rot[0], (100/self.wheel_distance) / min_rot[1]]) # Fraction of required rotations that is 10m and 100m
        array_10m = array.array('I', [0]*min_rot[0]) # Rotation times for recording 10m record
        array_100m = array.array('I', [0]*min_rot[1]) # Rotation times for recording 100m record
        current_10m = 0 # Current 10m time
        current_100m = 0 # Current 100m time
        run_rot_10m_record = 10000000000 / fract_rot[0] # Record run 10m minimum rotations time
        run_rot_100m_record = 10000000000 / fract_rot[1] # Record run 100m minimum rotations time
        
        # Date
        self.date = time.localtime()
        new_date = array.array('I', ([self.date[3], self.date[2], self.date[1], self.date[0]]))
                    
        # Recording how date has changed, 1 = No Change, 0 = Change
        date_check = 1 if self.old_date[1] == new_date[1] else 0
        
        gc.collect()
        #x = 0
        while True:
            #x += 1
            #if x % 10 == 0:
                #print(gc.mem_free())
            try:
                # If reading is no magnet
                if hall_effect.value() == 1:
                    # If previous reading was a magnet
                    if hall_effect_prv == 0:
                        # If currently in a run
                        if start_time != 0:
                            self.rot_time = time.ticks_diff(time.ticks_us(), start_time)
                            self.run_rots += 1
                            self.run_duration += self.rot_time
                            
                            # Speed Frequency
                            for i in range(0, no_speeds):
                                if i == no_speeds - 1:
                                    if self.rot_time < speed_rot_times[-1]:
                                        run_speed_frequency[i] += 1
                                        break
                                elif self.rot_time > speed_rot_times[i]:
                                    run_speed_frequency[i] += 1
                                    break
                            
                            # 10m and 100m records
                            current_10m = current_10m + self.rot_time - array_10m[(self.run_rots - 1) % min_rot[0]]
                            current_100m = current_100m + self.rot_time - array_100m[(self.run_rots - 1) % min_rot[1]]
                            array_10m[(self.run_rots - 1) % min_rot[0]] = self.rot_time
                            array_100m[(self.run_rots - 1) % min_rot[1]] = self.rot_time
                            
                            if self.run_rots > min_rot[0] and current_10m < run_rot_10m_record:
                                run_rot_10m_record = current_10m
                            
                            if self.run_rots > min_rot[1] and current_100m < run_rot_100m_record:
                                run_rot_100m_record = current_100m

                            # Calories 
                            run_walk_time[int(self.rot_time > run_rot_time_threshold)] += self.rot_time
                            run_walk_rot[int(self.rot_time > run_rot_time_threshold)] += 1

                            self.run_min_rot_time = min(self.run_min_rot_time, self.rot_time)
                            
                            #print(time.ticks_diff(time.ticks_us(), end_time))
                            
                        # If not currently in a run
                        else:
                            # Start run, reset run stats
                            start_run_time = time.ticks_ms()
                            self.run_duration = 0
                            self.run_top_speed = 0
                            run_rot_10m_record = 10000000000 / fract_rot[0]
                            run_rot_100m_record = 10000000000 / fract_rot[1]
                            self.run_min_rot_time = 1000000000
                            self.run_top_speed = 0
                            self.new_record = ["", "", "", "", "", "", ""]
                            run_walk_time[0] = 0
                            run_walk_time[1] = 0
                            run_walk_rot[0] = 0
                            run_walk_rot[1] = 0
                            
                        start_time = time.ticks_us() # Recording start time for next RPM measurement
                        
                    hall_effect_prv = 1 # Recording hall effect state for comparison in next loop
                    
                # If reading magnet
                else:
                    hall_effect_prv = 0 # Recording hall effect state for comparison in next loop
                
                if start_time == 0:
                    # Records current date
                    self.date = time.localtime()
                    gc.collect()
                    new_date[0] = self.date[3]
                    new_date[1] = self.date[2]
                    new_date[2] = self.date[1]
                    new_date[3] = self.date[0]
                    
                    # Recording how date has changed, 1 = No Change, 0 = Change
                    date_check = 1 if self.old_date[1] == new_date[1] else 0
                    self.old_date = new_date[:] # Copies old date
                    
                    # If last Sunday in March:
                    if dst_check == "Mar":
                        # If 1am
                        if self.date[3] == 1:
                            ntptime.settime() # Reset time
                            dst_check = "" # Reset dst_check
                    
                    # If last Sunday in October:
                    elif dst_check == "Oct":
                        # If 2am
                        if self.date[3] == 2:
                            ntptime.settime() # Reset time
                            dst_check = "" # Reset dst_check
                    
                    # Resets recent stats according to how the date has changed
                    if date_check == 0:
                        self.distance_today = 0
                        self.time_today = 0
                        self.top_speed_today = 0
                        self.runs_today = 0

                        self.days_active = max(1, math.floor((time.time() - self.start_date_time)/(60 * 60 * 24)))
                        self.new_record_day = ["", "", "", "", ""]
                        self.json_save(self.json_file)
                        self.json_save("data_backup.json")
                        
                        # Calculates day in March and October for the year to change clocks for daylight savings time
                        mar_day_dst = (31 - (int(5 * self.date[0]/4 + 4)) % 7)
                        oct_day_dst = (31 - (int(5 * self.date[0]/4 + 1)) % 7)
                        
                        if self.date[2] == mar_day_dst:
                            dst_check = "Mar"
                        elif self.date[2] == oct_day_dst:
                            dst_check = "Oct"
                    
                    self.last_run_time = time.ticks_diff(time.ticks_ms(), end_run_time)
                    
                elif start_time != 0:
                    time_elap = time.ticks_diff(time.ticks_us(),start_time) # Time elapsed since last start time of RPM measurement
                    
                    # If time elapsed since last start time of RPM measurement is greater than threshold value
                    if time_elap > threshold and self.run_rots != 0:
                        # Ending run and recording run data
                        end_run_time = time.ticks_ms()
                        self.run_duration = time.ticks_diff(end_run_time, start_run_time) / 1e3 - time_elap / 1e6
                        self.run_distance = self.run_rots * self.wheel_distance
                        self.avg_run_duration = (self.avg_run_duration * self.runs_all_time[0] + self.run_duration)/(self.runs_all_time[0] + 1)
                        self.avg_run_distance = (self.avg_run_distance * self.runs_all_time[0] + self.run_distance)/(self.runs_all_time[0] + 1)
                        run_avg_speed = (self.run_distance * 3600)/(self.run_duration * 1000)
                        self.run_top_speed = (self.wheel_distance / (self.run_min_rot_time / 1e6)) * 3600 / 1000
                        self.rot_time = 0
                        
                        if run_walk_time[0] > 0:
                            run_calories += (20.1 * degu_mass * run_walk_time[0]/1e6) * (5.76 + 1.41 * (self.wheel_distance/((run_walk_time[0]/1e6)/run_walk_rot[0]))) / 15062400
                        
                        if run_walk_time[1] > 0:
                            run_calories += (20.1 * degu_mass * run_walk_time[1]/1e6) * (2.91 + 3.8 * (self.wheel_distance/((run_walk_time[1]/1e6)/run_walk_rot[1]))) / 15062400
                                                                                 
                        run_peanuts = run_calories/peanut_calories
                        
                        # Today Totals
                        self.distance_today += self.run_distance
                        self.time_today += self.run_duration
                        self.top_speed_today = max(self.top_speed_today, self.run_top_speed)
                        self.runs_today += 1
                                    
                        # All Time Totals
                        self.avg_speed_all_time = (self.avg_speed_all_time * self.runs_all_time[0] + run_avg_speed)/(self.runs_all_time[0] + 1)
                        
                        self.distance_all_time[0] += self.run_distance
                        self.time_all_time[0] += self.run_duration
                        self.runs_all_time[0] += 1
                        self.calories_all_time[0] += run_calories
                        self.rotations_all_time[0] += self.run_rots
                        self.peanuts_all_time[0] += run_peanuts
                        
                        # Calculate the averages for each element in the list using list comprehensions
                        self.distance_all_time[1] = self.distance_all_time[0] / self.days_active
                        self.time_all_time[1] = self.time_all_time[0] / self.days_active
                        self.runs_all_time[1] = self.runs_all_time[0] / self.days_active
                        self.calories_all_time[1] = self.calories_all_time[0] / self.days_active
                        self.rotations_all_time[1] = self.rotations_all_time[0] / self.days_active
                        self.peanuts_all_time[1] = self.peanuts_all_time[0] / self.days_active

                        # Records
                        if self.run_top_speed > self.top_speed_record[0]:
                            self.new_record[0] = "top_speed"
                            self.new_record_day[0] = "top_speed"
                            self.top_speed_record= [self.run_top_speed, "{:02d}/{:02d}/{:02d} at {:02d}:{:02d}".format(new_date[1], new_date[2], new_date[3] % 100, time.localtime()[3], time.localtime()[4])]
                        
                        if (run_rot_10m_record * fract_rot[0])/1e6 < self.fastest_10m_record[0]:
                            self.new_record[2] = "10m_record"
                            self.new_record_day[1] = "10m_record"
                            self.fastest_10m_record = [(run_rot_10m_record * fract_rot[0])/1e6, "{:02d}/{:02d}/{:02d} at {:02d}:{:02d}".format(new_date[1], new_date[2], new_date[3] % 100, time.localtime()[3], time.localtime()[4])]
                            
                        if (run_rot_100m_record * fract_rot[1])/1e6 < self.fastest_100m_record[0]:
                            self.new_record[2] = "100m_record"
                            self.new_record_day[2] = "100m_record"
                            self.fastest_100m_record = [(run_rot_100m_record * fract_rot[1])/1e6, "{:02d}/{:02d}/{:02d} at {:02d}:{:02d}".format(new_date[1], new_date[2], new_date[3] % 100, time.localtime()[3], time.localtime()[4])]
                              
                        if self.run_distance > self.longest_run_record[0]:
                            self.new_record[3] = "longest_run_dist"
                            self.new_record_day[3] = "longest_run"
                            self.longest_run_record[0] = self.run_distance
                            self.longest_run_record[1] = "{:02d}/{:02d}/{:02d} at {:02d}:{:02d}".format(new_date[1], new_date[2], new_date[3] % 100, time.localtime()[3], time.localtime()[4])
                        
                        if self.run_duration > self.longest_run_record[2]:
                            if "longest_run_dist" in self.new_record:
                                self.new_record[5] = "longest_run"
                                self.new_record[3] = ""
                            else:
                                self.new_record[4] = "longest_run_time"
                            
                            self.new_record_day[3] = "longest_run"
                            self.longest_run_record[2] = self.run_duration
                            self.longest_run_record[3] = "{:02d}/{:02d}/{:02d} at {:02d}:{:02d}".format(new_date[1], new_date[2], new_date[3] % 100, time.localtime()[3], time.localtime()[4])
                        
                        if self.distance_today > self.max_distance_day_record[0]:
                            self.new_record[6] = "max_distance_day"
                            self.new_record_day[4] = "max_distance_day"
                            self.max_distance_day_record = [self.distance_today, "{:02d}/{:02d}/{:02d} at {:02d}:{:02d}".format(new_date[1], new_date[2], new_date[3] % 100, time.localtime()[3], time.localtime()[4])]
                        
                        # Distance History
                        for i in range(0, len(self.distance_hour)):
                            self.distance_hour[i] /= 100
                            self.distance_hour[i] *= self.distance_all_time[0] - self.run_distance
                            self.distance_hour[i] += self.run_distance if i == self.old_date[0] else 0
                            self.distance_hour[i] /= self.distance_all_time[0]
                            self.distance_hour[i] *= 100
                            
                        for i in range(0, len(self.distance_month)):
                            self.distance_month[i] /= 100
                            self.distance_month[i] *= self.distance_all_time[0] - self.run_distance
                            self.distance_month[i] += self.run_distance if i == self.old_date[2] - 1 else 0
                            self.distance_month[i] /= self.distance_all_time[0]
                            self.distance_month[i] *= 100
                            
                        # Frequency Distributions
                        for i in range(0, len(self.speed_frequency)):
                            self.speed_frequency[i] = (self.speed_frequency[i] / 100 * self.rotations_all_time[0]) + run_speed_frequency[i]
                            self.speed_frequency[i] = (self.speed_frequency[i] / (self.rotations_all_time[0] + sum(run_speed_frequency))) * 100
                        
                        for i in range(0, len(self.run_distance_frequency)):
                            self.run_distance_frequency[i] /= 100
                            self.run_distance_frequency[i] *= self.runs_all_time[0] - 1
                            if i == min(math.floor(self.run_distance/10), 30):
                                self.run_distance_frequency[min(math.floor(self.run_distance/10), 30)] += 1 
                            self.run_distance_frequency[i] /= self.runs_all_time[0]
                            self.run_distance_frequency[i] *= 100
                        
                        for i in range(0, len(self.run_time_frequency)):
                            self.run_time_frequency[i] /= 100
                            self.run_time_frequency[i] *= self.runs_all_time[0] - 1
                            if i == min(math.floor(self.run_duration/10), 12):
                                self.run_time_frequency[min(math.floor(self.run_duration/10), 12)] += 1
                            self.run_time_frequency[i] /= self.runs_all_time[0]
                            self.run_time_frequency[i] *= 100
                                              
                        # Resetting for next run
                        start_time = 0
                        time_elap = 0
                        self.run_rots = 0
                        
                        self.json_save(self.json_file)
                  
                #print(time.ticks_us() - start_test)
                time.sleep(0.01)
            except KeyboardInterrupt:
                 break
                
#hall_effect_stats = hallEffectStats()
#hall_effect_stats.monitor()
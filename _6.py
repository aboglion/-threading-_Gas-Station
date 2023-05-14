import threading
import time
import random
FUEL_TOTAL=1000 #כמות דלק בתחנה כוללת
PUMPS_TOTAL=10 #מספר עמדות תדלוק בתחנה
WORKING_TIME_SEC=100  #כמה שניות שהתחנה עובדת 
REFULING_SPEED=40 # כמה שניות שלוקח לכל רכב למלא דלק ממצב ריק לגמרי
how_many_cars_in_world=100 #כמות רכבים מקסמלית שיש בכבישים

#כאשר התחנה מלאה ברכבים זהו אובייקט התנאי שישמש ל- wait () ו- notify ().
cond = threading.Condition()
# This is the lock object that will be used to protect the shared variable.
lock = threading.Lock()

class Vehicle:
    id =10000 #מספר רכב
    counter=0 #כמות  מכוניות
    def __init__(self, license_number, fuel_level,tank_size=60):
        self.license_number = Vehicle.id
        self.fuel_level = random.randint(0, 100)
        self.tank_size=tank_size
        self.Station_fule_after_fuled=0
        Vehicle.id+=1
        Vehicle.counter+=1
        print(f'Vehicle created, license number: {Vehicle.id}, fuel level: {self.fuel_level}%')
        
    def enter_station(self, station):
        if station.free_pumps<=0:#אם כל העמדות ה10 תופוסות אז תהליכון יחכה בתור
            with cond: 
                print(f'🚦🚦<><><><>🚦!! Vehicle {self.license_number} Waiting TO Free Pump ... !!🚦<><><><>🚦🚦')
                cond.wait() #Waiting for notification of free pump to proceed
        if station.fuel > 0 and not station.closed:
            with lock:
                station.free_pumps-=1
                station.vehicles.append(self)
                print(f'|     _🚙Vehicle {self.license_number} entered the station.🚙_<---      |<------')
            self.refuel(station)
        else:self.leave_station(station)

    def refuel(self, station):
        liters_enters=-1
        if station.fuel <= 0 or station.closed:
            self.leave_station(station)
        start_time=time.time()
        refuel_time=REFULING_SPEED * (100 - self.fuel_level) / 100
        print(f'|🏧🏧🏧🚙Vehicle {self.license_number} Try to Refueling NOW.....🚙🏧🏧🏧|<-----O')
        while (self.fuel_level<100 and station.fuel > 0 and not station.closed):
              #מחשב זמן תדלוק וממתין באופן יחסי למהירות תדלוק ולמצב מיכל ברכב
            time.sleep(1)
            elapsed_time = time.time() - start_time
            if elapsed_time >= refuel_time:  # If refuel time has passed, the tank should be full.
                liters_enters = self.tank_size - (self.fuel_level / 100 * self.tank_size)
                self.fuel_level = 100
            else:  # If not, calculate the fueling proportionally.
                fueling = elapsed_time / refuel_time
                liters_enters = self.tank_size * fueling
                self.fuel_level += fueling * 100
            with lock:
                # Check that the station has enough fuel, otherwise adjust the liters entered and the fuel level.
                if station.fuel < liters_enters:
                    liters_enters = station.fuel
                    self.fuel_level = station.fuel / self.tank_size * 100
                station.fuel -= liters_enters
                self.Station_fule_after_fuled = station.fuel
            
        if (liters_enters==0):print(f'👻Sorry no fule -> Vehicle {self.license_number} refueled {liters_enters} Liters 👻👻' )
        else:print(f' ✅✅✅ -> Vehicle {self.license_number} refueled {liters_enters} Liters ✅✅✅' )
        self.leave_station(station)


    def leave_station(self, station):
        print(f'----->🚗 Vehicle {self.license_number} leave the station - the station fuel level: {self.Station_fule_after_fuled} liters.🚗----->  ')
        with lock:
            if self in station.vehicles:
                station.vehicles.remove(self)
            Vehicle.counter-=1
            station.free_pumps+=1
            with cond:cond.notify()



class GasStation:
    def __init__(self, initial_fuel, pumps, closing_time):
        self.fuel = initial_fuel
        self.free_pumps = pumps
        self.closing_time = closing_time
        self.vehicles = []
        self.closed = False

    def run_station(self):
        start_time = time.time()
        while not self.closed or self.vehicles:  # Keep station open if there are vehicles left
            if self.fuel <= 0:
                self.closed = True
                print('-----❌❌Station closed for reason - 💧fuel ran out.❌❌------')
                exit()
        
            if time.time() - start_time > self.closing_time:
                self.closed = True
                print('------⛔⛔Station closed for reason - closing time.⛔⛔------')
                exit()
            time.sleep(0.1)  # Sleep to allow other threads to run

def simulate():
    main_station = GasStation(FUEL_TOTAL, PUMPS_TOTAL, WORKING_TIME_SEC)
    station_thread = threading.Thread(target=main_station.run_station)
    station_thread.start()

    # Create threads
    threads = []
    while not main_station.closed:
        license_number = random.randint(1000, 9999999999)
        fuel_level=random.randint(0, 100)
        tank_size=random.randint(30, 80)
        vehicle = Vehicle(license_number, fuel_level,tank_size)
        if Vehicle.counter > how_many_cars_in_world-1:
            time.sleep(2)
        vehicle_thread = threading.Thread(target=vehicle.enter_station, args=(main_station,))
        threads.append(vehicle_thread)
        vehicle_thread.start()
        time.sleep(random.uniform(0.1, 1))
        
    # Join all threads
    for thread in threads:
        thread.join()
    station_thread.join()


simulate()

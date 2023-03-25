"""
Puente sobre el río Tajuña
"""
import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

#SOUTH = 1
#NORTH = 0

NCARS = 10
NPED = 10
TIME_CARS = 0.5  # a new car enters each 0.5s
TIME_PED = 5 # a new pedestrian enters each 5s
TIME_IN_BRIDGE_CARS = (1, 0.5) # normal 1s, 0.5s
TIME_IN_BRIDGE_PEDESTRIAN = (30, 10) # normal 1s, 0.5s

class Monitor():
    def __init__(self):
        self.mutex = Lock()
        self.p = Value('i', 0)
        self.c0 = Value('i', 0)
        self.c1 = Value('i', 0)
        """""
        self.turn = Value('i', 0)
        self.c0_waiting = Value('i', 0)
        self.c1_waiting = Value('i', 0)
        self.p_waiting = Value('i', 0)
        """
        self.no_cars0_no_pedestrians = Condition(self.mutex)
        self.no_cars1_no_pedestrians = Condition(self.mutex)
        self.no_cars = Condition(self.mutex)        
    
    def are_no_cars(self) -> bool:
        return (self.c0.value == 0 and self.c1.value == 0) #and (self.turn.value == 2 or (self.c0_waiting.value == 0 and self.c1_waiting.value == 0))
    
    def are_no_cars0_and_pedestrians(self) -> bool:
    	return (self.c0.value == 0 and self.p.value == 0) #and (self.turn.value == 1 or (self.c0_waiting.value == 0 and self.p_waiting.value == 0))
 
    def are_no_cars1_and_pedestrians(self) -> bool:
    	return (self.c1.value == 0 and self.p.value == 0) #and (self.turn.value == 0 or (self.p_waiting.value == 0 and self.c1_waiting.value == 0))
    	        
    def wants_enter_car(self, direction: int) -> None:
        self.mutex.acquire()
        if direction==0:
            self.no_cars1_no_pedestrians.wait_for(self.are_no_cars1_and_pedestrians)
            self.c0.value += 1
        elif direction==1:
            self.no_cars0_no_pedestrians.wait_for(self.are_no_cars0_and_pedestrians)
            self.c1.value += 1
        self.mutex.release()

    def leaves_car(self, direction: int) -> None:
        self.mutex.acquire() 
        if direction==0:
            self.c0.value -= 1
            #self.turn.value = 1
            if self.c0.value == 0:
                self.no_cars0_no_pedestrians.notify_all()
                self.no_cars.notify_all()
        else:
            self.c1.value -= 1
            #self.turn.value = 2
            if self.c1.value == 0:
                self.no_cars1_no_pedestrians.notify_all()
                self.no_cars.notify_all()
        self.mutex.release()

    def wants_enter_pedestrian(self) -> None:
        self.mutex.acquire()
        self.no_cars.wait_for(self.are_no_cars)
        self.p.value += 1
        self.mutex.release()

    def leaves_pedestrian(self) -> None:
        self.mutex.acquire()
        self.p.value -= 1
        #self.turn.value = 0
        if self.p.value == 0:
                self.no_cars0_no_pedestrians.notify_all()
                self.no_cars1_no_pedestrians.notify_all()
                self.no_cars.notify_all()	
        self.mutex.release()


def delay_car_north() -> None:
    time.sleep(5)

def delay_car_south() -> None:
    time.sleep(5)

def delay_pedestrian() -> None:
    time.sleep(10)

def car(cid: int, direction: int, monitor: Monitor)  -> None:
    print(f"car {cid} heading {direction} wants to enter. {monitor}")
    monitor.wants_enter_car(direction)
    print(f"car {cid} heading {direction} enters the bridge. {monitor}")
    if direction==0 :
        delay_car_north()
    else:
        delay_car_south()
    print(f"car {cid} heading {direction} leaving the bridge. {monitor}")
    monitor.leaves_car(direction)
    print(f"car {cid} heading {direction} out of the bridge. {monitor}")

def pedestrian(pid: int, monitor: Monitor) -> None:
    print(f"pedestrian {pid} wants to enter. {monitor}")
    monitor.wants_enter_pedestrian()
    print(f"pedestrian {pid} enters the bridge. {monitor}")
    delay_pedestrian()
    print(f"pedestrian {pid} leaving the bridge. {monitor}")
    monitor.leaves_pedestrian()
    print(f"pedestrian {pid} out of the bridge. {monitor}")



def gen_pedestrian(monitor: Monitor) -> None:
    pid = 0
    plst = []
    for _ in range(NPED):
        pid += 1
        p = Process(target=pedestrian, args=(pid, monitor))
        p.start()
        plst.append(p)
        time.sleep(random.expovariate(1/TIME_PED))

    for p in plst:
        p.join()

def gen_cars(monitor) -> Monitor:
    cid = 0
    plst = []
    for _ in range(NCARS):
        direction = random.randint(0,1)
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        plst.append(p)
        time.sleep(random.expovariate(1/TIME_CARS))

    for p in plst:
        p.join()

def main():
    monitor = Monitor()
    gcars = Process(target=gen_cars, args=(monitor,))
    gped = Process(target=gen_pedestrian, args=(monitor,))
    gcars.start()
    gped.start()
    gcars.join()
    gped.join()


if __name__ == '__main__':
    main()

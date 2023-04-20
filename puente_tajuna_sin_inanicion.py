"""
Puente sobre el río Tajuña
"""
import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

#SOUTH = 1
#NORTH = 0

NCARS = 10 # Número de coches
NPED = 10 # Número de peatones
TIME_CARS = 0.5  # a new car enters each 0.5s
TIME_PED = 5 # a new pedestrian enters each 5s
TIME_IN_BRIDGE_CARS = (1, 0.5) # normal 1s, 0.5s
TIME_IN_BRIDGE_PEDESTRIAN = (30, 10) # normal 1s, 0.5s

class Monitor():
    def __init__(self):
        """
        Inicialización del monitor.
        
        Args:
            self
        """
        self.mutex = Lock() #Semáforo mutex
        self.p = Value('i', 0) # Valor compartido. Número de peatones cruzando
        self.c0 = Value('i', 0) # Valor compartido. Número de coches cruzando en dirección 0
        self.c1 = Value('i', 0) # Valor compartido. Número de coches cruzando en dirección 1
        self.turn = Value('i', 0) # Valor compartido. Turno
        self.c0_waiting = Value('i', 0) # Valor compartido. Número de coches esperando en dirección 0
        self.c1_waiting = Value('i', 0) # Valor compartido. Número de coches esperando en dirección 1
        self.p_waiting = Value('i', 0) # Valor compartido. Número de peatones esperando
        self.no_cars0_no_pedestrians = Condition(self.mutex) # Variable condición
        self.no_cars1_no_pedestrians = Condition(self.mutex) # Variable condición
        self.no_cars = Condition(self.mutex) # Variable condición        
    
    def are_no_cars(self) -> bool:
        """
        Función que comprueba que no hay coches cruzando en ninguna dirección.
        
        Args:
            self
        """
        return (self.c0.value == 0 and self.c1.value == 0) and (self.turn.value == 2 or (self.c0_waiting.value == 0 and self.c1_waiting.value == 0))
    
    def are_no_cars0_and_pedestrians(self) -> bool:
    	"""
        Función que comprueba que no hay coches cruzando en dirección 0 ni peatones cruzando.
        
        Args:
            self
        """
        return (self.c0.value == 0 and self.p.value == 0) and (self.turn.value == 1 or (self.c0_waiting.value == 0 and self.p_waiting.value == 0))
 
    def are_no_cars1_and_pedestrians(self) -> bool:
    	"""
        Función que comprueba que no hay coches cruzando en dirección 1 ni peatones cruzando.
        
        Args:
            self
        """
        return (self.c1.value == 0 and self.p.value == 0) and (self.turn.value == 0 or (self.p_waiting.value == 0 and self.c1_waiting.value == 0))
    	        
    def wants_enter_car(self, direction: int) -> None:
        """
        El coche quiere cruzar y antes de hacerlo comprueba que no hay nada que se lo impida.
        
        Args:
            self
            direction (int) --> Dirección en la que cruza
        """
        self.mutex.acquire()
        if direction==0:
            self.no_cars1_no_pedestrians.wait_for(self.are_no_cars1_and_pedestrians)
            self.c0.value += 1
        elif direction==1:
            self.no_cars0_no_pedestrians.wait_for(self.are_no_cars0_and_pedestrians)
            self.c1.value += 1
        self.mutex.release()

    def leaves_car(self, direction: int) -> None:
        """
        El coche acaba de cruzar y avisa a otros procesos de que las condiciones para cruzar pueden haber cambiado.
        
        Args:
            self
            direction (int) --> Dirección en la que cruza
        """
        self.mutex.acquire() 
        if direction==0:
            self.c0.value -= 1
            self.turn.value = 1
            if self.c0.value == 0:
                self.no_cars0_no_pedestrians.notify_all()
                self.no_cars.notify_all()
        else:
            self.c1.value -= 1
            self.turn.value = 2
            if self.c1.value == 0:
                self.no_cars1_no_pedestrians.notify_all()
                self.no_cars.notify_all()
        self.mutex.release()

    def wants_enter_pedestrian(self) -> None:
        """
        El peatón quiere cruzar y antes de hacerlo comprueba que no hay nada que se lo impida.
        
        Args:
            self
        """
        self.mutex.acquire()
        self.no_cars.wait_for(self.are_no_cars)
        self.p.value += 1
        self.mutex.release()

    def leaves_pedestrian(self) -> None:
        """
        El peatón acaba de cruzar y avisa a otros procesos de que las condiciones para cruzar pueden haber cambiado.
        
        Args:
            self
        """
        self.mutex.acquire()
        self.p.value -= 1
        self.turn.value = 0
        if self.p.value == 0:
                self.no_cars0_no_pedestrians.notify_all()
                self.no_cars1_no_pedestrians.notify_all()
                self.no_cars.notify_all()	
        self.mutex.release()

"""
Funciones que representan el tiempo que tardan en cruzar tanto coches como peatones
"""

def delay_car_north() -> None:
    time.sleep(5)

def delay_car_south() -> None:
    time.sleep(5)

def delay_pedestrian() -> None:
    time.sleep(10)

def car(cid: int, direction: int, monitor: Monitor)  -> None:
    """
    El coche trata de cruzar el puente en una dirección determinada, solo hará esto si las condiciones para hacerlo se cumplen.
    
    Args:
        cid (int) --> Número de coche
        direction (int) --> Dirección en la que cruza
        monitor (Monitor) --> Monitor
    """
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
    """
    El peaton trata de cruzar el puente, solo hará esto si las condiciones para hacerlo se cumplen.
    
    Args:
        pid (int) --> Número de peatón
        monitor (Monitor) --> Monitor
    """
    print(f"pedestrian {pid} wants to enter. {monitor}")
    monitor.wants_enter_pedestrian()
    print(f"pedestrian {pid} enters the bridge. {monitor}")
    delay_pedestrian()
    print(f"pedestrian {pid} leaving the bridge. {monitor}")
    monitor.leaves_pedestrian()
    print(f"pedestrian {pid} out of the bridge. {monitor}")



def gen_pedestrian(monitor: Monitor) -> None:
    """
    Genera tantos procesos del tipo pedestrian como sea el valor de NPED.

    Args:
        monitor (Monitor) --> Monitor
    """
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
    """
    Genera tantos procesos del tipo car como sea el valor de NCARS.

    Args:
        monitor (Monitor) --> Monitor
    """
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

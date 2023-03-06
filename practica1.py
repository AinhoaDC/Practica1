#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 12:38:36 2023

@author: Ainhoa
"""

from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array
from time import sleep
from random import random, randint

N = 10
K = 10
NPROD = 3
NCONS = 1

def delay(factor = 3):
    sleep(random()/factor)

#Con la siguiente función añadimos el elemento producido por un productor a storage.
def add_data(storage, index, pid, data, mutex, productores):
    mutex.acquire()
    try:
        storage[index.value] = data 
        productores[index.value] = pid
        delay(6)
        index.value = index.value + 1
    finally:
        mutex.release() 

#La función a continuación sirve para añadir un -1 cuando un productor ha terminado de producir. 
def add_data1(storage, index, pid, data, mutex,productores): 
    mutex.acquire()
    try: 
        storage[index.value] = -1 
        productores[index.value] = pid
        delay(6) 
        index.value = index.value + 1 
    finally: 
        mutex.release()


def producer(storage, index, empty, non_empty, mutex, productores):
        data = 0
        for v in range(N): 
            print (f"producer {current_process().name} produciendo")
            delay(6)
            data += randint(1,6)
            empty.acquire()
            add_data(storage, index,int(current_process().name.split('_')[1]),
                     data, mutex, productores)
            non_empty.release()
            print (f"producer {current_process().name} almacenado {v}")
        empty.acquire()
        add_data1(storage, index, int(current_process().name.split('_')[1]),v, mutex, productores) 
        non_empty.release()



def consumer(storage, index, empty, non_empty, mutex, lista_cons, productores): 
    for i in range(NPROD): 
        non_empty[i].acquire() 
    while storage[:] != [-1]*len(storage) :
        minimo = 1000
        pos = 0 
        #No podemos usar la función mínimo para hallarlo puesto que si hay un -1 ese será el número que cogerá
        #por tanto lo hacemos comprabando la lista entera y buscando el menor elemento.
        for j in range(len(storage)): 
            if minimo > storage[j] and storage[j] >= 0 : 
                minimo = storage[j] 
                pos = j  
        productor = productores[pos]
        #Hay que actualizar el valor de index.value para que vuelva a la posición concreta de donde consumimos
        #para que pueda volver a producir un elemento ahí.
        index.value = pos
        #Cuando consumimos un elemento, se queda vacío y se pone -2
        storage[pos] = -2 
        empty[productor].release() 
        delay()  
        non_empty[productor].acquire() 
        #Creamos una lista creciente donde almacenamos el productor que ha producido el valor minimo, y dicho valor. 
        lista_cons.append((productor, minimo)) 
        print(lista_cons)

def main():
    storage = Array('i', NPROD)
    index = Value('i', 0)
    lista_cons = [] 
    productores = Array('i',NPROD)
    for i in range(NPROD):
        storage[i] = -1
    print ("almacen inicial", storage[:], "indice", index.value)
    #Creamos una lista de semáforos, porque ahora lo que queremos es poder usar varios semáforos.
    non_empty = []
    empty = []
    mutex = Lock()
    for i in range(N):
        non_empty.append(Semaphore(0))
        empty.append(BoundedSemaphore(1))
     

    prodlst = [ Process(target=producer,
                        name=f'prod_{i}',
                        args=(storage, index, empty[i], non_empty[i], mutex, productores))
                for i in range(NPROD) ]

    conslst = [ Process(target=consumer,
                      name=f"cons_{i}",
                      args=(storage, index, empty, non_empty, mutex,lista_cons,productores))
                for i in range(NCONS) ]

    for p in prodlst + conslst:
        p.start()

    for p in prodlst + conslst:
        p.join()


if __name__ == '__main__':
    main()

























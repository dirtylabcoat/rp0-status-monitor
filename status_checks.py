#!/usr/bin/env python3

import queue
import socket
import threading
from time import sleep

import requests
from gpiozero import StatusZero
from requests.exceptions import Timeout


class ServiceStatus:
    DOWN = 0
    UP = 1


def show_internet_connection(status_zero: StatusZero, input_queue: queue.Queue):
    while True:
        msg = input_queue.get()
        if msg == ServiceStatus.UP:
            status_zero.one.green.on()
            status_zero.one.red.off()
        elif msg == ServiceStatus.DOWN:
            status_zero.one.green.off()
            status_zero.one.red.on()
        else:
            status_zero.one.green.on()
            status_zero.one.red.on()


def check_dns(hostname='www.google.com'):
    try:
        ip_address = socket.gethostbyname(hostname)
        return (True, ip_address)
    except socket.gaierror:
        return (False, '')


def check_internet_connection(output_queue):
    while True:
        (has_dns, ip_address) = check_dns()
        if has_dns:
            try:
                response = requests.get(f'http://{ip_address}', allow_redirects=True, timeout=5)
                if response.status_code == 200:
                    output_queue.put(ServiceStatus.UP)
                else:
                    output_queue.put(ServiceStatus.DOWN)
            except Timeout:
                output_queue.put(ServiceStatus.DOWN)
        else:
            output_queue.put(ServiceStatus.DOWN)
        sleep(10)


status_zero = StatusZero()
check_internet_queue = queue.Queue()

thread1 = threading.Thread(target=show_internet_connection, args=(status_zero,check_internet_queue,))
thread2 = threading.Thread(target=check_internet_connection, args=(check_internet_queue,))

thread1.start()
thread2.start()

while True:
    pass

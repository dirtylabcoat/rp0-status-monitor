#!/usr/bin/env python3

import queue
import socket
import threading
from time import sleep

import requests
from gpiozero import StatusZero
from requests.exceptions import ConnectionError, Timeout


class ServiceStatus:
    DOWN = 0
    UP = 1


def show_internet_connection(status_zero: StatusZero, input_queue: queue.Queue):
    while True:
        msg = input_queue.get()
        # print(msg)
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
            except Exception:
                output_queue.put(ServiceStatus.DOWN)
        else:
            output_queue.put(ServiceStatus.DOWN)
        sleep(10)

def show_home_server(status_zero: StatusZero, input_queue: queue.Queue):
    while True:
        msg = input_queue.get()
        # print(msg)
        if msg == ServiceStatus.UP:
            status_zero.two.green.on()
            status_zero.two.red.off()
        elif msg == ServiceStatus.DOWN:
            status_zero.two.green.off()
            status_zero.two.red.on()
        else:
            status_zero.two.green.on()
            status_zero.two.red.on()

def check_jellyfin():
    jellyfin_health_url = 'http://my-jellyfin:8096/health'
    try:
        response = requests.get(jellyfin_health_url, allow_redirects=True, timeout=3)
        if response.status_code == 200 and response.text == 'Healthy':
            return True
        else:
            return False
    except Exception:
        return False


def check_home_server(output_queue):
    while True:
        checks = []
        checks.append(check_jellyfin())
        all_checks = all(item == True for item in checks)
        if all_checks:
            output_queue.put(ServiceStatus.UP)
        else:
            output_queue.put(ServiceStatus.DOWN)
        sleep(10)


def show_home_assistant(status_zero: StatusZero, input_queue: queue.Queue):
    while True:
        msg = input_queue.get()
        # print(msg)
        if msg == ServiceStatus.UP:
            status_zero.three.green.on()
            status_zero.three.red.off()
        elif msg == ServiceStatus.DOWN:
            status_zero.three.green.off()
            status_zero.three.red.on()
        else:
            status_zero.three.green.on()
            status_zero.three.red.on()


def check_home_assistant(output_queue):
    home_assistant_health_url = 'http://my-home-assistant/api'
    while True:
        try:
            response = requests.get(home_assistant_health_url, allow_redirects=True, timeout=3) # add Bearer token (long-lived access token) to headers
            response_message_is_ok = True # add proper check here
            if response.status_code == 200 and response_message_is_ok:
                output_queue.put(ServiceStatus.UP)
            else:
                output_queue.put(ServiceStatus.DOWN)
        except (Timeout, ConnectionError):
            output_queue.put(ServiceStatus.DOWN)
        sleep(10)


status_zero = StatusZero()

check_internet_queue = queue.Queue()
check_home_server_queue = queue.Queue()
check_home_assistant_queue = queue.Queue()

thread1 = threading.Thread(target=show_internet_connection, args=(status_zero,check_internet_queue,))
thread2 = threading.Thread(target=check_internet_connection, args=(check_internet_queue,))

thread3 = threading.Thread(target=show_home_server, args=(status_zero,check_home_server_queue,))
thread4 = threading.Thread(target=check_home_server, args=(check_home_server_queue,))

thread5 = threading.Thread(target=show_home_assistant, args=(status_zero,check_home_assistant_queue,))
thread6 = threading.Thread(target=check_home_assistant, args=(check_home_assistant_queue,))

thread1.start()
thread2.start()

thread3.start()
thread4.start()

thread5.start()
thread6.start()

while True:
    pass

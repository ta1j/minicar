import time
import socket
import os
import cv2
import numpy as np
import pygame
from pygame.locals import *
import json


# ESP32に接続
s = socket.socket() # ソケットの作成
host = "192.168.4.2" # 接続先のipアドレス
host2 = "192.168.4.3"
port = 80 # ポート指定

# connect to server
try:
    print(f"Connecting to {host}")
    s.connect((host, port))
    print(f"Successfully connected to {host}")
except ConnectionRefusedError:
    print(f"Connecting to {0}")
    s.connect((host2, port))
    print(f"Successfully connected to {host2}")

    
# connect to controller
pygame.init()
pygame.joystick.init()
try:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Connected to {joystick.get_name()}")
except pygame.error:
    print("Joystick is not connected")
    exit()

interval = 100

file_name = "training_data.npy"
if os.path.isfile(file_name):
    print("File exists, loading previous data")
    training_data = list(np.load(file_name, allow_pickle=True))
    predatasize = len(training_data)
else:
    print("file does not exist, starting fresh")
    training_data = []
    predatasize = 0

def conv_speed(left_y, speed_max):
        speed = -speed_max * left_y
        return int(speed)

def conv_steering(right_x, steer_max, error):
    steering = steer_max * right_x - error
    return int(steering)
  
def controller(mode):
    while True:
        pygame.event.get()
        right_x = joystick.get_axis(2)
        left_y = joystick.get_axis(1)
        x = joystick.get_button(0)  # 終了
        square = joystick.get_button(2)   # 一時停止
        # circle = joystick.get_button(1)
        # triangle = joystick.get_button(3)
        pygame.event.pump()     # イベントの更新

        if square == 1:
            pass
        
        elif x == 1:
            event = {
                "speed": 0,
                "steering": 0,
            }
            msg = json.dumps(event).encode("utf-8")
            s.send(msg)
            print(s.recv(1024))
            break
        else:
            speed_max = 600
            steer_max = 37
            error = 12
            speed = conv_speed(left_y, speed_max)
            steering = conv_steering(right_x, steer_max, error)
            event = {
                "speed": str(speed),
                "steering": str(steering),
            }
            msg = json.dumps(event).encode("utf-8")
            s.send(msg)
            print(s.recv(1024))

            ret, frame = cap.read()
            screen = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            screen = cv2.resize(screen, (80, 60))
            training_data.append([screen, speed, steering])
            cv2.imshow("rotate", frame)
            cv2.imshow("screen", screen)
            
            
            if mode=="capture":
                if len(training_data)%500 == 0:
                    nowtime = time.time()
                    timer = nowtime - starttime
                    print(len(training_data),"datas saved")
                    print(int((len(training_data)-predatasize)/timer),"/sec")
                    np.save(file_name, training_data)
            
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        
    cap.release()
    cv2.destroyAllWindows()


mode = "capture"
try:
    cap = cv2.VideoCapture("http://192.168.4.1:81/stream")
    starttime = time.time()
    print("Ready...")
    time.sleep(1)
    print("start")
    controller(mode)
    
except AttributeError:
    pass
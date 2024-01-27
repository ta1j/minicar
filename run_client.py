import time
import socket
import cv2
import numpy as np
from pynput import keyboard
import threading
import json
from alexnet import learning_model


# ESP32に接続
s = socket.socket() #ソケットの作成
host = "192.168.4.3" #接続先のipアドレス
port = 80 #ポート指定

print("Connecting to {0}".format(host))
s.connect(socket.getaddrinfo(host, port)[0][-1]) #接続確立
print("Successfully connected to {0}".format(host))

WIDTH = 80
HEIGHT = 60
LR = 1e-3
EPOCHS = 8
MODEL_NAME = "autonomous_car-{}-{}-{}-epochs.model".format(LR, "alexnet",EPOCHS)
    
model = learning_model(WIDTH, HEIGHT, LR)
model.load(MODEL_NAME)

def on_release(key):
    if key == keyboard.Key.esc:
        return False

def predict():
    while True:
        predict_direction = [0, 0, 0]
        cap = cv2.VideoCapture("http://192.168.4.1:81/stream")
        ret, frame = cap.read()
        #rotate = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        screen = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        screen = cv2.resize(screen, (80, 60))
        #cv2.imshow("screen", screen)
        prediction = model.predict([screen.reshape(WIDTH, HEIGHT, 1)])[0]
        max_index = np.argmax(prediction)
        predict_direction[max_index] = 1
        print(predict_direction)
        str_ = json.dumps(predict_direction)
        bytes_ = str_.encode("utf-8")
        s.sendall(bytes_)
        cap.release()
        cv2.destroyAllWindows()      
        time.sleep(0.15)
        
try:
    with keyboard.Listener(
        on_release=on_release) as listener:
        th1 = threading.Thread(target=predict)
        th1.setDaemon(True)
        print("Leady...")
        time.sleep(1)
        print("3")
        time.sleep(1)
        print("2")
        time.sleep(1)
        print("1")
        time.sleep(1)
        print("start")
        th1.start()
        listener.join()

except AttributeError:
    pass
        



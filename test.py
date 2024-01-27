import time

basetime = time.time() * 100
timer = 0
while(timer<1000):
    nowtime = time.time() * 100
    timer = int(nowtime - basetime)
    if timer%10==0:
        print(timer)
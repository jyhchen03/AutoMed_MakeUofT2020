import RPi.GPIO as GPIO
import time

'''GPIO declaration'''
servoPIN1 = 15 #cab
servoPIN2 = 17 #cap1
servoPIN3 = 18 #cap2
servoPIN4 = 27 #hop
servoPIN5 = 22 #exit

LED1 = 13 #cab
LED2 = 6 #cap1
LED3 = 5 #cap2
LED4 = 0 #exit

GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN1, GPIO.OUT)
GPIO.setup(servoPIN2, GPIO.OUT)
GPIO.setup(servoPIN3, GPIO.OUT)
GPIO.setup(servoPIN4, GPIO.OUT)
GPIO.setup(servoPIN5, GPIO.OUT)
GPIO.setup(LED1, GPIO.OUT)
GPIO.setup(LED2, GPIO.OUT)
GPIO.setup(LED3, GPIO.OUT)
GPIO.setup(LED4, GPIO.OUT)

s1 = GPIO.PWM(servoPIN1, 50) #15
s2 = GPIO.PWM(servoPIN2, 50) #17
s3 = GPIO.PWM(servoPIN3, 50) #18
s4 = GPIO.PWM(servoPIN4, 50) #27
s5 = GPIO.PWM(servoPIN5, 50) #22

l1 = LED(LED1)
l2 = LED(LED2)
l3 = LED(LED3)
l4 = LED(LED4)

s1.start(0)
s2.start(0)
s3.start(0)
s4.start(0)
s5.start(0)

def capsule(id):
    if id == 1:
        s = s1
    else:
        s = s2
    for i in range(0,25):
        time.sleep(1)
        s.changeDutyCycle(i)
    time.sleep(1)
    for j in range(24,-1):
        time.sleep(1)
        s.ChangeDutyCycle(j)

def hopper_o():
    for i in range(0,25):
        time.sleep(1)
        s4.ChangeDutyCycle(i)
def hopper_c():
    for i in range(24,-1):
        time.sleep(1)
        s4.ChangeDutyCycle(i)
def cabinet_o():
    for i in range(0,15,7):
        time.sleep(1)
        s1.ChangeDutyCycle(i)
def cabinet_c():
    for i in range(14,-1,7):
        time.sleep(1)
        s1.ChangeDutyCycle(i)
def exit_o():
    for i in range(0,7,3):
        time.sleep(1)
        s5.ChangeDutyCycle(i)
def exit_c():
    for i in range(6,-1,3):
        time.sleep(1)
        s5.ChangeDutyCycle(i)
def light_o(id):
    if (id=='0') or (id=='3'):
        l1.on()
    elif (id=='1') or (id=='2'):
        l4.on()
    elif id=='4':
        l2.on()
    else:
        l5.on()
def light_c(id):
    if (id=='0') or (id=='3'):
        l1.off()
    elif (id=='1') or (id=='2'):
        l4.off()
    elif id=='4':
        l2.off()
    else:
        l5.off()

'''mechanical_movements'''
def rotate_cabinet(status):
    if status == 'open':
        cabinet_o()
    elif status == 'close':
        cabinet_c()

def rotate_capsule(id, status):
        if status == 'open':
            capsule(id)

def flip_led(id, status):
    if status == 'on':
        light_o(id)
    else:
        light_o(id)

def rotate_hopper(status):
    if status == 'open':
        hopper_o()
    elif status == 'close':
        hopper_c()

def rotate_exit(status):
    if status == 'open':
        exit_o()
    elif status == 'close':
        exit_c()

def rotate_system(id, status):
    if id == '0':
        rotate_cabinet(status)
    elif (id == '1') or (id == '2'):
        rotate_capsule(id, status)
    else:
        raise ValueError()

def reset():
    rotate_system('0','close')
    rotate_cabinet('close')
    rotate_hopper('close')
    rotate_exit('close')
    flip_led('off')

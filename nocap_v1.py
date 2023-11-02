from djitellopy import tello
import KeyPressModule as kp
import cv2
from time import sleep

kp.init()
me = tello.Tello()
me.connect()
print(me.get_battery())
me.streamon()


def getKeyboardInput():
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 50
    if kp.getKey("a"):
        lr = -speed
    elif kp.getKey("d"):
        lr = speed
    if kp.getKey("w"):
        fb = speed
    elif kp.getKey("s"):
        fb = -speed
    if kp.getKey("UP"):
        ud = speed
    elif kp.getKey("DOWN"):
        ud = -speed
    if kp.getKey("e"):
        yv = -speed
    elif kp.getKey("r"):
        yv = speed
    if kp.getKey("j"):
        me.land()
        sleep(3)
    if kp.getKey("u"):
        me.takeoff()
    return [lr, fb, ud, yv]


while True:
    # 카메라 스트리밍 처리
    img = me.get_frame_read().frame
    img = cv2.resize(img, (600, 400))
    cv2.imshow("Image", img)
    cv2.waitKey(1)

    # 키보드 입력과 드론 제어 처리
    vals = getKeyboardInput()
    me.send_rc_control(vals[0], vals[1], vals[2], vals[3])
    sleep(0.05)

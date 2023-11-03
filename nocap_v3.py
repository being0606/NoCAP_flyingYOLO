from ultralytics import YOLO
import cv2
import math
from time import sleep

from djitellopy import tello
import KeyPressModule as kp


# model
model = YOLO("yolo-Weights/yolov8n.pt")

# object classes
classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
              "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
              "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
              "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
              "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
              "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
              "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
              "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
              "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
              "teddy bear", "hair drier", "toothbrush"
              ]

# "person" 클래스의 인덱스 추출
person_index = classNames.index("person")

def getKeyboardInput(me,kp):
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

input('텔로와 와이파이를 연결하시오 : (입력은 아무 키나 입력 후 엔터)')

kp.init()
me = tello.Tello()
me.connect()
print(me.get_battery())
me.streamon()

while True:
    # 카메라 스트리밍 처리
    img = me.get_frame_read().frame
    img = cv2.resize(img, (600, 400))

    # YOLO 객체 탐지
    results = model(img, stream=True)
    for r in results:
        boxes = r.boxes
        for box in boxes:
            cls = int(box.cls[0])
            # "person" 클래스만 탐지
            if cls == person_index:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
                org = [x1, y1]
                font = cv2.FONT_HERSHEY_SIMPLEX
                # cv2.putText(img, classNames[cls], org, font, 1, (255, 0, 0), 2)
                cv2.putText(img, "NoCAP", org, font, 1, (255, 0, 0), 2)

    cv2.imshow("Image", img)
    cv2.waitKey(1)

    # 키보드 입력과 드론 제어 처리
    vals = getKeyboardInput(me,kp)
    me.send_rc_control(vals[0], vals[1], vals[2], vals[3])
    sleep(0.05)


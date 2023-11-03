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


img_center_x = 600 // 2 # 이미지의 중앙을 계산
detection_mode = False # 디텍팅 모드 상태 변수 (기본값은 False)

while True:
    # 카메라 스트리밍 처리
    img = me.get_frame_read().frame
    img = cv2.resize(img, (600, 400))

    if kp.getKey("o"):
        detection_mode = True  # on
    if kp.getKey("p"):
        detection_mode = False  # off

    if detection_mode:
        # YOLO 객체 탐지 코드
        results = model(img, stream=True)
        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls = int(box.cls[0])
                # "person" 클래스만 탐지
                if cls == person_index:
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                    # 객체의 중앙 계산
                    obj_center_x = (x1 + x2) // 2

                    # 이미지 중앙과 객체 중앙 비교
                    if obj_center_x < img_center_x - 20:  # 임계값은 조정이 필요합니다.
                        # 드론을 왼쪽으로 회전
                        me.rotate_counter_clockwise(10)  # 속도는 조정이 필요합니다.
                    elif obj_center_x > img_center_x + 20:
                        # 드론을 오른쪽으로 회전
                        me.rotate_clockwise(10)

                    # 객체 중앙점을 붉은색으로 그리기
                    cv2.circle(img, (obj_center_x, (y1+y2)//2), 3, (0, 0, 255), -1)

                    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
                    org = [x1, y1]
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(img, "NoCAP", org, font, 1, (255, 0, 0), 2)
    else:
        # 디텍팅 모드가 꺼져있을 때 수행되는 코드 (여기서는 아무 것도 수행하지 않음)
        # 디텍팅 모드가 꺼져있을 때 수행되는 코드 (여기서는 아무 것도 수행하지 않음)
        pass
    
    cv2.imshow("Image", img)
    cv2.waitKey(1)

    # 키보드 입력과 드론 제어 처리
    vals = getKeyboardInput(me, kp)
    me.send_rc_control(vals[0], vals[1], vals[2], vals[3])
    sleep(0.05)
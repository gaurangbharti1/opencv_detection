#Code without ultrasonic sensors

import sys
import time
import RPi.GPIO as GPIO
from pygame import mixer
from pyzbar import pyzbar
import argparse
import cv2

mode=GPIO.getmode()

WHEEL_RADIUS = 5.2 #cm
lower_body_cascade = cv2.CascadeClassifier("haarcascade_lower_body.xml")

M1F= 13 #Front left motor
M1B= 21
M2F= 18 #Front right motor
M2B= 8
M3F= 19 #Back left motor
M3B= 22
M4F= 12 #Back right motor
M4B= 15

UVL1 = 2
UVL2 = 3

fl = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(M1F, GPIO.OUT)
GPIO.setup(M1B, GPIO.OUT)
GPIO.setup(M2F, GPIO.OUT)
GPIO.setup(M2B, GPIO.OUT)
GPIO.setup(M3F, GPIO.OUT)
GPIO.setup(M3B, GPIO.OUT)
GPIO.setup(M4F, GPIO.OUT)
GPIO.setup(M4B, GPIO.OUT)
GPIO.setup(UVL1, GPIO.OUT)
GPIO.setup(UVL2, GPIO.OUT)
GPIO.setup(fl, GPIO.OUT)

time.sleep(1) #GPIO Initalization
'''
#Argument for CSV? Change to fixed variable
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image",
  help="path to input image")
args = vars(ap.parse_args())

#csv = open(args["output"], "w")
#found = set()
'''
AUDIO_DIR = 'lang_audio/'
LANG = 'English'
mixer.init()

def continue_audio():
  audio_file = AUDIO_DIR + 'uv_progress.mp3'
  mixer.music.load(audio_file)
  mixer.music.play(-1)

def left(x):
  GPIO.output(M1B, GPIO.HIGH)
  GPIO.output(M2F, GPIO.HIGH)
  GPIO.output(M3B, GPIO.HIGH)
  GPIO.output(M4F, GPIO.HIGH)
  print("Turning left")
  time.sleep(x)
  GPIO.output(M1B, GPIO.LOW)
  GPIO.output(M2F, GPIO.LOW)
  GPIO.output(M3B, GPIO.LOW)
  GPIO.output(M4F, GPIO.LOW)

def right(x):
  GPIO.output(M1B, GPIO.HIGH)
  GPIO.output(M2F, GPIO.HIGH)
  GPIO.output(M3B, GPIO.HIGH)
  GPIO.output(M4F, GPIO.HIGH)
  print("Turning right")
  time.sleep(x)
  GPIO.output(M1B, GPIO.LOW)
  GPIO.output(M2F, GPIO.LOW)
  GPIO.output(M3B, GPIO.LOW)
  GPIO.output(M4F, GPIO.LOW)

def straight(x, center_flag=0):
  left_distance = usdistance(sl)
  right_distance = usdistance(sr)
  front_distance = usdistance(sf)
  if front_distance < 30:
    GPIO.output(M1F, GPIO.LOW)
    GPIO.output(M2F, GPIO.LOW)
    GPIO.output(M3F, GPIO.LOW)
    GPIO.output(M4F, GPIO.LOW)
    audio_file = AUDIO_DIR + 'obstacle.mp3'
    mixer.music.load(audio_file)
    mixer.music.play()
    reverse(1)
    left(1)
    continue_audio()

  '''if x>2 & center_flag == 0: #Get robot closer to center
    if abs(left_distance - right_distance) > 10:
      if left_distance > right_distance:
        left(2)
        straight(2)
        right(2)
      else:
        right(2)
        straight(2)
        left(2)
      x += -1.5'''

  GPIO.output(M1F, GPIO.HIGH)
  GPIO.output(M2F, GPIO.HIGH)
  GPIO.output(M3F, GPIO.HIGH)
  GPIO.output(M4F, GPIO.HIGH)
  print("Moving straight")
  time.sleep(x)
  GPIO.output(M1F, GPIO.LOW)
  GPIO.output(M2F, GPIO.LOW)
  GPIO.output(M3F, GPIO.LOW)
  GPIO.output(M4F, GPIO.LOW)

def reverse(x):
  GPIO.output(M1B, GPIO.HIGH)
  GPIO.output(M2B, GPIO.HIGH)
  GPIO.output(M3B, GPIO.HIGH)
  GPIO.output(M4B, GPIO.HIGH)
  print("Moving backwards")
  time.sleep(x)
  GPIO.output(M1B, GPIO.LOW)
  GPIO.output(M2B, GPIO.LOW)
  GPIO.output(M3B, GPIO.LOW)
  GPIO.output(M4B, GPIO.LOW)

def read_qr(frame):
  barcodes = pyzbar.decode(frame)
  result = [0,0,0]
  for barcode in barcodes:
    # extract the bounding box location of the barcode and draw
    # the bounding box surrounding the barcode on the image
    (x, y, w, h) = barcode.rect
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
    # the barcode data is a bytes object so if we want to draw it
    # on our output image we need to convert it to a string first
    barcodeData = barcode.data.decode("utf-8")
    barcodeType = barcode.type
    # draw the barcode data and barcode type on the image
    text = "{}".format(barcodeData)
    cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    #Write the timestamp + barcode to disk and update the set
    #csv.write("{},{}\n".format(datetime.datetime.now(),barcodeData))
    #csv.flush()
    #found.add(barcodeData)
    if w>100:
      if w+h > result[0]+result[1]:
        result = [w,h]
        result.append(text.split())
  cv2.imwrite("latestframe.jpg",frame)
  return result

def obstacle_check():

  cap = cv2.VideoCapture(0)

  ret, img = cap.read()
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  bodies = lower_body_cascade.detectMultiScale(gray, 1.3, 5)

  for (x,y,w,h) in bodies:
      cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
      roi_gray = gray[y:y+h, x:x+w]
      roi_color = img[y:y+h, x:x+w]

def main():
  for i in range(100):
	  GPIO.output(fl, 1)
	  cap = cv2.VideoCapture(0)
	  time.sleep(0.3)
	  ret, frame = cap.read()
	  cv2.imshow('feed', frame)
	  GPIO.output(fl, 0)
	  result = read_qr(frame)
	  cap.release()
	  print(result)
	  if result[2] == "":
	    straight(1)
	  elif result[2] == "left":
	    left(5)
	  elif result[2] == "right":
	    right(5)
	  elif result[2] == "straight":
	    straight(result[3])
	  elif result[2] == "reverse":
	    reverse(result[3])
	  i = i+1

main()
GPIO.cleanup()
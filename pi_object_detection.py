# USAGE
# python pi_object_detection.py --prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
from multiprocessing import Process
from multiprocessing import Queue
from multiprocessing import Pool
import numpy as np
import argparse
import imutils
import time
import cv2
import time
from datetime import datetime
import json
import requests
import urllib3
import os



def classify_frame(net, inputQueue, outputQueue):
	# keep looping
	while True:
		# check to see if there is a frame in our input queue
		if not inputQueue.empty():
			# grab the frame from the input queue, resize it, and
			# construct a blob from it
			frame = inputQueue.get()
			frame = cv2.resize(frame, (300, 300))
			blob = cv2.dnn.blobFromImage(frame, 0.007843,
				(300, 300), 127.5)

			# set the blob as input to our deep learning object
			# detector and obtain the detections
			net.setInput(blob)
			detections = net.forward()

			# write the detections to the output queue
			outputQueue.put(detections)

def create_info(object, addr, accuracy):
	#:dic = { 'Time': normal_time, 'Object':object}
	timestamp = datetime.now()
	#ds = timestamp.strftime("%d-%m-%Y")
	ds = timestamp.strftime("%A %d-%m-%Y")
	ts = timestamp.strftime("%I:%M:%S%p")
	dic = {'object_name': object, 'time': ts,'date': ds,'accuracy': accuracy}
	push_json = json.dumps(dic)
	js = json.loads(push_json)
	headers = "Content-Type: application/json"
	try:
		r = requests.post(addr, json=js)
	except:
		return -1

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt",default= 'MobileNetSSD_deploy.prototxt.txt',
	help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model",default='MobileNetSSD_deploy.caffemodel', 
	help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
	help="minimum probability to filter weak detections")
ap.add_argument("-src","--source", type = int, default = 0,help='Device index of the camera.')
ap.add_argument("-ho","--host",default = "127.0.0.1" , help = 'IP Server' )
ap.add_argument("-po","--port",default = 9999, help = 'Port Server')
ap.add_argument("-o","--object",help = "Name Object want to be detected")
ap.add_argument("-wh","--width",type = int, default = 640, help = 'Set Width ')
ap.add_argument("-ht","--height",type = int,default= 480, help = 'Set Height' )
args = vars(ap.parse_args())

# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])
host = args["host"]
port = args["port"]
addr = 'http://' + str(host) + ':' +  str(port)
if not os.path.exists('save_image'):
    os.mkdir('save_image')
if not os.path.exists('save_video'):
	os.mkdir('save_video')
# initialize the input queue (frames), output queue (detections),
# and the list of actual detections returned by the child process
inputQueue = Queue(maxsize=1)
outputQueue = Queue(maxsize=1)
detections = None

# construct a child process *indepedent* from our main process of
# execution
print("[INFO] starting process...")
p = Process(target=classify_frame, args=(net, inputQueue,
	outputQueue,))
p.daemon = True
p.start()

# initialize the video stream, allow the cammera sensor to warmup,
# and initialize the FPS counter
print("[INFO] starting video stream...")
vs = cv2.VideoCapture(args["source"]) 

width_x = args["width"]
height_y = args["height"]
vs.set(3, width_x)
vs.set(4, height_y)

time.sleep(2.0)
fps = FPS().start()
flag = time.time()
start = 0
frame_rate_calc = 1
freq = cv2.getTickFrequency()
font = cv2.FONT_HERSHEY_SIMPLEX

# fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Be sure to use the lower case
# out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (width_x, heig))
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('webcamOut.avi',fourcc,30.0,(640,480))
while True:
	t1 = cv2.getTickCount()
	timestamp = datetime.now()
	ds = timestamp.strftime("%d-%m-%Y")
	ts = timestamp.strftime("%I:%M:%S%p")
	
	# grab the frame from the threaded video stream, resize it, and
	# grab its imensions
	#frame = vs.read()
	(grabbed, frame) = vs.read()
	if not grabbed:
		break
	
	frame = imutils.resize(frame, width=width_x, height=height_y )
	(fH, fW) = frame.shape[:2]

	# if the input queue *is* empty, give the current frame to
	# classify
	if inputQueue.empty():
		inputQueue.put(frame)

	# if the output queue *is not* empty, grab the detections
	if not outputQueue.empty():
		detections = outputQueue.get()

	# check to see if our detectios are not None (and if so, we'll
	# draw the detections on the frame)
	if detections is not None:
		# loop over the detections
		arr = []
		for i in np.arange(0, detections.shape[2]):
			# extract the confidence (i.e., probability) associated
			# with the prediction
			confidence = detections[0, 0, i, 2]

			# filter out weak detections by ensuring the `confidence`
			# is greater than the minimum confidence
			if confidence < args["confidence"]:
				continue

			# otherwise, extract the index of the class label from
			# the `detections`, then compute the (x, y)-coordinates
			# of the bounding box for the object
			idx = int(detections[0, 0, i, 1])
			dims = np.array([fW, fH, fW, fH])
			box = detections[0, 0, i, 3:7] * dims
			(startX, startY, endX, endY) = box.astype("int")

			# draw the prediction on the frame
			label = "{}: {:.2f}%".format(CLASSES[idx],
				confidence * 100)
			no = str(CLASSES[idx]) + str(i)
			cv2.rectangle(frame, (startX, startY), (endX, endY),
				COLORS[idx], 2)
			y = startY - 15 if startY - 15 > 15 else startY + 15
			
			cv2.putText(frame,label,(startX, y),font, 0.5, COLORS[idx], 2)
			

			object_name = args["object"]
			if (args["object"] == None):
				if((time.time() - flag > 2) ):
					image_name = 'save_image//' + str(ts) + '_' + str(ds) + '_' + str(CLASSES[idx]) +'.jpg'
					cv2.imwrite(image_name, frame)
					flag = time.time()
					start = 1
					confidence = "{0:.4f}".format(confidence*100)
					pol = Process(target=create_info, args=(str(CLASSES[idx]), addr, str(confidence)))
					pol.start()
					pol.join()
					arr.append(no)
			else:
				if(str(CLASSES[idx])== object_name and (time.time() - flag > 2) ):
					image_name = 'save_image//' + str(ts) + '_' + str(ds) + '_' + str(CLASSES[idx]) +'.jpg'
					cv2.imwrite(image_name, frame)
					out.write(frame)
					# name = "save_video//" + time.strftime("%d-%m-%Y_%X")+".avi"
					# out = cv2.VideoWriter(name, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
					flag = time.time()
					start = 1
					
					confidence = "{0:.4f}".format(confidence*100)
					pol = Process(target=create_info, args=(str(CLASSES[idx]), addr, str(confidence)))
					pol.start()
					pol.join()
					arr.append(no)
	
	tss = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
	cv2.putText(frame,"FPS : {0:.2f}".format(frame_rate_calc), (10, 30),font, 1, (255, 255, 0), 2,cv2.LINE_AA)
	cv2.putText(frame,tss, (300, 30),font, 0.5, (0, 0, 255), 2)		
	cv2.imshow("Frame", frame)
	t2 = cv2.getTickCount()
	time1 = (t2-t1)/freq
	frame_rate_calc = 1/time1
	key = cv2.waitKey(1) & 0xFF
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

	# update the FPS counter
	fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
vs.release()
cv2.destroyAllWindows()
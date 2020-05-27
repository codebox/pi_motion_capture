import cv2, signal, os, glob
from pi_motion_capture import MotionCapture
from web_server import WebServer

config = {
    'captureDevice': 0,
    'minContourArea': 5000,
    'backgroundSubtractionAlgorithm': cv2.createBackgroundSubtractorMOG2(),
    'frameWidth': 1640,
    'frameAspectRatio': 4/3,
    'cropX1Fraction': 0.4,
    'cropX2Fraction': 0.6,
    'cropY1Fraction': 0.4,
    'cropY2Fraction': 0.6,
    'boxColour': {
        'r': 255,
        'g': 0,
        'b': 0
    },
    'boxThickness': 2,
    'imgFileNamePrefix': 'cam',
    'httpPort': 8000,
    'webDir': 'web',
    'imageDir': 'images'
}

def signal_handler(sig, frame):
    motion_capture.stop()
    web_server.stop()

signal.signal(signal.SIGINT, signal_handler)

os.chdir(config['webDir'])
[os.remove(f) for f in glob.glob(os.path.join(config['imageDir'], ".jpg"))]

motion_capture = MotionCapture(config)
motion_capture.start()

web_server = WebServer(config)
web_server.start()
from flask import Flask, render_template, Response, jsonify
import threading
import cv2
from serial import Serial
import logging


# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful for multiple browsers/tabs
# are viewing tthe stream)
outputFrame = None
lock = threading.Lock()
to_json = {'action': '', 'crossings': 0}
history = []

# initialize a flask object
app = Flask(__name__)
logging.getLogger('werkzeug').setLevel(logging.ERROR)

# initialize the video stream
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1000)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
ser = Serial('COM15', 9600)


def detect_motion():
    def findBigContour(mask, limit=1000):
        contours = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]
        if contours:
            contours = sorted(contours, key=cv2.contourArea, reverse=True)
            if cv2.contourArea(contours[0]) > limit:
                return contours[0]
            else:
                return None
        else:
            return None
    
    # grab global references to the video stream, output frame, and
    # lock variables
    global cap, outputFrame, lock, to_json, history

    crossings = 0

    # loop over frames from the video stream
    while True:
        _, frame = cap.read()
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        frame = cv2.resize(frame, (200, 250))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hsv = cv2.blur(hsv, (5, 5))

        # green
        mask = cv2.inRange(hsv, (79, 118, 56), (98, 185, 115))
        cnt = findBigContour(mask)
        if cnt is not None:
            cv2.drawContours(frame, cnt, -1, (0, 255, 0), 3)
            green = True
        else:
            green = False

        # red
        mask = cv2.inRange(hsv, (144, 72, 109), (255, 255, 231))
        cnt = findBigContour(mask)
        if cnt is not None:
            cv2.drawContours(frame, cnt, -1, (0, 0, 255), 3)
            red = True
        else:
            red = False

        if green and red:
            action = 'ERR'
        elif green:
            action = 'Green'
        elif red:
            action = 'Red'
        else:
            action = 'No'

        line = b''
        while ser.inWaiting():
            line = ser.readline()
        if line:
            crossings += int(line.split(b'\r\n')[0].decode())

        to_json['action'] = action
        to_json['crossings'] = crossings

        if action == 'Red' and crossings not in history:
            history.append(crossings)


        # acquire the lock, set the output frame, and release the
        # lock
        with lock:
            outputFrame = frame.copy()


def generate():
    # grab global references to the output frame and lock variables
    global outputFrame, lock

    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrame is None:
                continue

            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

            # ensure the frame was successfully encoded
            if not flag:
                continue

        # yield the output frame in the byte format
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               bytearray(encodedImage) + b'\r\n')


@app.route("/result")
def result():
    # return the rendered template
    return jsonify(history)


@app.route("/info")
def info():
    # return the rendered template
    return jsonify(to_json)


@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/")
def index():
    # return the rendered template
    return render_template("index.html")


# check to see if this is the main thread of execution
if __name__ == '__main__':
    t = threading.Thread(target=detect_motion)
    t.daemon = True
    t.start()

    # start the flask app
    app.run(host='0.0.0.0', port=8000, threaded=True, use_reloader=False)

    cap.release()

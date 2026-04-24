import camera
import cv2
from flask import Flask, Response

app = Flask(__name__)
camera.start()

def generate():
    
    while True:
        frame = camera.get_latest_frame()
        if frame is not None:
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video')
def video():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
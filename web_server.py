import http.server
import socketserver, socket
import os
import json
import threading
from functools import partial
from pi_motion_capture import MotionCapture

class WebServer:
    def __init__(self, config, queue):
        self.config = config
        self.queue = queue
        self.running = False
        self.server = None

    def start(self):
        if not self.running:
            self.running = True
            self.worker_thread = threading.Thread(target=self._run)
            self.worker_thread.start()

    def _run(self):
        handler = partial(PiMotionCaptureRequestHandler, self.config, self.queue)
        self.server = TCPServerThatTerminatesProperly(("", self.config['httpPort']), handler)
        print("Listening on port", self.config['httpPort'])
        self.server.serve_forever()

    def stop(self):
        self.running = False
        self.server.shutdown()
        self.server.server_close()
        print('Stopped listening')


class PiMotionCaptureRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, config, queue, *args, **kwargs):
        self.config = config
        self.queue = queue
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/images.json':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            json_string = json.dumps(os.listdir(self.config['imageDir']))
            self.wfile.write(json_string.encode(encoding='utf_8'))

        elif self.path == '/snapshot':
            self.queue.put(MotionCapture.TASK_SNAPSHOT)
            self.send_response(200)
            self.end_headers()

        else:
            if self.path == '/':
                self.path = 'index.html'

            return http.server.SimpleHTTPRequestHandler.do_GET(self)

class TCPServerThatTerminatesProperly(socketserver.TCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)


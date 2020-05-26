import http.server
import socketserver, socket
import os
import json
import threading


class WebServer:
    def __init__(self, config):
        self.config = config
        self.running = False
        self.server = None

    def start(self):
        if not self.running:
            self.running = True
            self.worker_thread = threading.Thread(target=self._run)
            self.worker_thread.start()

    def _run(self):
        PiMotionCaptureRequestHandler.config = self.config
        self.server = TCPServerThatTerminatesProperly(("", self.config['httpPort']), PiMotionCaptureRequestHandler)
        print("Listening on port", self.config['httpPort'])
        self.server.serve_forever()

    def stop(self):
        self.running = False
        self.server.shutdown()
        self.server.server_close()
        print('Stopped listening')


class PiMotionCaptureRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/images.json':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            json_string = json.dumps(os.listdir(PiMotionCaptureRequestHandler.config['imageDir']))
            self.wfile.write(json_string.encode(encoding='utf_8'))

        else:
            if self.path == '/':
                self.path = 'index.html'

            return http.server.SimpleHTTPRequestHandler.do_GET(self)

class TCPServerThatTerminatesProperly(socketserver.TCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)


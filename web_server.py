import http.server
import socketserver, socket
import os
import json
import signal, sys

class PiMotionCaptureRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/images.json':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            json_string = json.dumps(os.listdir('./images'))
            self.wfile.write(json_string.encode(encoding='utf_8'))

        else:
            if self.path == '/':
                self.path = 'index.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

class MyTCPServer(socketserver.TCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

def signal_handler(sig, frame):
    server.server_close()
    print('You pressed Ctrl+C!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

PORT = 8000
os.chdir('web')
server = MyTCPServer(("", PORT), PiMotionCaptureRequestHandler)
print("serving at port", PORT)
server.serve_forever()

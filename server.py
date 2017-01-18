import socketserver
from vision import getAngle

class StuffHandler(socketserver.BaseRequestHandler):
          
    def handle(self):
        res = getAngle()
        self.request.sendall(bytes('HTTP/1.1 200 OK\r\n\r\n' + res + '\n', 'UTF-8'))
    
socketserver.TCPServer(('localhost', 8080), StuffHandler).serve_forever()


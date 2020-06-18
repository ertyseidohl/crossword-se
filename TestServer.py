from http.server import HTTPServer, BaseHTTPRequestHandler

from threading import Thread

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def _set_headers(self, status):
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_GET(self):
        """Respond to GET requests"""
        print('GET ' + self.path)
        if self.path == '/words?word=...&page=0':
            self._set_headers(200)
            self.wfile.write(b'AAA BBB CCC DDD EEE FFF GGG HHH III JJJ')
        elif self.path == '/words?word=...&page=1':
            self._set_headers(200)
            self.wfile.write(b'LLL MMM NNN OOO PPP QQQ RRR SSS TTT UUU')
        elif self.path == '/words?word=H..&page=0':
            self._set_headers(200)
            self.wfile.write(b'HMM HNN')
        elif self.path == '/words?word=H..&page=1':
            self._set_headers(200)
            self.wfile.write(b'')
        elif self.path == '/solve?crossword=...%0A...%0A...':
            self._set_headers(200)
            self.wfile.write(b'ERA\nREL\nEDE')
        else:
            self._set_headers(404)
            self.wfile.write(b'404 Not Found')


class TestServer:
    def __init__(self):
        self._running = True
        self.httpd = HTTPServer(('localhost', 8079), SimpleHTTPRequestHandler)
        self.thread = Thread(target=self.httpd.serve_forever)
        self.thread.daemon = True

    def run(self):
        """Start the server thread."""
        self.thread.start()

    def terminate(self):
        """Shutdown the server thread."""
        self.httpd.shutdown()

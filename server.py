from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import ast
import json

hostName = "localhost"
serverPort = 8081

class MyServer(SimpleHTTPRequestHandler):
    def do_POST(self):
        self.data_string = self.rfile.read(int(self.headers['Content-Length'])).decode()

        # self.protocol_version = 'HTTP/1.1'
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        text = str(["aa", "aaa"]).encode()
        self.send_header("Content-Length", len(text))
        self.end_headers()
        self.wfile.write(text)
        return

if __name__ == "__main__":        
    webServer = ThreadingHTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")


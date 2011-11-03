'''
Created on 7. okt. 2011

@author: Eier
'''
import cgi
import sys
import time

from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from os import curdir, path

class HttpRequestHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        try:
            print 'Request: ' + self.path

            if self.path == '/':
                fpath = path.abspath(curdir + '/../gui/simulation.html')
            else:
                fpath = path.abspath(curdir + '/../gui' + self.path)
            
            print 'Path: '+fpath;
            
            f = open(fpath,'rb')
            
            if fpath.endswith('.css'):
                mime = 'text/css'
            elif fpath.endswith('.html'):
                mime = 'text/html'
            elif fpath.endswith('.gif'):
                mime = 'image/gif'  
            elif fpath.endswith('.png'):
                mime = 'image/png'
            elif fpath.endswith('.jpg'):
                mime = 'image/jpeg'
            elif fpath.endswith('.js'):
                mime = 'text/javascript'
            else:
                mime = 'text/plain'
                
            self.send_response(200)
            self.send_header('Content-type',mime)
            self.end_headers()

            self.wfile.write(f.read())
            f.close()            
            return
        except IOError:
            self.send_error(404,'File Not Found: %s' % fpath)
     
    def do_POST(self):
        try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                postvars = cgi.parse_multipart(self.rfile, pdict)
            elif ctype == 'application/x-www-form-urlencoded':
                length = int(self.headers.getheader('content-length'))
                postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
            else:
                postvars = {}
        except IOError:
            self.send_error(404,'File not found!')
            
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()
        self.wfile.write('ok!')
        return
    
if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', 8000), HttpRequestHandler)
    server.serve_forever()
    print "Server started!"
    pass
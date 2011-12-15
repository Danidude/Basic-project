'''
Created on 7. okt. 2011

@author: Eier
'''
import cgi
import base64;
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from os import curdir, path
from Analyzer import GPR_Controller
import time


class GridCell():

    def __init__(self,x,y,t,v,S2):
        self.x = x
        self.y = y
        self.t = t
        self.v = v #value
        self.S2 = S2
        

class Grid():
    sizeX = 0
    sizeY = 0
    
    def __init__(self,sizeX,sizeY,values1d):
        self.sizeX = sizeX
        self.sizeY = sizeY
        
        v = 0
        self.cells = []
        for x in range(sizeX):
            self.cells.append([])
            for y in range(sizeY):
#                print x,sizeX,y,sizeY,v,len(values1d)
                self.cells[x].append(GridCell(x, y, None, ord(values1d[v]),10000.0));
                v += 1
class HttpRequestHandlerWrapper:
    
    def __init__(self):
        HttpRequestHandlerWrapper.fire_cells = None
        HttpRequestHandlerWrapper.time_fire = []
        server = HTTPServer(('127.0.0.1', 8000), self.HttpRequestHandler)
        server.serve_forever()
        print "Server started!"

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
        
        def create_unit_vector_based_on_angle(self,radian_angle):
            import math
            x = math.cos(radian_angle)
            y = math.cos(radian_angle)
            return [x,y]
        
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
            cells = []
            angle = 0.0
            for key,value in postvars.items():
                if key == 'sizeX':
                    sizeX = int(value[0])
                elif key == 'sizeY':
                    sizeY = int(value[0])
                elif key=='cells':
                    for char in base64.b64decode(value[0]):
                        cells.append(char)
                elif key =="windDirection":
                    angle = float(value[0])
            
            grid = Grid(sizeX,sizeY,cells)
            unit_wind_vector = self.create_unit_vector_based_on_angle(angle)
            t = time.time()
            gpr_controller = GPR_Controller(grid, HttpRequestHandlerWrapper.time_fire, HttpRequestHandlerWrapper.fire_cells, unit_wind_vector)
            #grid = gpr_controller.grid
            
            large_string = gpr_controller.large_string
            HttpRequestHandlerWrapper.fire_cells = gpr_controller.fire_cells
            
            
            self.wfile.write(base64.b64encode(large_string))
    
            
            t2 = time.time() -t
            print t2
            
            return
    
if __name__ == '__main__':
    HttpRequestHandlerWrapper()
    pass
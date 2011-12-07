'''
Created on Dec 6, 2011

@author: enok
'''
import wx

class MainWindow(wx.Frame):
    def __init__(self, parent):
        app = wx.App(False)
        wx.Frame.__init__(self, parent, size=[500,500], pos=[0,0])

        bottom_panel = SensorPanel(self)
        
#        self.Bind(wx.EVT_LEFT_DCLICK, self.changed, bottom_panel)
        self.Bind(wx.EVT_KEY_DOWN, self.changed, self)
        
        
        self.Show()
        app.MainLoop()
    
    def changed(self, event):
        print "clicked"
        


class SensorPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent) #@UndefinedVariable
        self.quote = wx.StaticText(self, label="Your quote :", pos=(20, 30))
#        button_panel = ButtonPanel(parent)
#        self.SetBackgroundColour("blue")
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        dc = wx.ClientDC(self)
        dc.DrawRectangleRect(wx.Rect(10,10))
    
    def OnPaint(self, event=None):
        dc = wx.PaintDC(self)
        dc.Clear()
        dc.SetPen(wx.Pen(wx.BLUE, 1))
        dc.SetBrush(wx.Brush(wx.BLUE))
#        dc.DrawLine(50, 50, 50, 100)
        dc.DrawRectangle(50,50,50,50)
        
        dc.DrawRectangle(200,50,50,50)
        
    
class ButtonPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.quote = wx.StaticText(self, label="buttofdan panel", pos=(80, 80))
        
        
        
        
        
MainWindow(None)

import math
import wx

class Handle:
    def __init__(self, name, x, y):
        self.name = name
        self.x, self.y = x, y
        self.rect = wx.Rect(x-5, y-5, 10, 10)
        
        self.canx = True
        self.minx = -1000
        self.maxx =  1000
        self.cany = True
        self.miny = -1000
        self.maxy =  1000
    
    def setConstraints(self, canx = True, minx = -1000, maxx =  1000, cany = True, miny = -1000, maxy =  1000):
        self.canx = canx
        self.minx = minx
        self.maxx = maxx
        self.cany = cany
        self.miny = miny
        self.maxy = maxy
    
    def canMoveX(self, delta = 0):
        if self.canx and self.x+delta >= self.minx and self.x+delta <= self.maxx:
            return True
        else:
            return False
            
    def canMoveY(self, delta = 0):
        if self.cany and self.y+delta >= self.miny and self.y+delta <= self.maxy:
            return True
        else:
            return False
    
    def moveX(self, delta = 0):
        if self.canMoveX(delta):
            self.x += delta
        self.rect = wx.Rect(self.x-5, self.y-5, 10, 10)
            
    def moveY(self, delta = 0):
        if self.canMoveY(delta):
            self.y += delta
        self.rect = wx.Rect(self.x-5, self.y-5, 10, 10)
            
    def move(self, dx = 0, dy = 0):
        self.moveX(dx)
        self.moveY(dy)
        
    def contains(self, x, y):
        return self.rect.Contains(x,y)
        
    def draw(self, gc):
        gc.DrawRoundedRectangle(self.x-5, self.y-5, 10, 10, 3)
        
class Shape:
    def __init__(self, name):
        self.name = name
        self.handles = {}
        
    def addHandle(self, handle):
        self.handles[handle.name] = handle
        
    def draw(self):
        pass
    
    def getHandles(self):
        return self.handles.values()
        
class Head(Shape):
    def __init__(self, name):
        super().__init__(name)
        
        self.head_handle = Handle('Head Width', 50, 0)
        self.head_handle.setConstraints(cany=False, minx=10)
        self.addHandle(self.head_handle)
        
        self.jaw_handle = Handle('Jaw', 40, 70)
        self.addHandle(self.jaw_handle)
        
        self.chin_width_handle = Handle('Chin Width', 20, 90)
        self.addHandle(self.chin_width_handle)
        
        self.chin_handle = Handle('Chin', 0, 95)
        self.addHandle(self.chin_handle)
        
        self.eyes_handle = Handle('Eyes', 25, 25)
        self.addHandle(self.eyes_handle)
        
        self.nose_handle = Handle('Nose', 0, 55)
        self.nose_handle.setConstraints(canx=False)
        self.addHandle(self.nose_handle)
        
        self.mouth_handle = Handle('Mouth', 0, 68)
        self.mouth_handle.setConstraints(canx=False)
        self.addHandle(self.mouth_handle)
        
    def draw(self, gc):
        # head shape
        path = gc.CreatePath()
        path.AddArc(0, 0, self.head_handle.x, math.radians(180), math.radians(0), True)
        gc.StrokePath(path)
        
        # jaw lines
        gc.StrokeLine(-self.head_handle.x, self.head_handle.y, -self.jaw_handle.x, self.jaw_handle.y)
        gc.StrokeLine(self.head_handle.x, self.head_handle.y, self.jaw_handle.x, self.jaw_handle.y)
        
        # draw chin
        gc.StrokeLine(-self.jaw_handle.x, self.jaw_handle.y, -self.chin_width_handle.x, self.chin_width_handle.y)
        gc.StrokeLine(-self.chin_width_handle.x, self.chin_width_handle.y, 0, self.chin_handle.y)
        gc.StrokeLine(self.jaw_handle.x, self.jaw_handle.y, self.chin_width_handle.x, self.chin_width_handle.y)
        gc.StrokeLine(self.chin_width_handle.x, self.chin_width_handle.y, 0, self.chin_handle.y)
        
        # eyes
        gc.DrawEllipse(-self.eyes_handle.x-13, self.eyes_handle.y-4, 25, 8)
        path = gc.CreatePath()
        path.AddArc(self.eyes_handle.x, self.eyes_handle.y-2, 6, math.radians(180), math.radians(0), False)
        gc.StrokePath(path)
        
        gc.DrawEllipse(self.eyes_handle.x-13, self.eyes_handle.y-4, 25, 8)
        path = gc.CreatePath()
        path.AddArc(-self.eyes_handle.x, self.eyes_handle.y-2, 6, math.radians(180), math.radians(0), False)
        gc.StrokePath(path)
        
        # eyebrows
        path = gc.CreatePath()
        path.MoveToPoint(-self.eyes_handle.x-18, self.eyes_handle.y-2)
        path.AddLineToPoint(-self.eyes_handle.x-11, self.eyes_handle.y-10)
        path.AddLineToPoint(-self.eyes_handle.x+13, self.eyes_handle.y-7)
        path.AddLineToPoint(-self.eyes_handle.x+11, self.eyes_handle.y-11)
        path.AddLineToPoint(-self.eyes_handle.x-11, self.eyes_handle.y-14)
        path.CloseSubpath()
        gc.StrokePath(path)
        
        path = gc.CreatePath()
        path.MoveToPoint(self.eyes_handle.x+18, self.eyes_handle.y-2)
        path.AddLineToPoint(self.eyes_handle.x+11, self.eyes_handle.y-10)
        path.AddLineToPoint(self.eyes_handle.x-13, self.eyes_handle.y-7)
        path.AddLineToPoint(self.eyes_handle.x-11, self.eyes_handle.y-11)
        path.AddLineToPoint(self.eyes_handle.x+11, self.eyes_handle.y-14)
        path.CloseSubpath()
        gc.StrokePath(path)
        
        # nose
        path = gc.CreatePath()
        path.MoveToPoint(0, self.nose_handle.y)
        path.AddLineToPoint(4, self.nose_handle.y)
        path.AddLineToPoint(10, self.nose_handle.y-5)
        path.AddLineToPoint(8, self.nose_handle.y-15)
        path.AddLineToPoint(6, self.nose_handle.y-15)
        gc.DrawEllipse(2, self.nose_handle.y-4, 5, 2)
        gc.StrokePath(path)
        
        path = gc.CreatePath()
        path.MoveToPoint(0, self.nose_handle.y)
        path.AddLineToPoint(-4, self.nose_handle.y)
        path.AddLineToPoint(-10, self.nose_handle.y-5)
        path.AddLineToPoint(-8, self.nose_handle.y-15)
        path.AddLineToPoint(-6, self.nose_handle.y-15)
        gc.DrawEllipse(-7, self.nose_handle.y-4, 5, 2)
        gc.StrokePath(path)
        
        # ears
        path = gc.CreatePath()
        path.MoveToPoint(self.head_handle.x, self.eyes_handle.y)
        path.AddLineToPoint(self.head_handle.x+4, self.eyes_handle.y-4)
        path.AddLineToPoint(self.head_handle.x+8, self.eyes_handle.y-4)
        path.AddLineToPoint(self.head_handle.x+8, self.eyes_handle.y+6)
        path.AddLineToPoint(self.head_handle.x+4, self.eyes_handle.y+20)
        path.AddLineToPoint(self.head_handle.x-4, self.nose_handle.y)
        gc.StrokePath(path)
        
        path = gc.CreatePath()
        path.MoveToPoint(-self.head_handle.x, self.eyes_handle.y)
        path.AddLineToPoint(-self.head_handle.x-4, self.eyes_handle.y-4)
        path.AddLineToPoint(-self.head_handle.x-8, self.eyes_handle.y-4)
        path.AddLineToPoint(-self.head_handle.x-8, self.eyes_handle.y+6)
        path.AddLineToPoint(-self.head_handle.x-4, self.eyes_handle.y+20)
        path.AddLineToPoint(-self.head_handle.x+4, self.nose_handle.y)
        gc.StrokePath(path)
        
        # mouth
        path = gc.CreatePath()
        path.MoveToPoint(0, self.mouth_handle.y)
        path.AddLineToPoint(5, self.mouth_handle.y+2)
        path.AddLineToPoint(self.eyes_handle.x-6, self.mouth_handle.y)
        gc.DrawEllipse(self.eyes_handle.x-6, self.mouth_handle.y-2, 4, 2)
        gc.StrokePath(path)
        
        path = gc.CreatePath()
        path.MoveToPoint(0, self.mouth_handle.y)
        path.AddLineToPoint(-5, self.mouth_handle.y+2)
        path.AddLineToPoint(-self.eyes_handle.x+6, self.mouth_handle.y)
        gc.DrawEllipse(-self.eyes_handle.x+2, self.mouth_handle.y-2, 4, 2)
        gc.StrokePath(path)
        
        path = gc.CreatePath()
        path.AddArc(0, self.mouth_handle.y-10, 6, math.radians(140), math.radians(40), False)
        gc.StrokePath(path)
        path = gc.CreatePath()
        path.AddArc(0, self.mouth_handle.y+17, 8, math.radians(220), math.radians(-40), True)
        gc.StrokePath(path)
        
class Viewport( wx.Panel ):
    def __init__(self, parent, shapes):
        super().__init__(parent, wx.ID_ANY)
        
        self.shapes = shapes
        
        self.lastx = self.lasty = 0
        self.panx, self.pany = 200, 100
        self.gridsize = 50
    
        self.hovered_handle = None
        
        self.GRAY_BRUSH_200 = wx.Brush(wx.Colour(200,200,200))
        self.TGRAY_BRUSH_100 = wx.Brush(wx.Colour(100,100,100, 200))
        self.TBLUE_BRUSH_200 = wx.Brush(wx.Colour(150,150,220, 200))
        
        self.BLACK_PEN = wx.Pen(wx.Colour(0,0,0))
        self.GRAY_PEN_100 = wx.Pen(wx.Colour(100,100,100))
        self.GRAY_PEN_150 = wx.Pen(wx.Colour(150,150,150))
        
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        
        self.InitUI()

    def InitUI(self):
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        
        self.font = self.GetFont()
        
    def OnEraseBackground(self, event):
        pass
        
    def OnPaint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        
        gc = wx.GraphicsContext.Create(dc)
        gc.SetFont(self.font, wx.Colour(0,0,0))
        
        # paint background
        w, h = gc.GetSize()
        w, h = int(w), int(h)
        
        gc.SetBrush(self.GRAY_BRUSH_200)
        gc.DrawRectangle(0,0,w,h)
        
        # draw secondary axis lines
        gc.SetPen(self.GRAY_PEN_150)
        for x in range(int(self.panx)%self.gridsize,w-1,self.gridsize):
            gc.StrokeLine(x, 0, x, h)
        for y in range(int(self.pany)%self.gridsize,h-1,self.gridsize):
            gc.StrokeLine(0, y, w, y)
        # draw main axis lines (horizontal and vertical)
        gc.SetPen(self.GRAY_PEN_100)
        gc.StrokeLine(0, self.pany, w, self.pany)
        gc.StrokeLine(self.panx, 0, self.panx, h)
        
        # pan the viewport
        gc.Translate(self.panx, self.pany)
        
        # draw shapes
        for shape in self.shapes:
            gc.SetPen(self.BLACK_PEN)
            gc.SetBrush(wx.NullBrush)
            shape.draw(gc)
            ''' # to draw all handles
            for handle in shape.getHandles():
                if handle == self.hovered_handle:
                    gc.SetBrush(self.TBLUE_BRUSH_200)
                else:
                    gc.SetBrush(self.TGRAY_BRUSH_100)
                handle.draw(gc)
            '''
        if self.hovered_handle:
            gc.SetBrush(self.TGRAY_BRUSH_100)
            self.hovered_handle.draw(gc)
            
    def OnSize(self, e):
        self.Refresh()

    def OnMouseMotion(self, event):
        x, y = event.GetPosition()
        dx, dy = x-self.lastx, y-self.lasty
        self.lastx, self.lasty = x, y
        
        if event.Dragging():
            if event.MiddleIsDown():
                self.panx += dx
                self.pany += dy
            elif event.LeftIsDown():
                if self.hovered_handle:
                    self.hovered_handle.move(dx, dy)
                    
        else: # event.Dragging
            self.hovered_handle = None
            found = False
            for shape in self.shapes:
                for handle in shape.getHandles():
                    if handle.contains(x-self.panx, y-self.pany):
                        self.hovered_handle = handle
                        found = True
                        break
                if found:
                    break
                    
        self.Refresh()
        
class MainFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        self.shapes = []
        # create default shapes
        shape = Head('Head')
        
        self.shapes.append(shape)
        
        self.viewport = Viewport(self, self.shapes)

    def OnExit(self, event):
        self.Close(True)

if __name__ == '__main__':
    app = wx.App()
    frm = MainFrame(None, title='Facemap')
    frm.Show()
    app.MainLoop()
    
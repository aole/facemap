
import math
import wx

def rotate(px, py, angle, cx=0, cy=0):
    r = math.radians(angle)
    qx = cx + math.cos(r) * (px-cx) - math.sin(r) * (py-cy)
    qy = cy + math.sin(r) * (px-cx) + math.cos(r) * (py-cy)
    
    return qx, qy
    
class UIElement:
    def move(self, dx = 0, dy = 0, event=None):
        pass
    
    def draw(self, gc):
        pass
        
    def contains(self, x, y):
        return False
        
    def scale(self, s=1, event=None):
        pass
        
class Image(wx.Bitmap, UIElement):
    def __init__(self, file, x, y):
        image = wx.Image(file)
        image = image.AdjustChannels(1,1,1,.4)
        super().__init__(image)
        self.bitmapx, self.bitmapy = x, y
        self.bitmapw = image.GetWidth()
        self.bitmaph = image.GetHeight()
        self.bitmapwh = self.bitmapw/self.bitmaph
        
    def draw(self, gc):
        gc.DrawBitmap(self, self.bitmapx, self.bitmapy, int(self.bitmapw), int(self.bitmaph))
        
    def move(self, dx = 0, dy = 0, event=None):
        if event.ControlDown():
            self.bitmapx += dx
            self.bitmapy += dy
        
    def contains(self, x, y, event):
        return x>=self.bitmapx and x<self.bitmapx+self.bitmapw and y>=self.bitmapy and y<self.bitmapy+self.bitmaph
        
    def scale(self, s, event=None):
        if event.ControlDown():
            self.bitmaph += s
            self.bitmapw += s * self.bitmapwh
    
class Handle(UIElement):
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
            
    def move(self, dx = 0, dy = 0, event=None):
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
        
    def draw(self, vp, gc, shaded):
        pass
    
    def getHandles(self):
        return self.handles.values()
        
class Proportion(Shape):
    def __init__(self, name):
        super().__init__(name)
        
        self.size = 20
        self.num_heads = 8
        self.start_y = -int(self.size*self.num_heads/2)
        self.shoulder_y = self.start_y + self.size + self.size/2
        
    def draw(self, vp, gc, shaded):
        gc.SetBrush(wx.NullBrush)
        gc.SetPen(vp.TBLACK_PEN_100)
        '''
        # draw circles
        for y in range(self.start_y, -self.start_y, self.size):
            gc.DrawEllipse(-self.size/2, y, self.size, self.size)
        '''
        gc.SetPen(vp.BLACK_PEN)
        
        # ground
        gc.StrokeLine(-100, -self.start_y+self.size/4, 100, -self.start_y+self.size/4)
        
        # draw head
        gc.DrawEllipse(-self.size/2+self.size/6, self.start_y, 2*self.size/3, self.size)
        
        # draw neck
        gc.StrokeLine(-self.size/10, self.start_y+self.size, -self.size/10, self.shoulder_y)
        gc.StrokeLine(self.size/10, self.start_y+self.size, self.size/10, self.shoulder_y)
        
        # draw chest
        gc.DrawEllipse(-self.size/2, self.start_y+self.size+self.size/3, self.size, self.size+self.size/2+self.size/6)
        
        # draw pelvis
        gc.DrawEllipse(-self.size/2, -self.size, self.size, self.size)
        
        # draw shoulders
        shoulder_x = 2*self.size/3
        gc.StrokeLine(-shoulder_x, self.shoulder_y, shoulder_x, self.shoulder_y)
        gc.DrawEllipse(-shoulder_x-self.size/8, self.shoulder_y-self.size/8, self.size/4, self.size/4)
        gc.DrawEllipse(shoulder_x-self.size/8, self.shoulder_y-self.size/8, self.size/4, self.size/4)
        
        # draw arms
        hand_x, hand_y = rotate(shoulder_x, 0, -25, shoulder_x, self.shoulder_y)
        gc.StrokeLine(-shoulder_x, self.shoulder_y, -hand_x, hand_y)
        gc.StrokeLine(shoulder_x, self.shoulder_y, hand_x, hand_y)
        
        # elbow
        elbow_x, elbow_y = rotate(shoulder_x, self.shoulder_y/2, -25, shoulder_x, self.shoulder_y)
        gc.DrawEllipse(-elbow_x-self.size/8, elbow_y, self.size/4, self.size/4)
        gc.DrawEllipse(elbow_x-self.size/8, elbow_y, self.size/4, self.size/4)
        
        # hands
        #gc.DrawEllipse(-hand_x-self.size/4, hand_y, self.size/2, self.size/2)
        #gc.DrawEllipse(hand_x-self.size/4, hand_y, self.size/2, self.size/2)
        path = gc.CreatePath()
        path.MoveToPoint(self.size/8, 0)
        path.AddLineToPoint(-self.size/8, 0)
        path.AddLineToPoint(-self.size/8, self.size-self.size/4)
        path.AddLineToPoint(0, self.size-self.size/8)
        path.AddLineToPoint(self.size/6, self.size-self.size/2)
        path.CloseSubpath()
        
        gc.PushState()
        gc.Scale(-1, 1)
        gc.Translate(hand_x, hand_y)
        gc.Rotate(math.radians(-25))
        gc.StrokePath(path)
        gc.PopState()
        
        gc.PushState()
        gc.Translate(hand_x, hand_y)
        gc.Rotate(math.radians(-25))
        gc.StrokePath(path)
        gc.PopState()
        
        # draw legs
        gc.DrawEllipse(-self.size/2-self.size/8, 0, self.size/4, self.size/4)
        gc.DrawEllipse(self.size/2-self.size/8, 0, self.size/4, self.size/4)
        
        knee_x, knee_y = self.size/2-self.size/8, self.num_heads/4*self.size+self.size/8
        
        gc.StrokeLine(-self.size/2, self.size/8, -knee_x, knee_y)
        gc.StrokeLine(self.size/2, self.size/8, knee_x, knee_y)
        
        gc.DrawEllipse(-knee_x-self.size/8, knee_y-self.size/8, self.size/4, self.size/4)
        gc.DrawEllipse(knee_x-self.size/8, knee_y-self.size/8, self.size/4, self.size/4)
        
        foot_x, foot_y = self.size/2-self.size/8, self.num_heads/2*self.size
        
        gc.StrokeLine(-knee_x, knee_y, -foot_x, foot_y)
        gc.StrokeLine(knee_x, knee_y, foot_x, foot_y)
        # foot
        #gc.DrawEllipse(-self.size/2-self.size/8, self.num_heads/2*self.size, self.size/4, self.size/4)
        #gc.DrawEllipse(self.size/2-self.size/8, self.num_heads/2*self.size, self.size/4, self.size/4)
        path = gc.CreatePath()
        path.MoveToPoint(foot_x-self.size/7, foot_y+self.size/8)
        path.AddLineToPoint(foot_x, foot_y+self.size/8)
        path.AddLineToPoint(foot_x+self.size/4, foot_y+self.size/6)
        path.AddLineToPoint(foot_x+self.size/4, foot_y+self.size/4)
        path.AddLineToPoint(foot_x-self.size/7, foot_y+self.size/4)
        path.AddLineToPoint(foot_x-self.size/7, foot_y+self.size/6)
        path.AddLineToPoint(foot_x-self.size/9, foot_y)
        path.AddLineToPoint(foot_x+self.size/9, foot_y)
        path.AddLineToPoint(foot_x+self.size/4, foot_y+self.size/6)
        
        path.MoveToPoint(-foot_x+self.size/7, foot_y+self.size/8)
        path.AddLineToPoint(-foot_x, foot_y+self.size/8)
        path.AddLineToPoint(-foot_x-self.size/4, foot_y+self.size/6)
        path.AddLineToPoint(-foot_x-self.size/4, foot_y+self.size/4)
        path.AddLineToPoint(-foot_x+self.size/7, foot_y+self.size/4)
        path.AddLineToPoint(-foot_x+self.size/7, foot_y+self.size/6)
        path.AddLineToPoint(-foot_x+self.size/9, foot_y)
        path.AddLineToPoint(-foot_x-self.size/9, foot_y)
        path.AddLineToPoint(-foot_x-self.size/4, foot_y+self.size/6)
        gc.StrokePath(path)
        
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
        
        self.eyes_handle = Handle('Eyes', 22, 23)
        self.addHandle(self.eyes_handle)
        
        self.nose_handle = Handle('Nose', 0, 55)
        self.nose_handle.setConstraints(canx=False)
        self.addHandle(self.nose_handle)
        
        self.mouth_handle = Handle('Mouth', 0, 66)
        self.mouth_handle.setConstraints(canx=False)
        self.addHandle(self.mouth_handle)
        
        self.hairline_handle = Handle('Hairline', 0, -30)
        self.hairline_handle.setConstraints(canx=False)
        self.addHandle(self.hairline_handle)
        
    def draw(self, vp, gc, shaded):
        gc.SetBrush(wx.NullBrush)
            
        gc.SetPen(vp.BLACK_PEN)
        
        # head shape
        path1 = gc.CreatePath()
        path1.AddArc(0, 0, self.head_handle.x, math.radians(180), math.radians(0), True)
        
        
        path1.AddLineToPoint(self.jaw_handle.x, self.jaw_handle.y)
        path1.AddLineToPoint(self.chin_width_handle.x, self.chin_width_handle.y)
        path1.AddLineToPoint(0, self.chin_handle.y)
        path1.AddLineToPoint(-self.chin_width_handle.x, self.chin_width_handle.y)
        path1.AddLineToPoint(-self.jaw_handle.x, self.jaw_handle.y)

        path1.CloseSubpath()
        
        if shaded:
            gc.SetBrush(vp.SKIN_BASE_BRUSH)
            gc.FillPath(path1)
            
            gc.SetBrush(vp.SKIN_LIT0_BRUSH)
            path2 = gc.CreatePath()
            path2.MoveToPoint(-42, -18)
            path2.AddLineToPoint(-32, 12)
            path2.AddLineToPoint(-14, 14)
            path2.AddLineToPoint(-25, -40)
            path2.CloseSubpath()
            gc.FillPath(path2)
            '''
            gc.SetBrush(vp.SKIN_BASE_BRUSH)
            path2 = gc.CreatePath()
            path2.MoveToPoint(25, -40)
            path2.AddLineToPoint(14, 14)
            path2.AddLineToPoint(-14, 14)
            path2.AddLineToPoint(-25, -40)
            path2.CloseSubpath()
            gc.FillPath(path2)
            '''
            '''
            gc.SetBrush(gc.CreateLinearGradientBrush(-35, -25, 0, -27, wx.Colour(234,210,184), wx.Colour(222,191,162)))
            path2 = gc.CreatePath()
            path2.MoveToPoint(-33, -29)
            path2.AddLineToPoint(-23, 13)
            path2.AddLineToPoint(0, 14)
            path2.AddLineToPoint(0, -40)
            path2.CloseSubpath()
            gc.FillPath(path2)
            '''
            gc.SetBrush(vp.SKIN_LIT2_BRUSH)
            path2 = gc.CreatePath()
            path2.MoveToPoint(42, -18)
            path2.AddLineToPoint(32, 12)
            path2.AddLineToPoint(14, 14)
            path2.AddLineToPoint(25, -40)
            path2.CloseSubpath()
            gc.FillPath(path2)
            '''
            gc.SetBrush(gc.CreateLinearGradientBrush(0, -27, 35, -27, wx.Colour(222,191,162), wx.Colour(156,93,86)))
            path2 = gc.CreatePath()
            path2.MoveToPoint(30, -29)
            path2.AddLineToPoint(23, 13)
            path2.AddLineToPoint(0, 14)
            path2.AddLineToPoint(0, -40)
            path2.CloseSubpath()
            gc.FillPath(path2)
        '''
        gc.StrokePath(path1)
        gc.SetBrush(wx.NullBrush)
        
        # eyes
        gc.SetBrush(vp.GRAY_BRUSH_220)
        gc.DrawEllipse(-self.eyes_handle.x-13, self.eyes_handle.y-4, 25, 8)
        gc.DrawEllipse(self.eyes_handle.x-13, self.eyes_handle.y-4, 25, 8)
        
        # eye balls
        gc.SetBrush(vp.BLACK_BRUSH)
        path = gc.CreatePath()
        path.AddArc(self.eyes_handle.x, self.eyes_handle.y-2, 6, math.radians(180), math.radians(0), False)
        gc.DrawPath(path)
        path = gc.CreatePath()
        path.AddArc(-self.eyes_handle.x, self.eyes_handle.y-2, 6, math.radians(180), math.radians(0), False)
        gc.DrawPath(path)
        gc.SetBrush(wx.NullBrush)
        
        # eyebrows
        gc.SetBrush(vp.GRAY_BRUSH_50)
        path = gc.CreatePath()
        path.MoveToPoint(-self.eyes_handle.x-18, self.eyes_handle.y-2)
        path.AddLineToPoint(-self.eyes_handle.x-11, self.eyes_handle.y-10)
        path.AddLineToPoint(-self.eyes_handle.x+13, self.eyes_handle.y-7)
        path.AddLineToPoint(-self.eyes_handle.x+11, self.eyes_handle.y-11)
        path.AddLineToPoint(-self.eyes_handle.x-11, self.eyes_handle.y-14)
        path.CloseSubpath()
        
        path.MoveToPoint(self.eyes_handle.x+18, self.eyes_handle.y-2)
        path.AddLineToPoint(self.eyes_handle.x+11, self.eyes_handle.y-10)
        path.AddLineToPoint(self.eyes_handle.x-13, self.eyes_handle.y-7)
        path.AddLineToPoint(self.eyes_handle.x-11, self.eyes_handle.y-11)
        path.AddLineToPoint(self.eyes_handle.x+11, self.eyes_handle.y-14)
        path.CloseSubpath()
        gc.DrawPath(path)
        gc.SetBrush(wx.NullBrush)
        
        # nose
        path = gc.CreatePath()
        path.MoveToPoint(-4, self.nose_handle.y)
        path.AddLineToPoint(4, self.nose_handle.y)
        
        path.MoveToPoint(7, self.nose_handle.y)
        path.AddLineToPoint(12, self.nose_handle.y-4)
        path.AddLineToPoint(8, self.nose_handle.y-10)
        
        path.MoveToPoint(-7, self.nose_handle.y)
        path.AddLineToPoint(-12, self.nose_handle.y-4)
        path.AddLineToPoint(-8, self.nose_handle.y-10)
        
        gc.StrokePath(path)
        
        gc.SetBrush(vp.GRAY_BRUSH_50)
        gc.DrawEllipse(2, self.nose_handle.y-3, 5, 2)
        gc.DrawEllipse(-7, self.nose_handle.y-3, 5, 2)
        gc.SetBrush(wx.NullBrush)
        
        # ears
        path = gc.CreatePath()
        path.MoveToPoint(self.head_handle.x, self.eyes_handle.y)
        path.AddLineToPoint(self.head_handle.x+4, self.eyes_handle.y-4)
        path.AddLineToPoint(self.head_handle.x+8, self.eyes_handle.y-4)
        path.AddLineToPoint(self.head_handle.x+8, self.eyes_handle.y+6)
        path.AddLineToPoint(self.head_handle.x+4, self.eyes_handle.y+20)
        path.AddLineToPoint(self.head_handle.x-4, self.nose_handle.y)
        
        path.MoveToPoint(-self.head_handle.x, self.eyes_handle.y)
        path.AddLineToPoint(-self.head_handle.x-4, self.eyes_handle.y-4)
        path.AddLineToPoint(-self.head_handle.x-8, self.eyes_handle.y-4)
        path.AddLineToPoint(-self.head_handle.x-8, self.eyes_handle.y+6)
        path.AddLineToPoint(-self.head_handle.x-4, self.eyes_handle.y+20)
        path.AddLineToPoint(-self.head_handle.x+4, self.nose_handle.y)
        
        if shaded:
            gc.SetBrush(vp.SKIN_BASE_BRUSH)
            gc.DrawPath(path)
            gc.SetBrush(wx.NullBrush)
        else:
            gc.StrokePath(path)
            
        # mouth
        path = gc.CreatePath()
        path.MoveToPoint(0, self.mouth_handle.y)
        path.AddLineToPoint(5, self.mouth_handle.y-2)
        path.AddLineToPoint(self.eyes_handle.x-6, self.mouth_handle.y)
        gc.DrawEllipse(self.eyes_handle.x-6, self.mouth_handle.y-2, 4, 2)
        gc.StrokePath(path)
        
        path = gc.CreatePath()
        path.MoveToPoint(0, self.mouth_handle.y)
        path.AddLineToPoint(-5, self.mouth_handle.y-2)
        path.AddLineToPoint(-self.eyes_handle.x+6, self.mouth_handle.y)
        gc.DrawEllipse(-self.eyes_handle.x+2, self.mouth_handle.y-2, 4, 2)
        gc.StrokePath(path)
        
        path = gc.CreatePath()
        path.AddArc(0, self.mouth_handle.y-10, 6, math.radians(140), math.radians(40), False)
        gc.StrokePath(path)
        
        gc.StrokeLine(-8, self.mouth_handle.y+7, 8, self.mouth_handle.y+7)
        
        # hair
        path = gc.CreatePath()
        path.MoveToPoint(0, self.hairline_handle.y)
        path.AddLineToPoint(-15, self.hairline_handle.y-5)
        path.AddLineToPoint(-30, self.hairline_handle.y+5)
        path.AddLineToPoint(-40, self.hairline_handle.y+20)
        path.AddLineToPoint(-35, self.hairline_handle.y+35)
        path.AddLineToPoint(-45, self.hairline_handle.y+45)
        
        path.AddArc(0, 0, self.head_handle.x+8, math.radians(160), math.radians(20), True)
        
        path.AddLineToPoint(45, self.hairline_handle.y+45)
        path.AddLineToPoint(35, self.hairline_handle.y+35)
        path.AddLineToPoint(40, self.hairline_handle.y+20)
        path.AddLineToPoint(30, self.hairline_handle.y+5)
        path.AddLineToPoint(15, self.hairline_handle.y-5)
        
        path.CloseSubpath()
        
        gc.SetBrush(vp.GRAY_BRUSH_50)
        gc.DrawPath(path)
        gc.SetBrush(wx.NullBrush)
        
class Viewport( wx.Panel ):
    def __init__(self, parent, shapes):
        super().__init__(parent, wx.ID_ANY)
        
        self.shapes = shapes
        self.shaded = True
        self.hovered_element = None
        
        self.lastx = self.lasty = 0
        self.panx, self.pany = 200, 100
        self.gridsize = 50
    
        self.BLACK_BRUSH = wx.Brush(wx.Colour(0,0,0))
        self.WHITE_BRUSH = wx.Brush(wx.Colour(255,255,255))
        self.SKIN_LIT0_BRUSH = wx.Brush(wx.Colour(234,210,184))
        self.SKIN_LIT2_BRUSH = wx.Brush(wx.Colour(156,93,86))
        self.SKIN_BASE_BRUSH = wx.Brush(wx.Colour(222,191,162))
        self.SKIN_SHADOW_BRUSH = wx.Brush(wx.Colour(90,47,57))
        self.GRAY_BRUSH_50 = wx.Brush(wx.Colour(50,50,50))
        self.GRAY_BRUSH_200 = wx.Brush(wx.Colour(200,200,200))
        self.GRAY_BRUSH_220 = wx.Brush(wx.Colour(220,220,220))
        self.TGRAY_BRUSH_100 = wx.Brush(wx.Colour(100,100,100, 200))
        self.TBLUE_BRUSH_200 = wx.Brush(wx.Colour(150,150,220, 200))
        
        self.BLACK_PEN = wx.Pen(wx.Colour(0,0,0))
        self.TBLACK_PEN_100 = wx.Pen(wx.Colour(0,0,0, 100))
        self.GRAY_PEN_100 = wx.Pen(wx.Colour(100,100,100))
        self.GRAY_PEN_150 = wx.Pen(wx.Colour(150,150,150))
        
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        
        self.background_image = False
        self.bgImage = Image('facemap.jpg', -self.panx, -self.pany)
        
        self.InitUI()

    def InitUI(self):
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        
        self.font = self.GetFont()
        
    def OnKeyDown(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_F1:
            self.background_image = not self.background_image
        elif keycode == wx.WXK_F2:
            self.shaded = not self.shaded
            
        self.Refresh()
        
    def OnEraseBackground(self, event):
        pass
        
    def OnPaint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        
        gc = wx.GraphicsContext.Create(dc)
        
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
        
        gc.PushState()
        # pan the viewport
        gc.Translate(self.panx, self.pany)
        
        # draw shapes
        for shape in self.shapes:
            shape.draw(self, gc, self.shaded)
            ''' # to draw all handles
            for handle in shape.getHandles():
                if handle == self.hovered_element:
                    gc.SetBrush(self.TBLUE_BRUSH_200)
                else:
                    gc.SetBrush(self.TGRAY_BRUSH_100)
                handle.draw(gc)
            '''
        if self.hovered_element and type(self.hovered_element)==Handle:
            gc.SetBrush(self.TGRAY_BRUSH_100)
            self.hovered_element.draw(gc)
            
        # draw bitmap
        if self.bgImage and self.background_image:
            self.bgImage.draw(gc)
        
        gc.PopState()
        
        gc.SetFont(self.GetFont(), wx.Colour(0,0,0))
        gc.DrawText('F1: '+('Hide Image' if self.background_image else 'Show Image'), 10, 10)
        gc.DrawText('F2: '+('Shaded' if self.shaded else 'Unshaded'), 10, 25)
        
    def OnSize(self, e):
        self.Refresh()

    def OnMouseMotion(self, event):
        x, y = event.GetPosition()
        #print(x-self.panx, y-self.pany)
        dx, dy = x-self.lastx, y-self.lasty
        self.lastx, self.lasty = x, y
        
        if event.Dragging():
            if event.MiddleIsDown():
                self.panx += dx
                self.pany += dy
            elif event.LeftIsDown():
                if self.hovered_element:
                    # move shape handles
                    self.hovered_element.move(dx, dy, event)
        else: # event.Dragging
            self.hovered_element = None
            found = False
            for shape in self.shapes:
                for handle in shape.getHandles():
                    if handle.contains(x-self.panx, y-self.pany):
                        self.hovered_element = handle
                        found = True
                        break
                if found:
                    break
            if not found and self.bgImage:
                if self.bgImage.contains(x-self.panx, y-self.pany, event):
                    self.hovered_element = self.bgImage
                    
        self.Refresh()
    
    def OnMouseWheel(self, event):
        if self.hovered_element:
            s = event.GetLinesPerAction()* event.GetWheelRotation()/120
            self.hovered_element.scale(s, event)
        
        self.Refresh()
    
class MainFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        self.shapes = []
        # create default shapes
        #shape = Head('Head')
        shape = Proportion('Male')
        
        self.shapes.append(shape)
        
        self.viewport = Viewport(self, self.shapes)

    def OnExit(self, event):
        self.Close(True)

if __name__ == '__main__':
    app = wx.App()
    frm = MainFrame(None, title='Facemap')
    frm.Show()
    app.MainLoop()
    
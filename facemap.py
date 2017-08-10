import tkinter as tk
from PIL import Image, ImageTk

class Handle:
	count = 1
	w2 = 4
	h2 = 4
	
	def __init__( self, x, y, line ):
		self.x, self.y, self.line, self.name = x, y, line, 'handle'+str(Handle.count)
		Handle.count += 1

	def draw( self, canvas ):
		canvas.create_rectangle(self.x-self.w2, self.y-self.h2, self.x+self.w2, self.y+self.h2, tags=self.name)

	def intersect( self, x, y ):
		if x<self.x+self.w2 and x>self.x-self.w2 and y<self.y+self.h2 and y>self.y-self.h2:
			return True

	def translate( self, canvas, dx, dy ):
		self.x += dx
		self.y += dy
		canvas.move( self.name, dx, dy )
		self.line.redraw(canvas)

class Line:
	def __init__( self, x1, y1, x2, y2 ):
		self.h1 = Handle(x1, y1, self)
		self.h2 = Handle(x2, y2, self)
	
	def draw( self, canvas, edit ):
		self.line = canvas.create_line(self.h1.x, self.h1.y, self.h2.x, self.h2.y)
		if edit:
			self.h1.draw(canvas)
			self.h2.draw(canvas)

	def redraw( self, canvas ):
		canvas.delete( self.line )
		self.draw( canvas, True )

class Application:
	lines = []
	selectedline = None
	mousedown = False
	prevx, prevy = 0,0
	fpx,fpy = 0,0
	mousemode = 1 # Create 2: Edit
	secondpoint = False
	
	def __init__(self, w, h):
		self.root = tk.Tk()

		self.canvas = tk.Canvas(self.root, width=w, height=h)

		self.canvas.bind('<ButtonPress-1>', self.left_mouse_down) #left mouse down
		self.canvas.bind('<ButtonRelease-1>', self.left_mouse_up) #left mouse up
		self.canvas.bind('<Motion>', self.mouse_move) #move move
		self.canvas.bind('<Key>', self.key_press) #move move
		self.canvas.pack()

		line = Line(50,50,160,70)
		self.lines.append( line )

		self.repaint()
		
		#self.label = tk.Label(self.root, anchor=tk.S, text='coords')
		#self.label.pack()

	def render_image(self, file, loc):
		image = Image.open(file)
		photo = ImageTk.PhotoImage(image)
		self.canvas.image = photo
		self.canvas.create_image(loc, image = photo, anchor = tk.NW)
		
	def mouse_move( self, event ):
		#self.label['text'] = str(event.x)+','+str(event.y)
		if self.mousemode==2: # Edit
			if self.mousedown and self.selectedline != None:
				self.selectedline.translate(self.canvas, event.x-self.prevx, event.y-self.prevy)

		self.prevx, self.prevy = event.x, event.y
			
	def left_mouse_down( self, event ):
		self.mousedown = True
		if self.mousemode==2: # Edit
			self.selectedline = None
			for line in self.lines:
				if line.h1.intersect(event.x, event.y):
					self.selectedline = line.h1
					break
				elif line.h2.intersect(event.x, event.y):
					self.selectedline = line.h2
					break
					
		self.prevx, self.prevy = event.x, event.y
		
	def left_mouse_up( self, event ):
		self.mousedown = False
		if self.mousemode==1:
			if self.secondpoint:
				line = Line(self.fpx, self.fpy, event.x, event.y)
				self.lines.append( line )
				self.repaint()
				self.secondpoint = False
			else:
				self.fpx, self.fpy = event.x, event.y
				self.secondpoint = True
				
		self.prevx, self.prevy = event.x, event.y

	def key_press( self, event ):
		if event.keysym=='Tab':
			self.mousemode = 2 if self.mousemode==1 else 1
			self.repaint()

	def run(self):
		self.root.mainloop()

	def repaint(self):
		self.canvas.delete("all")
		for h in self.lines:
			h.draw(self.canvas, self.mousemode==2)
		
app = Application(340, 480)
#app.render_image("C:/Users/baole/Downloads/facemap.jpg", (0,0))
app.run()
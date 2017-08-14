import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from PIL import Image, ImageTk

''' 
TODO:
1. edit mirror
2. selected handle/line
3. delete lines
4. undo/redo
5. truncate lines at mirror
6. create mirrored lines; ctrl+m on selected line
7. only 1 editable line
8. F1 (Help screen)
9. resize
'''

class Handle:
	count = 1
	w2 = 4
	h2 = 4
	lines=[]
	
	def __init__( self, x, y, line ):
		self.x, self.y, self.name = x, y, 'handle'+str(Handle.count)
		Handle.count += 1
		self.lines.append(line)

	def draw( self, canvas ):
		canvas.create_rectangle(self.x-self.w2, self.y-self.h2, self.x+self.w2, self.y+self.h2, tags=self.name)

	def intersect( self, x, y ):
		if x<self.x+self.w2 and x>self.x-self.w2 and y<self.y+self.h2 and y>self.y-self.h2:
			return True

	def translate( self, canvas, dx, dy ):
		self.x += dx
		self.y += dy
		canvas.move( self.name, dx, dy )
		for line in self.lines:
			line.redraw(canvas)

class Line:
	templine = 0 # create rubberband to display what line will be created
	edit = False
	
	def __init__( self, x1, y1, x2, y2 ):
		self.h1 = Handle(x1, y1, self)
		self.h2 = Handle(x2, y2, self)
	
	def draw( self, canvas ):
		self.line = canvas.create_line(self.h1.x, self.h1.y, self.h2.x, self.h2.y)
		if self.edit:
			self.h1.draw(canvas)
			self.h2.draw(canvas)

	def redraw( self, canvas ):
		canvas.delete( self.line )
		self.draw( canvas )

	def rubberband(canvas, x1, y1, x2, y2):
		if Line.templine != 0:
			canvas.delete(Line.templine)
		Line.templine = canvas.create_line(x1, y1, x2, y2)
	
	def save(self, file):
		msg = ','.join(map(str, [self.h1.x, self.h1.y, self.h2.x, self.h2.y]))
		file.write(msg)

class Application:
	lines = [] # all lines that need drawing
	
	mousedown = False #is mouse button down
	prevx, prevy = 0,0 # last mouse moved position. needed for dx/dy
	
	selectedline = None
	selectedhandle = None # handle that is currently editing
	
	mousemode = 1 #Create. 2: Edit. press TAB to change
	
	fpx,fpy = 0,0
	secondpoint = False
	
	showmirror = False
	
	def __init__(self, w, h):
		self.root = tk.Tk()
		self.root.title("Face Map")

		self.canvas = tk.Canvas(self.root, width=w, height=h)
		self.canvas.image = None

		self.canvas.bind('<ButtonPress-1>', self.left_mouse_down) #left mouse down
		self.canvas.bind('<ButtonRelease-1>', self.left_mouse_up) #left mouse up
		self.canvas.bind('<Motion>', self.mouse_move) #move move
		self.canvas.bind('<Key-Tab>', self.key_tab) #move move
		self.canvas.bind('<Key-m>', self.key_m) #move move
		self.canvas.bind('<Enter>', self.mouse_enter)
		self.root.bind('<Control-Key-i>', self.key_control_i)
		self.root.bind('<Control-Key-o>', self.key_control_o)
		self.root.bind('<Control-Key-s>', self.key_control_s)
		self.canvas.pack()

		mousemode = 1
		self.root.config(cursor="target")

		#self.label = tk.Label(self.root, anchor=tk.S, text='coords')
		#self.label.pack()

	def key_control_i(self, event):
		filename = askopenfilename()
		if filename != None:
			self.render_image(filename, (0,0))
			self.repaint()
	
	def render_image(self, file, loc):
		image = Image.open(file)
		photo = ImageTk.PhotoImage(image)
		self.canvas.image = photo
		self.canvas.create_image(loc, image = photo, anchor = tk.NW)
	
	def mouse_move( self, event ):
		#self.label['text'] = str(event.x)+','+str(event.y)
		if self.mousemode==1:
			if self.secondpoint:
				Line.rubberband(self.canvas, self.fpx, self.fpy, event.x, event.y)
		if self.mousemode==2: # Edit
			if self.mousedown and self.selectedhandle != None:
				self.selectedhandle.translate(self.canvas, event.x-self.prevx, event.y-self.prevy)

		self.prevx, self.prevy = event.x, event.y
	
	def left_mouse_down( self, event ):
		self.mousedown = True
		if self.mousemode==2: # Edit
			self.selectedhandle = None
			self.selectedline = None
			for line in self.lines:
				if line.h1.intersect(event.x, event.y):
					self.selectedhandle = line.h1
					self.selectedline = line
					break
				elif line.h2.intersect(event.x, event.y):
					self.selectedhandle = line.h2
					self.selectedline = line
					break
			if self.selectedhandle == None:
				overlapping = self.canvas.find_overlapping(event.x-4, event.y-4, event.x+4, event.y+4)
				print(overlapping)
					
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

	def toggle_mouse_mode(self):
		if self.mousemode == 1:
			self.mousemode = 2
			self.root.config(cursor="")
		else:
			self.mousemode = 1
			self.root.config(cursor="target")
			
		self.repaint()
	
	def key_tab( self, event ):
		self.toggle_mouse_mode()
	
	def mouse_enter( self, event ):
		self.canvas.focus_set()
	
	def run(self):
		self.root.mainloop()

	def repaint(self):
		self.canvas.delete("all")
		# background image
		if self.canvas.image != None:
			self.canvas.create_image((0,0), image = self.canvas.image, anchor = tk.NW)
		# lines
		for h in self.lines:
			h.draw(self.canvas)
		# mirror line
		if self.showmirror:
			x = self.canvas.winfo_width()/2
			y = self.canvas.winfo_height()
			self.canvas.create_line(x, 0, x, y, fill='red',dash=[2,3])
	
	def key_m( self, event ):
		self.showmirror = not self.showmirror
		self.repaint()
	
	def key_control_s( self, event ):
		#filename = asksaveasfilename(defaultextension='.txt')
		filename = 'test.txt'
		if filename != None:
			file = open(filename, 'w')
			self.save(file)
			file.close()
	
	def save(self, file):
		for line in self.lines:
			line.save(file)
			file.write('\n')
	
	def key_control_o( self, event ):
		#filename = askopenfilename()
		filename = 'test.txt'
		if filename != None:
			file = open(filename, 'r')
			self.load(file)
			file.close()
	
	def load(self, file):
		self.lines.clear()
		for readline in file:
			if readline.strip()=='':
				continue
			coords = [int(x.strip()) for x in readline.split(',')]
			self.lines.append(Line(coords[0], coords[1], coords[2], coords[3]))
		self.repaint()
	
app = Application(340, 480)
app.run()
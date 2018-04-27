import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from PIL import Image, ImageTk
from tkinter import messagebox
from tkinter import ttk

''' 
TODO:
1. edit mirror
5. truncate lines at mirror
6. create mirrored lines; ctrl+m on selected line
10. select multiple
11. Panning
12. other shapes
13. edit only selected lines
14. scroll bars
15.
'''

class Handle:
    count = 1
    w2 = 4
    h2 = 4
    
    class LineEditAction:
        def __init__(self, handle, x1, y1, x2, y2):
            self.handle = handle
            self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
            
        def redo(self):
            self.handle.update( self.x2, self.y2 )
        
        def undo(self):
            self.handle.update( self.x1, self.y1 )

    class HandleDeleteAction:
        def __init__(self, line, handle):
            self.line = line
            self.handle = handle
            
        def redo(self):
            self.line.remove_handle( self.handle )
        
        def undo(self):
            self.handle.update( self.x1, self.y1 )

    def __init__( self, app, x, y, line, index ):
        self.app = app
        self.canvas = app.canvas
        self.line = line
        self.index = index
        
        self.mousedown = False
        
        self.shape = self.canvas.create_rectangle( x-self.w2, y-self.h2, x+self.w2, y+self.h2, activeoutline='#BBBBEE' )
        
        self.canvas.tag_bind( self.shape, '<Button-1>', self.on_left_click )
        self.canvas.tag_bind( self.shape, '<ButtonRelease-1>', self.on_left_up )
        self.canvas.tag_bind( self.shape, '<B1-Motion>', self.on_left_drag )
        self.canvas.tag_bind( self.shape, '<Control-ButtonPress-1>', self.ctrl_left_mouse_down)
        
    def getCoords( self ):
        coords = self.canvas.coords( self.shape )
        return [coords[0]+self.w2, coords[1]+self.h2]
        
    def editable( self, b ):
        if not self.visible:
            return
        
        state = tk.NORMAL if b else tk.HIDDEN
        self.canvas.itemconfig( self.shape, state=state )
        
    def on_left_click( self, event ):
        self.mousedown = True
        self.prevx, self.prevy = self.origx, self.origy = event.x, event.y
        
    def on_left_up( self, event ):
        if self.mousedown:
            self.app.undomanager.add( Handle.LineEditAction( self, self.origx, self.origy, event.x, event.y ) )
        self.mousedown = False
        
    def on_left_drag( self, event ):
        dx, dy = event.x-self.prevx, event.y-self.prevy
        self.move( dx, dy )
        self.prevx, self.prevy = event.x, event.y

    def ctrl_left_mouse_down( self, event ):
        self.line.remove_handle( self )
        
    def update( self, x, y ):
        coords = self.canvas.coords( self.shape )
        self.move( x-(coords[0]+self.w2), y-(coords[1]+self.h2) )
        
    def move( self, dx, dy ):
        self.canvas.move( self.shape, dx, dy )
        
        new_coords = self.canvas.coords( self.shape )
        
        line = self.line
        idx = self.index
        line_coords = self.canvas.coords( line.shape )
        line_coords[idx*2] = new_coords[0]+self.w2
        line_coords[idx*2+1] = new_coords[1]+self.h2
        self.canvas.coords( line.shape, line_coords )
            
    def show( self ):
        if app.is_edit_mode() and self.line.is_visible():
            self.canvas.itemconfig( self.shape, state=tk.NORMAL )
        else:
            self.canvas.itemconfig( self.shape, state=tk.HIDDEN )
        
class Line:
    class LineAddAction:
        def __init__(self, line):
            self.line = line
            
        def redo(self):
            self.line.set_visible( True )
        
        def undo(self):
            self.line.set_visible( False )

    class HandleAddAction:
        def __init__( self, line, handle, x, y ):
            self.line = line
            self.handle = handle
            self.x, self.y = x, y
            
        def redo(self):
            self.line.add_handle( self.handle, self.x, self.y, self.handle.index )
        
        def undo(self):
            self.line.remove_handle( self.handle )

    def __init__( self, app, coords ):
        self.app = app
        self.canvas = app.canvas
        
        self.shape = self.canvas.create_line( coords, smooth=True, activefill='#CC0000', tags='LINE' )
        self.canvas.tag_bind( self.shape, '<Control-ButtonPress-1>', self.ctrl_left_mouse_down)
        
        self.handles = []
        for i in range( 0, len(coords), 2 ):
            self.handles.append( Handle( app, coords[i], coords[i+1], self, int(i/2) ) )
            
        self.set_editable( app.is_edit_mode() )
        self.set_visible( True )
        
    def ctrl_left_mouse_down( self, event ):
        if self.editable:
            replace_index = self.handles[-1].index
            handle = Handle( self.app, event.x, event.y, self, replace_index )
            self.add_handle( handle, event.x, event.y, replace_index )
            self.app.undomanager.add( Line.HandleAddAction( self, handle, event.x, event.y ) )
            
    def add_handle( self, handle, x, y, index ):
        for idx in range( index, len(self.handles) ):
            self.handles[idx].index += 1
            
        self.handles.insert( index, handle )

        line_coords = self.canvas.coords( self.shape )
        line_coords.insert( index*2, y )
        line_coords.insert( index*2, x )
        self.canvas.coords( self.shape, line_coords )
        
        handle.show()
        
    def remove_handle( self, handle ):
        if len(self.handles)<=2:
            return
            
        self.handles.remove( handle )
        
        index = handle.index
        line_coords = self.canvas.coords( self.shape )
        del line_coords[index*2]
        del line_coords[index*2]
        self.canvas.coords( self.shape, line_coords )
        
        for idx in range( index, len(self.handles) ):
            self.handles[idx].index -= 1
        
        handle.show()
        
    def update_end( self, x, y ):
        self.handles[-1].update( x, y )
        
    def save(self, file):
        coords = self.canvas.coords( self.shape )
        msg = ','.join(str(x) for x in coords)
        file.write(msg)

    def load( app, strline ):
        coords = [float(x.strip()) for x in strline.split(',')]
        return Line( app, coords )
        
    def set_editable( self, edit ):
        self.editable = edit
        for h in self.handles:
            h.show()
        
    def set_visible( self, v ):
        self.visible = v
        if v:
            self.canvas.itemconfig( self.shape, state=tk.NORMAL )
        else:
            self.canvas.itemconfig( self.shape, state=tk.HIDDEN )
            
        for h in self.handles:
            h.show()
    
    def is_visible( self ):
        return self.visible
        
    def select( self ):
        self.canvas.itemconfig( self.shape, fill='blue' )
    
    def deselect( self ):
        self.canvas.itemconfig( self.shape, fill='black' )
        
class UndoManager:
    def __init__(self,):
        self.undos = []
        self.redos = []
    
    def add( self, command ):
        self.undos.append(command)
        self.redos.clear()
    
    def undo(self):
        try:
            command = self.undos.pop()
            command.undo()
            self.redos.append(command)
        except IndexError:
            pass

    def redo(self):
        try:
            command = self.redos.pop()
            command.redo()
            self.undos.append(command)
        except IndexError:
            pass

class Application( tk.Frame ):
    
    mousedown = False #is mouse button down
    prevx, prevy = 0,0 # last mouse moved position. needed for dx/dy
    
    mousemode = 1 #Create. 2: Edit. press TAB to change
    
    class SelectAction:
        def __init__( self, app, newSelection, oldSelection ):
            self.app = app
            self.newSelection = newSelection
            self.oldSelection = oldSelection
            
        def undo(self):
            self.app.select_line( self.oldSelection, False )
            
        def redo(self):
            self.app.select_line( self.newSelection, False )
            
    class DeleteAction:
        def __init__( self, line ):
            self.line = line
            
        def undo(self):
            self.line.set_visible( True )
            
        def redo(self):
            self.line.set_visible( False )
            
    def __init__(self, w, h):
        mousemode = 1
        self.lines = [] # all lines that need drawing
        self.linesMap = {}
        self.currentLine = None
        self.selectedLine = None
        
        self.undomanager = UndoManager()
        
        self.root = tk.Tk()
        self.root.title("Face Map")

        tk.Frame.__init__( self, self.root )
        
        self.canvas = tk.Canvas( self, closeenough=5 )
        
        self.canvas.image = None
        self.image_shape = None
        
        vbar = ttk.Scrollbar( self, orient='vertical', command=self.canvas.yview )
        hbar = ttk.Scrollbar( self, orient='horizontal', command=self.canvas.xview )
        self.canvas.configure( yscrollcommand=vbar.set, xscrollcommand=hbar.set )
        self.canvas.configure( scrollregion=(-500,-500,500,500) )
        
        hbar.grid(row=1, column=0, sticky="ew")
        vbar.grid(row=0, column=1, sticky="ns")
        self.canvas.grid(row=0, column=0, sticky='nswe')
        self.grid_rowconfigure( 0, weight=1 )
        self.grid_columnconfigure( 0, weight=1 )
        
        #self.root.bind( '<Configure>', self.resize )
        self.root.bind( '<Control-Key-i>', self.key_control_i )
        self.root.bind( '<Key-i>', self.key_i )
        self.root.bind( '<Control-Key-o>', self.key_control_o ) 
        self.root.bind( '<Control-Key-s>', self.key_control_s )
        self.root.bind( '<Control-Key-z>', self.key_control_z )
        self.root.bind( '<Control-Shift-Key-Z>', self.key_control_y )
        self.root.bind( '<Key-F1>', self.key_F1 )
        
        self.canvas.bind( '<ButtonPress-1>', self.left_mouse_down ) #left mouse down
        self.canvas.bind( '<ButtonRelease-1>', self.left_mouse_up ) #left mouse up
        self.canvas.bind( '<Motion>', self.mouse_move )
        self.canvas.bind( '<Key-Tab>', self.key_tab )
        self.canvas.bind( '<Key-Delete>', self.key_delete )
        self.canvas.bind( '<Enter>', self.mouse_enter )
        
        #self.canvas.pack( fill=tk.BOTH, expand=1 )

        self.display_help_text()
        
    def display_help_text( self ):
        txts = ['Press F1 to toggle help text.',
            'Drag left mouse button to create / edit lines.',
            'Click on lines to select them.',
            'Press DEL to delete selected lines.',
            'Press TAB to toggle line creation / editing.',
            'Press CTRL+z, CTRL+SHIFT+z for undo and redo.',
            'Press CTRL+o, CTRL+s to open and save file.',
            'CTRL+i loads background image. i will toggle image display.',
            'CTRL+Click adds control point and smooths the line.']

        #messagebox.showinfo( 'Help', txts )
        self.helptext = []
        for i in range(len(txts)):
            ht = self.canvas.create_text( ( 10, i*20 + 10 ), text=txts[i], fill='gray', anchor='nw' )
            self.helptext.append( ht )
            
        self.helpdisplayed = True
        
    def key_F1( self, event ):
        if self.helpdisplayed:
            self.helpdisplayed = False
            for ht in self.helptext:
                self.canvas.itemconfig( ht, state=tk.HIDDEN )
        else:
            self.helpdisplayed = True
            for ht in self.helptext:
                self.canvas.itemconfig( ht, state=tk.NORMAL )
            
    def left_mouse_down( self, event ):
        self.mousedown = True
        self.prevx, self.prevy = self.origx, self.origy = event.x, event.y
    
    def mouse_move( self, event ):
        if self.mousemode==1:
            if self.currentLine:
                self.currentLine.update_end( event.x, event.y )
            elif self.mousedown:
                line = Line( self, [self.origx, self.origy, event.x, event.y] )
                self.currentLine = line
                
        self.prevx, self.prevy = event.x, event.y
    
    def left_mouse_up( self, event ):
        self.mousedown = False
        if self.origx==event.x and self.origy==event.y:
            lineshape = self.canvas.find_withtag( tk.CURRENT )
            try:
                line = self.linesMap[lineshape[0]]
            except:
                line = None
            self.select_line( line )
        else:
            if self.mousemode==1:
                self.add_line( self.currentLine )
    
            self.currentLine = None
            
        self.prevx, self.prevy = event.x, event.y

    def add_line( self, line, fromFile = False ):
        self.lines.append( line )
        self.linesMap[line.shape] = line
        if not fromFile:
            self.undomanager.add( Line.LineAddAction( line ) )
            self.select_line( line )
        
    def select_line( self, line, undoable=True ):
        if self.selectedLine:
            self.selectedLine.deselect()
            
        if undoable:
            self.undomanager.add( Application.SelectAction( self, line, self.selectedLine ) )
            
        self.selectedLine = line
        if line:
            line.select()
        
    def key_delete( self, event ):
        if self.selectedLine:
            self.delete_line( self.selectedLine )
        
    def delete_line( self, line ):
        self.selectedLine.set_visible( False )
        self.undomanager.add( Application.DeleteAction( self.selectedLine ) )
        self.select_line( None, False )
        
    def key_tab( self, event ):
        self.toggle_mouse_mode()
    
    def toggle_mouse_mode(self):
        self.mousemode = 1 if self.mousemode == 2 else 2
        for line in self.lines:
            line.set_editable( self.mousemode==2 )
            
    def mouse_enter( self, event ):
        self.canvas.focus_set()
    
    def run(self):
        self.root.mainloop()

    def key_control_s( self, event ):
        #filename = asksaveasfilename(defaultextension='.txt')
        filename = 'test.txt'
        if filename != None:
            file = open(filename, 'w')
            self.save(file)
            file.close()
    
    def key_control_o( self, event ):
        #filename = askopenfilename()
        filename = 'test.txt'
        if filename != None:
            file = open(filename, 'r')
            self.load(file)
            file.close()
    
    def save(self, file):
        for line in self.lines:
            if line.visible:
                line.save(file)
                file.write('\n')
    
    def load(self, file):
        self.lines.clear()
        self.linesMap.clear()
        for readline in file:
            if readline.strip()=='':
                continue
            line = Line.load( self, readline.strip() )
            self.add_line( line, fromFile = True )
            
    def key_control_i(self, event):
        # filename = askopenfilename()
        filename = 'facemap.jpg'
        if filename != None:
            self.render_image(filename, (0,0))
    
    def key_i(self, event):
        if self.image_shape:
            if self.image_displayed:
                self.canvas.itemconfig( self.image_shape, state=tk.HIDDEN )
                self.image_displayed = False
            else:
                self.canvas.itemconfig( self.image_shape, state=tk.NORMAL )
                self.image_displayed = True
        
    def render_image(self, file, loc):
        image = Image.open(file)
        photo = ImageTk.PhotoImage(image)
        self.canvas.image = photo
        self.image_shape = self.canvas.create_image(loc, image = photo, anchor = tk.NW)
        self.canvas.tag_lower( self.image_shape ) # Moves to the bottom of the canvas stack.
        self.image_displayed = True
    
    # Undo management
    def key_control_z( self, event ):
        self.undomanager.undo()
        
    def key_control_y( self, event ):
        self.undomanager.redo()
    
    def is_edit_mode( self ):
        return self.mousemode == 2
        
app = Application(480, 480)
app.pack(fill="both", expand=True)
app.load( open('test.txt', 'r') )
app.run()

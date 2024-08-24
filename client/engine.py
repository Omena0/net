from pygame._sdl2 import Window as _Window
from types import FunctionType
from easing import get_easing
from threading import Thread
from copy import copy
import time as t
import pygame
pygame.init()

clock = pygame.time.Clock()


# Basic
running = True
root   = None
focus  = None

# Used events
usedEvents = [pygame.MOUSEBUTTONDOWN,pygame.MOUSEBUTTONUP,pygame.KEYDOWN,pygame.KEYUP,pygame.MOUSEMOTION,pygame.QUIT,pygame.VIDEORESIZE,pygame.WINDOWMAXIMIZED]

# Mouse pos
x = 0
y = 0

# Tabs
tab  = 0
tabs = 0

# Counters
frame = -1  # -1 cuz we increase before we process anything
a     = 0   # Counter used for testing

def nothing(*args, **kwargs):
    """Does nothing"""

### COMPONENTS ###

# Dummy parent class, might move some functions here.
class Component: ...

class Text(Component):
    def __init__(
            self,
            position,
            text,
            size,
            color=(255, 255, 255),
            bg_color = None,
            font=None
        ):
        
        self.parent = None
        
        # Style
        self.text:str = text
        self.size = size
        self.color = color
        self.bg_color = bg_color
        self.font = font
        
        # Position
        self.pos = position
        self.x = position[0]
        self.y = position[1]
        self.abs_pos = self.pos
        self.abs_x = self.x
        self.abs_y = self.y
        
        # Rendering
        self.layer = 0
        self.visible = True

    def setPos(self, x, y):
        self.pos = x, y
        self.x = x
        self.y = y
        self.abs_x = x + self.parent.abs_x
        self.abs_y = y + self.parent.abs_y
        self.abs_pos = self.abs_x, self.abs_y
        self.changed = True
        return self

    def render(self):
        if not self.changed: return
        blits = []
        font = pygame.font.SysFont(self.font, self.size)
        i = 0
        for segment in self.text.split('\n'):
            text = font.render(segment, True, self.color,self.bg_color)
            blits.append((text, (self.abs_x, self.abs_y+(self.size+3)*i)))
            if segment.strip() == '':
                i += 0.5
            else: i += 1
        root.disp.blits(blits)
        self.changed = False

    def add(self, parent, layer=0):
        self.layer = layer
        self.parent = parent
        self.setPos(self.x, self.y)
        parent.addChild(self)
        return self

class Button(Component):
    def __init__(
            self,
            position:tuple[int,int],
            width:int,
            height:int,
            text:str,
            size:int,
            action:FunctionType=nothing,
            color=(200, 200, 200),
            hover_color=(150, 150, 150),
            font_color=(255, 255, 255),
            corner_radius=10,
            font=None
        ):
        self.parent = None
        
        # Style
        self.text = text
        self.size = size
        self.width = width
        self.height = height
        self.action = action
        self.color = color
        self.hoverColor = hover_color
        self.font_color = font_color
        self.font = font
        self.hovered = False
        self.corner_radius = corner_radius
        
        # Position
        self.pos = position
        self.x = position[0]
        self.y = position[1]
        self.abs_pos = self.pos
        self.abs_x = self.x
        self.abs_y = self.y
        
        # Rendering
        self.layer = 0
        self.visible = True

    def setPos(self, x, y):
        self.pos = x, y
        self.x = x
        self.y = y
        self.abs_x = x + self.parent.abs_x
        self.abs_y = y + self.parent.abs_y
        self.abs_pos = self.abs_x, self.abs_y
        self.changed = True
        return self

    def checkHovered(self):
        global x,y
        self.hovered = (
            x in range(self.abs_x, self.abs_x + self.width)
            and y in range(self.abs_y, self.abs_y + self.height)
        )
        return self.hovered

    def render(self):
        if not self.changed: return
        color = self.color if not self.hovered else self.hoverColor
        pygame.draw.rect(
            root.disp,
            color,
            (self.abs_x, self.abs_y, self.width, self.height),
            0,
            self.corner_radius
        )
        font = pygame.font.SysFont(self.font, self.size)
        text = font.render(self.text, 1, self.font_color)
        x = self.abs_x + (self.width - text.get_width()) // 2
        y = self.abs_y + (self.height - text.get_height()) // 2
        root.disp.blit(text, (x, y))
        self.changed = False
        return self

    def add(self, parent, layer=0):
        self.layer = layer
        self.parent = parent
        self.setPos(self.x, self.y)
        parent.addChild(self)
        return self

    def event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and self.hovered:
            event.handled = True
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            event.handled = True
            self.action()

    def tick(self,frame):
        # CheckHovered every tick (performance)
        self.checkHovered()

class Checkbox(Component):
    def __init__(
            self,
            position,
            width,
            height,
            color=(56,56,56),
            hover_color=(70,70,70),
            check_color=(120,120,120),
            corner_radius=3,
            checked:bool=False,
            action:FunctionType=None
    ):
        self.parent = None
        self.action = action

        # Position
        self.pos = position
        self.x = position[0]
        self.y = position[1]
        self.abs_pos = self.pos
        self.abs_x = self.x
        self.abs_y = self.y
        
        # Style
        self.width = width
        self.height = height
        self.color = color
        self.hoverColor = hover_color
        self.checkColor = check_color
        self.corner_radius = corner_radius
        self.checked = checked
        self.hovered = False

        # Rendering
        self.layer = 0
        self.visible = True

    def setPos(self, x, y):
        self.pos = x, y
        self.x = x
        self.y = y
        self.abs_x = x + self.parent.abs_x
        self.abs_y = y + self.parent.abs_y
        self.abs_pos = self.abs_x, self.abs_y
        self.changed = True
        return self

    def toggle(self):
        self.checked = not self.checked
        if self.action:
            self.action(self.checked)

    def render(self):
        if not self.changed: return
        color = self.hoverColor if self.hovered else self.color
        
        pygame.draw.rect(
            root.disp,
            color,
            (self.abs_x, self.abs_y, self.width, self.height),
            0,
            self.corner_radius
        )

        if self.checked:
            pygame.draw.rect(
                root.disp,
                self.checkColor,
                (self.abs_x+self.width/8, self.abs_y+self.width/8, self.width-self.width/4+1, self.height-self.width/4+1),
                0,
                self.corner_radius
            )
        self.changed = False
        return self

    def checkHovered(self):
        global x,y
        self.hovered = (
            x in range(self.abs_x, self.abs_x + self.width)
            and y in range(self.abs_y, self.abs_y + self.height)
        )
        return self.hovered

    def add(self, parent, layer=0):
        self.layer = layer
        self.parent = parent
        self.setPos(self.x, self.y)
        parent.addChild(self)
        return self

    def tick(self,frame):
        # CheckHovered every second tick (performance)
        self.checkHovered()

    def event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            event.handled = True
            self.toggle()

class Textbox(Component):
    def __init__(
            self,
            position:tuple[int,int],
            width:int,
            height:int,
            size:int,
            color=(200, 200, 200),
            focus_color=(175,175,175),
            hover_color=(150,150,150),
            font_color =(255,255,255),
            corner_radius=8,
            font=None,
            text="",
            action=None,
        ):
        self.parent = None
        self.action = action
        
        # Style
        self.color = color
        self.focusColor = focus_color
        self.hoverColor = hover_color
        self.fontColor  = font_color
        self.corner_radius = corner_radius
        self.size = size
        self.width = width
        self.height = height
        self.font = font
        self.text = text
        self.hovered = False
        self.inactive = False
        
        # Extra
        self.repeat_delay = 10
        self.repeat_interval = 1
        self.repeat_timer = 0
        self.repeating = False
        self.pressed = ''
        self.pressed_old = ''
        
        # Position
        self.pos = position
        self.x = position[0]
        self.y = position[1]
        self.abs_pos = self.pos
        self.abs_x = self.x
        self.abs_y = self.y
        
        # Rendering
        self.layer = 0
        self.visible = True

    def setPos(self, x, y):
        self.pos = x, y
        self.x = x
        self.y = y
        
        self.abs_x = x + self.parent.abs_x
        self.abs_y = y + self.parent.abs_y
        self.abs_pos = self.abs_x, self.abs_y
        self.changed = True
        
        return self

    def checkHovered(self):
        global x,y
        self.hovered = x in range(self.abs_x, self.abs_x + self.width) and y in range(self.abs_y, self.abs_y + self.height)
        return self.hovered

    def render(self):
        global frame
        if not self.changed: return
        
        # Render
        color = self.color if self.hovered else self.hoverColor
        if focus == self: color = self.focusColor

        pygame.draw.rect(
            root.disp,
            color,
            pygame.Rect(
                self.abs_x,
                self.abs_y,
                self.width,
                self.height
            ),
            0,
            self.corner_radius
        )
        if self.text:
            font = pygame.font.SysFont(self.font, self.size)

            # Blinking cursor (i love this lmao)
            a = f'{self.text}|' if focus == self and frame//15 % 2 == 0 else self.text
            text = font.render(a, 1, self.fontColor)

            x = self.abs_x + 5
            y = self.abs_y + (self.height - self.size) // 2
            root.disp.blit(text, (x, y))
        self.changed = False

    def tick(self,frame):
        if self.inactive: return
        # CheckHovered every second tick (perf)
        self.checkHovered()
        # Key repeat timer
        if self.pressed: self.repeat_timer += 10
        if not self.repeating and self.repeat_timer > self.repeat_delay:
            self.repeating = True
            self.repeat_timer = 0

        if self.pressed != self.pressed_old:
            self.repeat_timer = 0
            self.pressed_old = self.pressed

        if self.repeating and self.repeat_timer > self.repeat_interval:
            if self.pressed == 'BACKSPACE':
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    words = self.text.split()
                    self.text = ' '.join(words[:-1]) if words else ''
                else:
                    self.text = self.text[:-1]
            else:
                self.text += self.pressed
            self.repeat_timer = 0
            
            # Autorepeat calls action :)
            if self.action:
                self.action(self.text)

        return self

    def add(self, parent, layer=0):
        self.layer = layer
        self.parent = parent
        self.setPos(self.x, self.y)
        parent.addChild(self)
        return self

    def event(self, event):
        global focus
        if self.inactive: return

        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            focus = self
            event.handled = True

        # Text input
        if event.type == pygame.KEYDOWN and focus == self:
            event.handled = True
            if focus == self:
                if event.key == pygame.K_BACKSPACE:
                    self.pressed = 'BACKSPACE'
                    if pygame.key.get_mods() & pygame.KMOD_CTRL:
                        words = self.text.split()
                        self.text = ' '.join(words[:-1]) if words else ''
                    else:
                        self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                    self.pressed = event.unicode

                if self.action:
                    self.action(self.text)

        elif event.type == pygame.KEYUP and focus == self:
            event.handled = True
            self.pressed = ''
            self.repeating = False
            self.repeat_timer = 0

class Image(Component):
    def __init__(
            self,
            position,
            image_path,
            width=None,
            height=None
        ):
        self.parent = None

        # Position
        self.pos = position
        self.x = position[0]
        self.y = position[1]
        self.width = width
        self.height = height
        self.abs_pos = self.pos
        self.abs_x = self.x
        self.abs_y = self.y

        # Image
        self.image_path = image_path
        self.update_image()

        # Rendering
        self.layer = 0
        self.visible = True

    def setPos(self, x, y):
        self.pos = x, y
        self.x = x
        self.y = y
        
        self.abs_x = x + self.parent.abs_x
        self.abs_y = y + self.parent.abs_y
        self.abs_pos = self.abs_x, self.abs_y
        self.changed = True
        return self

    def update_image(self):
        self.image = pygame.image.load(self.image_path)
        if not (self.width and self.height): return
        self.image = pygame.transform.smoothscale(self.image,(self.width,self.height))

    def render(self):
        if not self.changed: return
        root.disp.blit(self.image, (self.abs_x, self.abs_y))
        self.changed = False
        return self

    def event(self,event):
        if event.type in (pygame.VIDEORESIZE,pygame.WINDOWMAXIMIZED):
            self.update_image()
    
    def add(self, parent, layer=0):
        self.layer = layer
        self.parent = parent
        self.setPos(self.x, self.y)
        parent.addChild(self)
        return self

class Progressbar(Component):
    def __init__(
            self,
            position,
            width,
            height,
            color=(30,85,230),
            border_color=(56,56,56),
            border_radius=4,
            corner_radius=4,
            speed=0
        ):
        
        self.parent = None
        
        # Style
        self.color = color
        self.borderColor = border_color
        self.borderRadius = border_radius
        self.corner_radius = corner_radius
        
        # Position
        self.pos = position
        self.x = position[0]
        self.y = position[1]
        self.abs_pos = self.pos
        self.abs_x = self.x
        self.abs_y = self.y
        self.width = width
        self.height = height
        
        # Rendering
        self.layer = 0
        self.visible = True
        
        # Progress
        self.progress   = 0              # Progressbar state (0-1)
        self.max        = 1              # Max (0-1)
        self.completed  = 0              # Current (0-1)
        self.speed      = speed/5000    # How much to increase/tick
        self.started    = False          # Should we increase?
        self.halted     = False          # Should we increase? (if set progress < current progress)
        self.shouldHalt = True           # Should halt (set externally)
        self.realProg   = 0              # The last progress value sent to us
        self.tolerance  = 0.3            # Largest difference between prog (smoothed) and realProg can be before we halt

    def setPos(self, x, y):
        self.pos = x, y
        self.x = x
        self.y = y
        self.abs_x = x + self.parent.abs_x
        self.abs_y = y + self.parent.abs_y
        self.abs_pos = self.abs_x, self.abs_y
        self.changed = True
        return self

    def tick(self,frame):
        global a

        if self.started and not self.halted:
            # Dynamically adjust the speed of the progress bar depending on
            # how far away we are from the last datapoint (realProg)
            # Im really fucking proud of making a better Progressbar than tkinter lmao
            speed = round(self.speed - max(self.progress-self.realProg,0)/100,5)

            self.progress += speed

        #print(f'Speed: {speed}')
        #print(f'Smooth: {self.progress} Real: {self.realProg}')
        
        # Run this shit to check if we should halt (for next frame)
        self.setProgress(self.completed,self.max)

    def render(self):
        if not self.changed: return
        
        pygame.draw.rect(
            root.disp,
            self.borderColor,
            pygame.Rect(self.abs_x,self.abs_y,self.width,self.height),
            self.borderRadius,
            self.corner_radius
        )
        pygame.draw.rect(
            root.disp,
            self.color,
            pygame.Rect(
                self.abs_x+self.borderRadius,
                self.abs_y+self.borderRadius,
                min(max((self.width-self.borderRadius*2)*(self.progress),0),self.width-self.borderRadius*2),
                self.height-self.borderRadius*2
            ),
            0,
            self.corner_radius//2
        )
        
        self.changed = False
        return self
    
    def start(self):
        self.started = True
        
    def stop(self):
        self.started = False
    
    def setProgress(self,completed,max_=100):
        self.max = max_
        self.completed = completed
        
        progress = (self.completed/self.max)

        self.halted = self.progress > progress+self.tolerance and self.shouldHalt
        self.realProg = progress
        
        # only lets you decrease progress if not started.
        self.progress = round(max(self.progress, progress) if self.started else progress,5)

    def add(self, parent, layer=0):
        self.layer = layer
        self.parent = parent
        self.setPos(self.x, self.y)
        parent.addChild(self)
        return self

class Slider(Component):
    def __init__(
            self,
            position,
            width,
            height,
            color=(30, 85, 230),
            handle_color=(56, 56, 56),
            handle_radius=8,
            track_color=(200, 200, 200),
            track_height=4,
            action:FunctionType=None
    ):
        self.parent = None
        self.hovered = False

        # Style
        self.color = color
        self.handleColor = handle_color
        self.handleRadius = handle_radius
        self.trackColor = track_color
        self.trackHeight = track_height

        # Position
        self.pos = position
        self.x = position[0]
        self.y = position[1]
        self.abs_pos = self.pos
        self.abs_x = self.x
        self.abs_y = self.y
        self.width = width
        self.height = height

        # Value
        self.value = 0
        self.pressed = False
        self.action = action
        
        # Rendering
        self.layer = 0
        self.visible = True

    def setPos(self, x, y):
        self.pos = x, y
        self.x = x
        self.y = y
        self.abs_x = x + self.parent.abs_x
        self.abs_y = y + self.parent.abs_y
        self.abs_pos = self.abs_x, self.abs_y
        self.changed = True
        return self

    def render(self):
        if not self.changed: return

        # Draw track
        track_y = self.abs_y + (self.height - self.trackHeight) // 2
        pygame.draw.rect(
            root.disp,
            self.trackColor,
            pygame.Rect(self.abs_x, track_y, self.width, self.trackHeight)
        )

        # Calculate handle position
        handle_x = self.abs_x + (self.width - self.handleRadius * 2) * ((self.value - 0) / (1 - 0))

        # Draw handle
        handle_y = self.abs_y + (self.height - self.handleRadius * 2) // 2
        pygame.draw.circle(
            root.disp,
            self.handleColor,
            (int(handle_x + self.handleRadius), int(handle_y + self.handleRadius)),
            self.handleRadius
        )

        self.changed = False
        return self

    def checkHovered(self):
        global x,y
        self.hovered = (
            x in range(self.abs_x, self.abs_x + self.width)
            and y in range(self.abs_y, self.abs_y + self.height)
        )
        return self.hovered

    def setValue(self, value):
        self.value = max(0, min(value, 1))
        if self.action:
            self.action(self.value)

    def add(self, parent, layer=0):
        self.layer = layer
        self.parent = parent
        self.setPos(self.x, self.y)
        parent.addChild(self)
        return self

    def tick(self,frame):
        # CheckHovered every second tick (performance)
        self.checkHovered()
        # Track movement
        if self.pressed:
            x = pygame.mouse.get_pos()[0]
            self.setValue((x-self.abs_x)/self.width)

    def event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered:
                event.handled = True
                self.pressed = True

        elif event.type == pygame.MOUSEBUTTONUP:
            event.handled = True
            self.pressed = False

class Area(Component):
    def __init__(
            self,
            position,
            width,
            height,
            color=(255, 255, 255),
            corner_radius=15
        ):
        
        self.parent = None
        
        # Style
        self.color = color
        self.corner_radius = corner_radius
        
        # Position
        self.pos = position
        self.x = position[0]
        self.y = position[1]
        self.abs_pos = self.pos
        self.abs_x   = self.x
        self.abs_y   = self.y
        self.width   = width
        self.height  = height
        
        # Rendering
        self.layer = 0
        self.visible = True

    def setPos(self, x, y):
        self.pos = x, y
        self.x = x
        self.y = y
        self.abs_x = x + self.parent.abs_x
        self.abs_y = y + self.parent.abs_y
        self.abs_pos = self.abs_x, self.abs_y
        self.changed = True
        return self

    def render(self):
        if not self.changed: return
        
        pygame.draw.rect(
            root.disp,
            self.color,
            pygame.Rect(
                self.abs_x,self.abs_y,self.width,self.height
            ),
            0,
            self.corner_radius
        )
        self.changed = False
        return self

    def add(self, parent, layer=0):
        self.layer = layer
        self.parent = parent
        self.setPos(self.x, self.y)
        parent.addChild(self)
        return self

class Line(Component):
    def __init__(
            self,
            from_:tuple[int,int],
            to:tuple[int,int],
            color=(255, 255, 255),
            width=5
        ):
        
        self.parent = None
        
        # Style
        self.color = color
        self.width = width
        
        # Position
        self.from_ = from_
        self.to    = to
        
        ## Shit that might have to exist for it to work smh
        self.x       = from_[0]
        self.y       = from_[1]
        self.abs_pos = from_
        self.abs_x   = from_[0]
        self.abs_y   = from_[1]
        
        # Rendering
        self.layer = 0      # Set in .add()
        self.visible = True

    def setPos(self, x, y):
        self.x = x
        self.y = y
        self.pos = self.x,self.y
        self.abs_x = self.x + self.parent.abs_x
        self.abs_y = self.y + self.parent.abs_y
        self.abs_pos = self.abs_x, self.abs_y
        self.changed = True
        return self

    def render(self):
        if not self.changed: return
        pygame.draw.line(
            root.disp,
            self.color,
            self.from_,
            self.to,
            self.width
        )
        self.changed = False
        return self

    def add(self, parent, layer=0):
        self.layer = layer
        self.parent = parent
        self.setPos(self.x, self.y)
        parent.addChild(self)
        return self

class Titlebar(Component):
    def __init__(
            self,
            text:str,
            height:int = 25,
            color = (40,40,40),
            border_radius:int = 5,
            size = 25,
            text_position = None
        ):
        self.text = text
        self.width = root.disp.get_width()
        self.height = height
        self.color = color
        self.border_radius = border_radius
        
        # Pos
        self.x = 0
        self.y = 0
        self.abs_x = 0
        self.abs_y = 0
        
        if text_position is None:
            text_position = (5,height//2-size//3)
        self.textPos = text_position
        self.dragPoint = (0,0)
        self.dragging = False
        
        # Style
        self.size = size
        self.visible = True
        self.changed = True
        
        # Close button
        self.close = Button(
            (root.disp.get_width()-25,0),
            25,
            25,
            'X',
            25,
            lambda: pygame.quit(),
            color=(40,40,40),
            hover_color=(175,60,60),
            corner_radius=5
        ).add(root,30)
    
    def setPos(self, x, y):
        """Does nothing because this is a title bar bruh"""
    
    def render(self):
        if not self.changed: return
        # Bar
        pygame.draw.rect(
            root.disp,
            self.color,
            (0,0,root.disp.get_size()[0],self.height),
            0,
            -1,
            self.border_radius,
            self.border_radius
        )
        
        # Text
        font = pygame.font.SysFont(None,self.size)
        t = font.render(self.text,1,(255,255,255))
        root.disp.blit(t,self.textPos)
        
        # Close button in __init__
        
        self.changed = False
    
    def tick(self,frame):
        self.checkHovered()
        if pygame.mouse.get_pressed()[0] and self.dragging:
            pos = root.window.position
            root.window.position = (pos[0] + x - self.dragPoint[0]), (pos[1] + y - self.dragPoint[1])
        
    def checkHovered(self):
        self.hovered = (
            x in range(self.abs_x, self.abs_x + self.width)
            and y in range(self.abs_y, self.abs_y + self.height)
        )
        return self.hovered
    
    def add(self, parent, layer=0):
        self.layer = layer
        self.parent = parent
        self.setPos(self.x, self.y)
        parent.addChild(self)
        return self

    def event(self, event):
        global focus
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            self.dragPoint = event.dict['pos']
            self.dragging = True
            focus = self
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        
        elif event.type in (pygame.VIDEORESIZE,pygame.WINDOWMAXIMIZED):
            self.width = root.disp.get_width()
            self.close.setPos(self.width-27,self.close.y)

class Window(Component):
    def __init__(
            self,
            position:tuple[int,int],
            width:int,
            height:int,
            title:str,
            tb_height:int=25,
            corner_radius=5,
            color=(45, 45, 45),
            bg_focused_color=(50, 50, 50),
            font=None,
            on_quit:FunctionType=nothing
        ):
        self.parent = None
        self.children = []
        self.onQuit = on_quit
        
        # Style
        self.title = title
        self.width = width
        self.height = height
        self.tb_height = tb_height
        self.corner_radius = corner_radius
        self.bgColor = color
        self.bgFocusedColor = bg_focused_color
        self.font = font
        self.hovered = False
        
        self.dragPoint = 0,0
        self.dragging = False
        self.nextPos = None
        
        # Position
        self.pos = position
        self.x = position[0]
        self.y = position[1]
        self.abs_pos = self.pos
        self.abs_x = self.x
        self.abs_y = self.y
        
        # Rendering
        self.layer = 0
        self.visible = True
        self.quit_ = False
        
        # Close button
        self.close = Button(
            (self.width-27,3-self.tb_height),
            25,
            20,
            'X',
            25,
            self.quit,
            color=(40,40,40),
            hover_color=(175,60,60),
            corner_radius=5
        ).add(self,self.layer)

    def quit(self):
        self.parent.children.remove(self)
        root.update_all()
        self.quit_ = True
        self.onQuit()
    
    def setPos(self, x, y):
        self.pos = x, y
        self.x = x
        self.y = y
        self.abs_x = x + self.parent.abs_x
        self.abs_y = y + self.parent.abs_y
        self.abs_pos = self.abs_x, self.abs_y
        self.changed = True
        for child in self.children:
            child.setPos(child.x,child.y)
        return self

    def checkHovered(self):
        self.hovered = (
            x in range(self.abs_x, self.abs_x + self.width)
            and y in range(self.abs_y-self.tb_height, self.abs_y-self.tb_height + self.height+self.tb_height)
        )
        return self.hovered

    def addChild(self, child):
        child.setPos(child.x,child.y)
        self.children.append(child)
        self.children = sorted(self.children,key=lambda x: x.layer)

    def render(self):
        if self.changed:
            ## Title bar
            color = self.bgFocusedColor if focus == self else self.bgColor

            # Rect
            pygame.draw.rect(
                root.disp,
                (40,40,40),
                (self.abs_x,self.abs_y-self.tb_height,self.width,self.tb_height),
                border_top_left_radius=self.corner_radius,
                border_top_right_radius=self.corner_radius
            )

            # Text
            font:pygame.font.Font = pygame.font.SysFont(self.font,25)
            t = font.render(self.title,1,(255,255,255))
            root.disp.blit(
                t,
                (self.abs_x+10,self.abs_y+5-self.tb_height)
            )

            ## Window background
            # Rect
            pygame.draw.rect(
                root.disp,
                color,
                (self.abs_x,self.abs_y,self.width,self.height),
                border_bottom_left_radius=self.corner_radius,
                border_bottom_right_radius=self.corner_radius
            )
        
        # Dragging rectangle
        if self.dragging and not drag_high_quality:
            pygame.draw.rect(
                root.disp,
                (100,100,100),
                (x-self.dragPoint[0],y-self.dragPoint[1]-self.tb_height,self.width,self.height+self.tb_height),
                2,
                self.corner_radius
            )
        
        for child in self.children:
            if child.visible and child.changed:
                child.render()
        
        self.changed = False

    def add(self, parent, layer=0):
        self.layer = layer
        self.parent = parent
        self.setPos(self.x, self.y)
        parent.addChild(self)
        return self

    def event(self, event):
        global focus

        for child in self.children:
            if event.handled: return
            if hasattr(child,'event') and child.visible:
                child.event(event)
        
        if event.handled: return

        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            event.handled = True
            self.dragPoint = event.dict['pos'][0]-self.abs_x, event.dict['pos'][1]-self.abs_y
            if self.dragPoint[1] < 0:
                self.dragging = True
            focus = self
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            if self.nextPos:
                self.setPos(*self.nextPos)
                for child in self.children:
                    child.setPos(child.x,child.y)

    def tick(self,frame):
        # CheckHovered every tick (performance)
        self.checkHovered()
        if focus == self:
            self.parent.children.remove(self)
            self.parent.children.append(self)
        
        if self.dragging:
            p = self.parent
            px = 0
            py = 0
            while True:
                px += p.x
                py += p.y
                if hasattr(p,'parent'):
                    p = p.parent
                else: break

            self.nextPos = (x-self.dragPoint[0]-px,y-self.dragPoint[1]-py)
            if drag_high_quality: self.setPos(*self.nextPos)

        for child in self.children:
            if hasattr(child,'tick'):
                child.tick(frame)

    def remove(self,child):
        self.children.remove(object)

class Tab(Component):
    def __init__(self):
        global tab, tabs
        self.children = []
        self.parent = None
        self.id = tabs
        tabs += 1
        
        # Position
        self.x = 0
        self.y = 0
        self.abs_x = 0
        self.abs_y = 0
        self.width = root.width
        self.height = root.height
        
        # Rendering
        self.visible = False
        self.layer = 100

    def event(self, event):
        event.handled = False
        for child in reversed(self.children):
            if event.handled: break
            if hasattr(child,'event') and child.visible:
                child.event(event)

    def addChild(self, child):
        child.setPos(child.x,child.y)
        self.children.append(child)
        self.children = sorted(self.children,key=lambda x: x.layer)

    def tick(self,frame):
        global tab, tabs
        # Set visibility
        self.visible = (tab == self.id)
        if not self.visible: return
        
        for child in self.children:
            if hasattr(child,'tick'):
                child.tick(frame)
    
    def setPos(self, x, y):
        self.pos = x, y
        self.x = x
        self.y = y
        self.abs_x = x + self.parent.abs_x
        self.abs_y = y + self.parent.abs_y
        self.abs_pos = self.abs_x, self.abs_y
        self.changed = True
        for child in self.children:
            child.setPos(child.x,child.y)
        return self

    def render(self): 
        for child in self.children:
            if child.visible:
                child.render()
        self.changed = False
        return self

    def add(self, parent, layer=0):
        self.layer = layer
        self.parent = parent
        self.setPos(self.x, self.y)
        parent.addChild(self)
        return self

class Frame(Component):
    def __init__(
        self,
        position,
        width,
        height
    ):
        self.children = []
        self.parent = None
        
        # Position
        self.pos = position
        self.x = position[0]
        self.y = position[1]
        self.abs_pos = self.pos
        self.abs_x = self.x
        self.abs_y = self.y
        self.pos2 = width, height
        self.width = width
        self.height = height
        
        # Rendering
        self.layer = 0
        self.visible = True

    def setPos(self, x, y):
        self.pos = x, y
        self.x = x
        self.y = y
        self.abs_x = x + self.parent.abs_x
        self.abs_y = y + self.parent.abs_y
        self.abs_pos = self.abs_x, self.abs_y
        self.changed = True
        for child in self.children:
            child.setPos(child.x,child.y)
        return self

    def event(self, event):
        event.handled = False
        for child in reversed(self.children):
            if event.handled: break
            if hasattr(child,'event') and child.visible:
                child.event(event)

    def addChild(self, child):
        child.setPos(child.x,child.y)
        self.children.append(child)
        self.children = sorted(self.children,key=lambda x: x.layer)

    def tick(self,frame):
        for child in self.children:
            if hasattr(child,'tick'):
                child.tick(frame)
    
    def render(self):
        for child in self.children:
            if child.visible and child.changed:
                child.render()
        self.changed = False
        return self

    def add(self, parent, layer=0):
        self.layer = layer
        self.parent = parent
        self.setPos(self.x, self.y)
        parent.addChild(self)
        return self

    def remove(self, object):
        self.children.remove(object)

class Root:
    def __init__(
            self,
            title="",
            bg=(100, 100, 100),
            res=(600, 500)
        ):
        pygame.init()
        pygame.threads.init(2)

        global root
        self.setTitle(title)
        self._title = f'{self.title} | FPS: {clock.get_fps()//1}'
        self.res = res
        self.children = []
        self._customEventListeners = set()
        self._customTickListeners = set()
        self._customFrameListeners = set()
        
        # Style
        self.bgColor = bg
        self.width = self.res[0]
        self.height = self.res[1]
        self.changed = True
        
        self._update_timer = 0
        
        # Position (just so parent.x / parent.abs_x works)
        self.x = 0
        self.y = 0
        self.abs_y = 0
        self.abs_x = 0
        
        root = self

    def setTitle(self, title):
        self.title = title
        return self

    def setTab(self,tabId):
        global tab
        tab = tabId

    def show(self, resizable=True, extraFlag=0):
        flags = (pygame.RESIZABLE if resizable else 0) | extraFlag
        
        self.disp = pygame.display.set_mode(
            self.res, vsync=1, flags=flags
        )
        self.window = _Window.from_display_module()
        
        self.disp.fill(self.bgColor)
        
        return self
    
    def setPos(self, x, y):
        self.pos = x, y
        self.x = x
        self.y = y
        self.abs_x = x
        self.abs_y = y
        self.abs_pos = self.x, self.y
        return self

    def addChild(self, child):
        child.setPos(child.x,child.y)
        self.children.append(child)
        self.children = sorted(self.children,key=lambda x: x.layer)

    def tick(self,frame):
        self.update_all()
        for child in self.children:
            if hasattr(child,'tick') and (child.visible or isinstance(child,Tab)):
                child.tick(frame)
        if self._customTickListeners:
            for listener in self._customTickListeners:
                listener(frame)

    def render(self):
        self._title = f'{self.title} | FPS: {clock.get_fps()//1}'
        pygame.display.set_caption(self._title)
        for child in self.children:
            if child.visible:
                child.render()
        if self._customFrameListeners:
            for listener in self._customFrameListeners:
                listener()

    def remove(self,object):
        self.children.remove(object)
        self.update_all()
        del object

    def event(self, event:pygame.event.Event):
        global x, y, focus, a

        if event.type == pygame.VIDEORESIZE:
            self.res = event.size
            self.disp = pygame.display.set_mode(
                self.res, flags=self.disp.get_flags()
            )
            self.update_all()

        elif event.type == pygame.MOUSEMOTION:
            x,y = event.dict['pos']

            if a != 10:
                a += 1
                return
            else:
                a = 0

        event.handled = False
        for child in reversed(self.children):
            if not (hasattr(child,'event') and child.visible):
                continue

            try: event.dict.pop('window')
            except: ...

            if debug_events: print(f'Child name: {child.__class__.__name__}\nEvent Type: {event.type}\nEvent: {event.dict}\nHandled: {event.handled}\n')
            if event.handled: break
            child.event(event)
        
        if self._customEventListeners:
            for listener in self._customEventListeners:
                listener(event)

    def addFrameListener(self,listener:FunctionType):
        self._customFrameListeners.add(listener)

    def addEventListener(self,listener:FunctionType):
        self._customEventListeners.add(listener)

    def addTickListener(self,listener:FunctionType):
        self._customTickListeners.add(listener)

    def update_all(self):
        global count
        count = 0
        def update(object):
            global count
            object.changed = True
            if hasattr(object,'children'):
                for child in object.children:
                    update(child)
                    count += 1

        update(self)

    def wait_for_frame(self):
        global frame
        f = copy(frame)
        while f == frame: t.sleep(0.001)


def update():
    global frame, root, dt, running
    try:
        frame += 1
        if frame % 10 == 0:
            root.tick(frame)
        root.render()
        for event in pygame.event.get(usedEvents):
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()

            root.event(event)
        
        if not running: return
        dt = clock.tick(120)
        
        pygame.display.flip()
        return root
    except pygame.error as e:
        running = False
        if e == 'display surface quit':
            return
        else:
            print(e)
            if debug: raise e
        return

    except Exception as e:
        print(e)
        if debug:
            running = False
            raise e
        return

### ANIMATIONS ###

class Animation:
    def __init__(
            self,
            component:Component,
            length,
            endPos,
            easing,
            ease_in=True,
            ease_out=True
        ):
        self.component = component
        self.length = length
        self.startPos = copy(component.pos)
        self.endPos = endPos
        self.easing = easing
        
        self.easer = Easer(self.length,get_easing(easing,ease_in,ease_out))
    
    def start(self):
        Thread(target=self.start_blocking).start()
    
    def start_blocking(self):
        print(self.startPos,self.endPos)
        for i in self.easer:
            try: i = next(i)+0.0001
            except StopIteration: break


            x = abs(self.startPos[0] - abs(self.endPos[0] - self.startPos[0]) * i)

            y = abs(self.startPos[1] - abs(self.endPos[1] - self.startPos[1]) * i)
                
            self.component.setPos(round(x),round(y))
            if not running: break
            t.sleep(1/120)

class Easer:
    def __init__(self,length:int,easing_function:FunctionType):
        self.frame = -1
        self.length = length
        self.ease = easing_function
    
    def __len__(self):
        return self.length
    
    def __iter__(self):
        return self
    
    def __next__(self):
        self.frame += 1
        if self.frame > self.length: return
        yield self.ease(self.frame/self.length)

### LAYOUT MANAGER ###


class LayoutManager():
    def __init__(self,x,y,width,height,padding):
        self.x = x
        self.y = y
        self.width = width - padding
        self.height = height - padding
        self.padding = padding
        self.setPos(x+padding,y+padding)
        self.screen_width = root.width
        self.screen_height = root.height
        root.addEventListener(self.event)

    def setPos(self,x,y):
        self.x = x
        self.y = y
        if hasattr(self,'frame'): self.frame.setPos(x,y)

    def add(self,parent,layer=1):
        self.parent = parent
        self.layer  = layer
        return self

    def __enter__(self):
        global root
        self.old_root = root
        root = Frame((self.x,self.y),self.width,self.height).add(self.parent,self.layer)
        root.addEventListener = self.old_root.addEventListener
        self.frame = root

    def __exit__(self, *_):
        global root
        root = self.old_root
        self.update()
    
    def event(self,event):
        if event.type == pygame.VIDEORESIZE:
            self.width += event.dict['w'] - self.screen_width
            self.height += event.dict['h'] - self.screen_height
            self.frame.width = abs(self.width)
            self.frame.height = abs(self.height)

            self.screen_width = event.dict['w']
            self.screen_height = event.dict['h']
            self.update()
            root.update_all()

    def update(self):
        totalX = 0
        totalY = [0 for _ in range(self.screen_height)]
        for i,child in enumerate(self.frame.children):
            if not hasattr(child,'orig_x'): child.orig_x = child.x
            if not hasattr(child,'orig_y'): child.orig_y = child.y
            totalX += child.orig_x
            totalY[i] += child.orig_y
        
        x = 0
        y = 0
        for i,child in enumerate(self.frame.children):

            child.width  = abs(self.frame.width /(totalX   /(child.orig_x))-self.padding)
            child.height = abs(self.frame.height/(totalY[i]/(child.orig_y))-self.padding)

            print(f'{str(child):50}: {round(x):4}, {round(y):4} - {round(child.width):4}, {round(child.height):4}')

            child.setPos(abs(round(x)),abs(round(y)))
            x += child.width + self.padding



# Raise any exception caught
debug = True

# Display event debug information
debug_events = False

# Makes the dragging thing a rectangle kinda like in windows with the setting off
drag_high_quality = False

def mainloop():
    global running
    running = True
    while update() and running: ...

if __name__ == "__main__":
    import main

import pygame
from typing import Callable
pygame.init()
pygame.threads.init(2)

clock = pygame.time.Clock()


# Basic
running = True
root   = None
focus  = None

# Used events
usedEvents = [pygame.MOUSEBUTTONDOWN,pygame.KEYDOWN,pygame.KEYUP,pygame.MOUSEMOTION,pygame.QUIT,pygame.VIDEORESIZE]

# Mouse pos
x = 0
y = 0

# Tabs
tab  = 0
tabs = 0

# Counters
frame = -1  # -1 cuz we increase before we process anything
a     = 0   # Counter used for testing

def nothing():
    """Does nothing"""

class Text:
    def __init__(
            self,
            position,
            text,
            size,
            color=(255, 255, 255),
            font='Roboto'
        ):
        
        self.parent = None
        
        # Style
        self.text:str = text
        self.size = size
        self.color = color
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
        return self

    def render(self):
        if not self.visible: return
        font = pygame.font.SysFont(self.font, self.size)
        text = font.render(self.text, 1, self.color)
        root.disp.blit(text, (self.abs_x, self.abs_y))

    def add(self, parent, layer=0):
        self.layer = layer
        self.parent = parent
        self.setPos(self.x, self.y)
        parent.addChild(self)
        return self

class Button:
    def __init__(
            self,
            position:tuple[int,int],
            width:int,
            height:int,
            text:str,
            size:int,
            action:Callable=nothing,
            color=(200, 200, 200),
            hover_color=(150, 150, 150),
            font_color=(255, 255, 255),
            corner_radius=10,
            font='Roboto'
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
        return self

    def checkHovered(self):
        global x,y
        self.hovered = (
            x in range(self.abs_x, self.abs_x + self.width)
            and y in range(self.abs_y, self.abs_y + self.height)
        )
        return self.hovered

    def render(self):
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
        return self

    def add(self, parent, layer=0):
        self.layer = layer
        self.parent = parent
        self.setPos(self.x, self.y)
        parent.addChild(self)
        return self

    def event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            self.action()

    def tick(self,frame):
        # CheckHovered every second frame (performance)
        self.checkHovered()

class Checkbox:
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
            action:Callable=None
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
        return self

    def toggle(self):
        self.checked = not self.checked
        if self.action:
            self.action(self.checked)

    def render(self):
        

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
            self.toggle()

class Textbox:
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
            font="Roboto",
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
        
        # Extra
        self.repeat_delay = 20
        self.repeat_interval = 2
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
        
        return self

    def checkHovered(self):
        global x,y
        self.hovered = x in range(self.abs_x, self.abs_x + self.width) and y in range(self.abs_y, self.abs_y + self.height)
        return self.hovered

    def render(self):
        global frame
        
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
            a = f'{self.text}|' if focus == self and frame//20 % 2 == 0 else self.text
            text = font.render(a, 1, self.fontColor)

            x = self.abs_x + 5
            y = self.abs_y + (self.height - text.get_height()) // 2
            root.disp.blit(text, (x, y))

    def tick(self,frame):
        # CheckHovered every second tick (perf)
        self.checkHovered()
        # Key repeat timer
        if self.pressed: self.repeat_timer += 1
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

        # Text input
        if event.type == pygame.KEYDOWN:
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

        elif event.type == pygame.KEYUP:
            if focus == self:
                self.pressed = ''
                self.repeating = False
                self.repeat_timer = 0

        # Set focus
        if event.type == pygame.MOUSEBUTTONDOWN:
            focus = self if self.hovered else None

class Image:
    def __init__(
            self,
            position,
            image_path
        ):
        self.parent = None

        # Position
        self.pos = position
        self.x = position[0]
        self.y = position[1]
        self.abs_pos = self.pos
        self.abs_x = self.x
        self.abs_y = self.y

        # Image
        self.image = pygame.image.load(image_path)

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
        return self

    def render(self):
        
        root.disp.blit(self.image, (self.abs_x, self.abs_y))
        return self

    def add(self, parent, layer=0):
        self.layer = layer
        self.parent = parent
        self.setPos(self.x, self.y)
        parent.addChild(self)
        return self

class Progressbar:
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

class Slider:
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
            action:Callable=None
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
        return self

    def render(self):
        if not self.visible:
            return self

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
                self.pressed = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.pressed = False

class Area:
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
        return self

    def render(self):
        
        pygame.draw.rect(
            root.disp,
            self.color,
            pygame.Rect(
                self.abs_x,self.abs_y,self.width,self.height
            ),
            0,
            self.corner_radius
        )
        return self

    def add(self, parent, layer=0):
        self.layer = layer
        self.parent = parent
        self.setPos(self.x, self.y)
        parent.addChild(self)
        return self

class Line:
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
        return self

    def render(self):
        pygame.draw.line(
            root.disp,
            self.color,
            self.from_,
            self.to,
            self.width
        )
        return self

    def add(self, parent, layer=0):
        self.layer = layer
        self.parent = parent
        self.setPos(self.x, self.y)
        parent.addChild(self)
        return self

class Tab:
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
        for child in self.children:
            if hasattr(child,'event') and child.visible:
                child.event(event)

    def addChild(self, child):
        child.setPos(child.x,child.y)
        if self.children:
            for i, c in enumerate(self.children):
                if child.layer <= c.layer:
                    self.children.insert(i, child)
                    break
            else:
                self.children.append(child)
        else:
            self.children.append(child)
        return self

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
        return self

    def render(self): 
        for child in self.children:
            if child.visible:
                child.render()
        return self

    def add(self, parent, layer=0):
        self.layer = layer
        self.parent = parent
        self.setPos(self.x, self.y)
        parent.addChild(self)
        return self

class Frame:
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
        return self

    def event(self, event):
        for child in self.children:
            if hasattr(child,'event') and child.visible:
                child.event(event)

    def addChild(self, child):
        x = max(child.x, self.x)
        x = min(child.x, self.x + self.width)
        y = max(child.y, self.y)
        y = min(child.y, self.y + self.height)
        child.setPos(x, y)
        if self.children:
            for i, c in enumerate(self.children):
                if child.layer <= c.layer:
                    self.children.insert(i, child)
                    break
            else:
                self.children.append(child)
        else:
            self.children.append(child)
        return self

    def tick(self,frame):
        for child in self.children:
            if hasattr(child,'tick'):
                child.tick(frame)
    
    def render(self):
        for child in self.children:
            if child.visible:
                child.render()
        return self

    def add(self, parent, layer=0):
        self.layer = layer
        self.parent = parent
        self.setPos(self.x, self.y)
        parent.addChild(self)
        return self

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
        self.res = res
        self.children = []
        
        # Style
        self.bgColor = bg
        self.width = self.res[0]
        self.height = self.res[1]
        
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

    def show(self, resizable=True):
        flags = pygame.SCALED | (pygame.RESIZABLE if resizable else 0)
        self.disp = pygame.display.set_mode(
            self.res, flags=flags
        )
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
        if self.children:
            for i, c in enumerate(self.children):
                if child.layer <= c.layer:
                    self.children.insert(i, child)
                    break
            else: self.children.append(child)
        else: self.children.append(child)

    def tick(self):
        global frame
        for child in self.children:
            if hasattr(child,'tick') and (child.visible or isinstance(child,Tab)):
                child.tick(frame)

    def render(self):
        pygame.display.set_caption(f'{self.title} | FPS: {clock.get_fps()//1}')
        self.disp.fill(self.bgColor)
        for child in self.children:
            if child.visible:
                child.render()
        pygame.display.flip()
        return self

    def remove(self,object):
        self.children.remove(object)
        del object

    def event(self, event:pygame.event.Event):
        global x, y
        
        if event.type == pygame.VIDEORESIZE:
            self.res = event.size
            self.disp = pygame.display.set_mode(
                self.res, flags=self.disp.get_flags()
            )
            return
        
        elif event.type == 1024:
            x,y = event.dict['pos']
            return

        for child in self.children:
            if hasattr(child,'event') and child.visible:
                child.event(event)



def update():
    global frame, eventCount, root
    try:
        frame += 1
        if frame %2 == 0: root.tick()
        root.render()
        for event in pygame.event.get(usedEvents):
            if event.type == pygame.QUIT:
                pygame.quit()
            root.event(event)
        clock.tick()
        return root
    except Exception as e:
        print(e)
        if debug: raise e
        return

debug = False

def mainloop():
    while update() and running: ...



if __name__ == "__main__":
    import test

# This is used to create a gui from a .ui file

import engine as ui
from typing import Any, Callable

scripts:dict[str,list[str]] = {} # "Script name": [Script code]
events:dict[str,list[str]]  = {} # "Event name":  [Script code]
objects:dict[str,Any]       = {} # "Object class": "Script name"

def init(r:Callable):
    global redirect
    redirect = r

def runScript(script:str):
    src = scripts[script]
    exec(src,globals(),locals())
    globals().update(locals())

def runEvent(event):
    if event not in events.keys():
        print(f'[ERROR] Event not found: {event}')
        return
    src = events[event]
    exec(src,globals(),locals())
    globals().update(locals())

def getLevel(expr:str) -> int:
    return expr.count('    ',0,expr.rfind('    ')+4)


def getAttrs(startline:int,source) -> dict:
    attr = {}
    level = getLevel(source[startline])
    for line,i in enumerate(source[startline:]):
        if getLevel(i) < level and i.strip() != '': break
        print(f'[ATTR]   {line+startline:>3} | {i}')
        i = i.strip()
        if '=' not in i: break
        key, value = i.split('=')
        key = key.strip()
        value = eval(value)
        attr[key] = value
    return attr

def getScript(startLine:int,source):
    script = ''
    for line,i in enumerate(source[startLine:]):
        if getLevel(i) == 0 and i.strip() != '': break
        print(f'[SCRIPT] {line+startLine:>3} | {i}')
        i = i.removeprefix('    ')
        script += f'\n{i}'
    return script

def parseExpr(line:int,source,parent=None):
    if line >= len(source): return
    if parent is None: parent = ui.root
    expr:str = source[line]
    level = getLevel(expr)
    lastLevel = getLevel(source[line-1])
    if level < lastLevel: return parseExpr(line+1,source,parent)
    
    print(f'[EXPR]   {line:>3} | {expr}')
    expr = expr.strip()
    
    if expr == '':
        return parseExpr(line+1,source,parent)

    if expr.startswith('//'):
        return parseExpr(line+1,source,parent)
    
    if expr.startswith('!'):
        if expr.startswith('!script'):
            script = getScript(line+1,source)
            scripts[expr.split(':')[1]] = script
            return parseExpr(line+script.count('\n')+1,source,parent)

        elif expr.startswith('!event'):
            script = getScript(line+1,source)
            events[expr.split(':')[1]] = script
            return parseExpr(line+script.count('\n')+1,source,parent)

    if expr.startswith('#'):
        class_ = None
        if ':' in expr:
            expr, class_ = expr.split(':')
        attr = getAttrs(line+1,source)
        if not attr:
            return parseExpr(line+1,source,parent)
        
        layer = 0
        if 'layer' in attr.keys(): layer = attr.pop('layer')
        if 'action' in attr.keys():
            s = attr['action']
            attr['action'] = lambda *_: runScript(s)
        
        if expr == '#root':
            if 'bg' not in attr.keys():
                attr['bg'] = (100,100,100)

            ui.root = ui.Root(title=attr['title'],bg=attr['bg'])
            if 'size' in attr.keys(): ui.root.res = attr['size']
            if 'resizable' in attr.keys(): ui.root.resizable = attr['resizable']
        
        elif expr == '#frame':
            frame = ui.Frame(**attr).add(parent)
            return parseExpr(line+len(attr)+1,source,frame)
        
        else:
            a = getattr(ui,expr.replace('#','').capitalize())(
                **attr
            ).add(parent,layer=layer)
            if class_:
                objects[class_] = a
        
    
        return parseExpr(line+len(attr)+1,source,parent)

    else:
        parseExpr(line+1,source,parent)


def render(src:str):
    global events, scripts
    ui.pygame.quit()
    events = {}
    scripts = {}
    ui.root = None

    source = src.splitlines()
    source.append('')
    source.append('')

    parseExpr(0,source)
    
    if not ui.root:
        print('[ERROR] "ui.root" Is not defined.')
        return
    
    runEvent('onLoad')

    ui.root.show(ui.root.resizable)
    ui.mainloop()
    runEvent('onUnload')



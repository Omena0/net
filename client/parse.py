# This is used to create a gui from a .ui file

from typing import Any
import engine as ui
import os

scripts:dict[str,list[str]] = {} # "Script name": [Script code]
events:dict[str,list[str]]  = {} # "Event name":  [Script code]
objects:dict[str,Any]       = {} # "Object class": "Script name"

def init(redirect_,get_page_,get_file_,get_from_dns_,addr_, url_):
    global redirect, get_page, get_file, get_from_dns, addr, url
    redirect = redirect_
    get_page = get_page_
    get_file = get_file_
    get_from_dns = get_from_dns_
    addr = addr_
    url = url_

def runScript(script:str):
    src = scripts[script]
    exec(src,globals(),locals())


def runEvent(event):
    if event not in events.keys():
        #print(f'[ERROR] Event not found: {event}')
        return
    src = events[event]
    exec(src,globals(),locals())
    globals().update(locals())

def getLevel(expr:str) -> int:
    return expr.count('    ',0,expr.rfind('    ')+4)

def getAttrs(startLine:int,source) -> dict:
    attr = {}
    level = getLevel(source[startLine])
    for line,i in enumerate(source[startLine:]):
        if getLevel(i) < level and i.strip() != '': break
        if display_src: print(f'[ATTR]   {line+startLine:>3} | {i}')
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
        if display_src: print(f'[SCRIPT] {line+startLine:>3} | {i}')
        i = i.removeprefix('    ')
        script += f'\n{i}'
    return script

def parseExpr(line:int,source,parent=None):
    global titlebar

    if line >= len(source): return

    if parent is None:
        parent = ui.root

    expr:str = source[line]
    level = getLevel(expr)
    lastLevel = getLevel(source[line-1])

    if level < lastLevel:
        return parseExpr(line+1,source,parent)

    if display_src:
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

        # I hate myself for this
        if use_titlebar:
                if 'position' in attr.keys():
                    attr['position'] = attr['position'][0], attr['position'][1] + 25

        layer = 0
        if 'layer' in attr.keys(): layer = attr.pop('layer')
        if 'action' in attr.keys():
            s = attr['action']
            attr['action'] = lambda *_: runScript(s)

        if expr == '#root':
            if 'bg' not in attr.keys():
                attr['bg'] = (100,100,100)

            ui.root = ui.Root(title=attr['title'],bg=attr['bg'])

            if 'size' in attr.keys():
                if use_titlebar:
                    attr['size'] = attr['size'][0], attr['size'][1] + 25
                ui.root.res = attr['size']
            if 'resizable' in attr.keys(): ui.root.resizable = attr['resizable']

        elif expr == '#frame':
            frame = ui.Frame(**attr).add(parent,layer)
            return parseExpr(line+len(attr)+1,source,frame)

        elif expr == '#image':
            path = attr.pop('image_path')
            name = path.split('/')[-1]

            if not os.path.exists(f'temp/{name}'):

                img = get_file(addr,path)

                if img == FileNotFoundError:
                    print(f'[ERROR] Failed to load image: {path}, File not found.')
                    return parseExpr(line+len(attr)+1,source,parent)

                os.makedirs(f'temp',exist_ok=True)
                with open(f'temp/{name}','wb') as f: f.write(img)

            try: ui.Image(**attr,image_path=f'temp/{name}').add(parent,layer)
            except Exception as e:
                print(f'[ERROR] Failed to load image: {path}, {e}')

            return parseExpr(line+len(attr)+1,source,parent)

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
    global events, scripts, titlebar

    source = src.splitlines()
    source.append('')
    source.append('')

    if source[0] == '#type: ignore':
        source[0] == ''

    parseExpr(0,source)

    if not ui.root:
        print('[ERROR] "ui.root" Is not defined.')
        return

    runEvent('onLoad')

    if not hasattr(ui.root,'resizable'):
        ui.root.resizable = False

    ui.root.show(ui.root.resizable,extraFlag=ui.pygame.NOFRAME if use_titlebar else 0)

    def frame():
        global titlebar
        titlebar.text = ui.root._title

    if use_titlebar:
        titlebar = ui.Titlebar(
            ui.root._title
        ).add(ui.root,10)
        ui.root.addFrameListener(frame)

    ui.clock = ui.pygame.time.Clock()
    ui.mainloop()
    runEvent('onUnload')

    ui.pygame.quit()
    events = {}
    scripts = {}
    ui.root = None

display_src = True
use_titlebar = False

# This is used to create a gui from a .ui file

import engine as ui

def getLevel(expr:str) -> int:
    return expr.count('    ',0,expr.rfind('    ')+4)

def getAttrs(line:int,source) -> dict:
    expr = source[line]
    level = getLevel(expr)
    print(f'{line:<4} {level:>2} {expr}')

    if expr.strip() == '': return
    if expr.strip().startswith('#'): return

    attr = {}
    key,value = expr.split('=')
    key,value = key.strip(), value.strip()
    value = eval(value,{},{})


    attr[key] = value
    if getLevel(source[line+1]) < level:
        return attr
    a = getAttrs(line+1,source)
    if a is None: return attr
    attr |= a
    return attr

def parseExpr(line:int,source,parent=None):
    if line >= len(source): return
    if parent is None: parent = ui.root
    expr = source[line]
    level = getLevel(expr)
    lastLevel = getLevel(source[line-1])
    if level < lastLevel: return parseExpr(line+1,source,parent)
    
    print(f'{line:<4} {level:>2} {expr}')
    expr = expr.strip()
    
    if expr == '':
        return parseExpr(line+1,source,parent)

    if expr.startswith('#'):
        attr = getAttrs(line+1,source)
        if not attr:
            return parseExpr(line+1,source,parent)
        
        if expr == '#root':
            if 'bg' not in attr.keys():
                attr['bg'] = (100,100,100)

            ui.root = ui.Root(title=attr['title'],bg=attr['bg'])
            ui.root.width  = attr['size'][0]
            ui.root.height = attr['size'][1]
        
        elif expr == '#frame':
            frame = ui.Frame(**attr).add(parent)
            return parseExpr(line+len(attr)+1,source,frame)
        
        elif expr.startswith('#'):
            getattr(ui,expr.replace('#','').capitalize())(
                **attr
            ).add(parent)
        
    
        return parseExpr(line+len(attr)+1,source,parent)


def render(src:str):
    source = src.splitlines()
    parseExpr(0,source)

    ui.root.show()
    ui.mainloop()
    ui.root = None



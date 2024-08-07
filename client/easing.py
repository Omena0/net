import math

### EASING FUNCTIONS ###

def linear(t):
    return t

def easeInSine(t):
    return -math.cos(t * math.pi / 2) + 1

def easeOutSine(t):
    return math.sin(t * math.pi / 2)

def easeInOutSine(t):
    return -(math.cos(math.pi * t) - 1) / 2

def easeInQuad(t):
    return t * t

def easeOutQuad(t):
    return -t * (t - 2)

def easeInOutQuad(t):
    t *= 2
    if t < 1:
        return t * t / 2
    else:
        t -= 1
        return -(t * (t - 2) - 1) / 2

def easeInCubic(t):
    return t * t * t

def easeOutCubic(t):
    t -= 1
    return t * t * t + 1

def easeInOutCubic(t):
    t *= 2
    if t < 1:
        return t * t * t / 2
    else:
        t -= 2
        return (t * t * t + 2) / 2

def easeInQuart(t):
    return t * t * t * t

def easeOutQuart(t):
    t -= 1
    return -(t * t * t * t - 1)

def easeInOutQuart(t):
    t *= 2
    if t < 1:
        return t * t * t * t / 2
    else:
        t -= 2
        return -(t * t * t * t - 2) / 2

def easeInQuint(t):
    return t * t * t * t * t

def easeOutQuint(t):
    t -= 1
    return t * t * t * t * t + 1

def easeInOutQuint(t):
    t *= 2
    if t < 1:
        return t * t * t * t * t / 2
    else:
        t -= 2
        return (t * t * t * t * t + 2) / 2

def easeInExpo(t):
    return math.pow(2, 10 * (t - 1))

def easeOutExpo(t):
    return -math.pow(2, -10 * t) + 1

def easeInOutExpo(t):
    t *= 2
    if t < 1:
        return math.pow(2, 10 * (t - 1)) / 2
    else:
        t -= 1
        return -math.pow(2, -10 * t) - 1

def easeInCirc(t):
    return 1 - math.sqrt(1 - t * t)

def easeOutCirc(t):
    t -= 1
    return math.sqrt(1 - t * t)

def easeInOutCirc(t):
    t *= 2
    if t < 1:
        return -(math.sqrt(1 - t * t) - 1) / 2
    else:
        t -= 2
        return (math.sqrt(1 - t * t) + 1) / 2


def get_easing(method,ease_in=True,ease_out=True):
    if not (ease_in or ease_out): return linear
    match method:
        case 'linear':
            return linear
        case 'sine':
            if ease_in:
                if ease_out: return easeInOutSine
                else: return easeInSine
            else:
                if ease_out: return easeOutSine
        case 'quad':
            if ease_in:
                if ease_out: return easeInOutQuad
                else: return easeInQuad
            else:
                if ease_out: return easeOutQuad
        case 'cubic':
            if ease_in:
                if ease_out: return easeInOutCubic
                else: return easeInCubic
            else:
                if ease_out: return easeOutCubic
        case 'quart':
            if ease_in:
                if ease_out: return easeInOutQuart
                else: return easeInQuart
            else:
                if ease_out: return easeOutQuart
        case 'quint':
            if ease_in:
                if ease_out: return easeInOutQuint
                else: return easeInQuint
            else:
                if ease_out: return easeOutQuint
        case 'exp':
            if ease_in:
                if ease_out: return easeInOutExpo
                else: return easeInExpo
            else:
                if ease_out: return easeOutExpo
        case 'circ':
            if ease_in:
                if ease_out: return easeInOutCirc
                else: return easeInCirc
            else:
                if ease_out: return easeOutCirc
        case _:
            return easeInOutSine




# Net

Literally the internet but with basically no features

## .ui Syntax

Components start with `#` (case insensitive)

Attributes indented, with typical key = value syntax

Child items also indented.

For a full list of components, see [Ui-engine](https://github.com/Omena0/Ui-engine)

There are no callbacks (yet). Might add inline python support.

### Examples

#### 404 - Not Found

```py
#root
    title = "404 - Not Found"
    size = (500,500)
    bg = (50,50,50)

#text
    position = (250, 250)
    text = "404 - Not Found"
    size = 50
    color = (255,255,255)
```

#### Hello world

```py
#root
    title = "Test"
    size = (500,500)
    bg = (50,50,50)

#text
    text = "Hello world!"
    position = (220,220)
    size = 50
```

## Hosting a server



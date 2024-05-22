
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

## Hosting a web server

In the server directory, you can create a file for each page on your website.

The page that your users will see when they navigate to / (root), is called index.ui.

If a file is not found, they will be sent the page in 404.ui

After you have your pages set up, run the server, and test if it works locally. (run your own dns)

If you want to get a domain for your site, you can message me (Omena0) or make your own dns.

## Hosting a DNS server

Literally just run the server and port forward / tunnel it.

Sites are stored in data/sites.json, where you can configure websites.

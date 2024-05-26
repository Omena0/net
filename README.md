
# Net

# [BROWSER DOWNLOAD LINK](https://raw.githubusercontent.com/Omena0/net/main/dist/client.exe)

Literally the internet but with basically no features

## .ui Syntax

With .ui files, there are 3 different types of nodes.
Here I explain all of them to the best of my ability.

For more examples,
see the websites in this repository.

---

### General

---

In .ui files, the parent node of any given line is determined by indentation.

All nodes have a start character,
which for components is `#` and for scripts and events is `!`

---

### Components

Components are (on their own) static elements of a page.
They can only change with the 2 other types of nodes.

Components begin with their start character
(`#`) followed by the component type.

---

Optionally components can have an id.
Which allows editing it from a script or event.

Component id's are marked after the component name
and separated from it using a `:`

#### Example: #text:mytext

---

Components have attributes,
that define where it is on the page,
how it looks like, and what it does. (e.g., buttons)

For a full list of components, see [`Ui-engine`](https://github.com/Omena0/Ui-engine)

### Scripts

---

Scripts are pieces of code,
that can be run as an action to a component,
or manually from another script/event
and also have an identifier similar to components.

Scripts start with their start character (`!`) followed by `script`.
Scripts must have an identifier to be useful.

#### Example

```python
!script:onPress
    print('Button Pressed!')

#button
    position = (200,200)
    width = 50
    height = 500
    text = "Press"
    action = "onPress"
    size = 30
```

(here, `Button Pressed!` will be printed to
the console when the button is pressed.)

---

### Events

---

Events are pieces of code,
that get called automatically when the said event occurs.

Instead of having an id,
the event type is specified after the `:`.

#### Current Events

- onLoad
- onUnload

#### Example

```python
!event:onLoad
    print('Loaded!')
```

(here, `Loaded!` will be printed to the
console when the site is loaded.)

## Hosting a web server

In the server's directory,
each file corresponds to a web page.

The home page (`website.com/`) is `index.ui`

If the page the user is trying to access is not found,
the 404.ui page will be displayed.

By default, users are only able to
access theese file extensions: `.ui`, `.png`, `.jpeg` and `.txt`

You can configure theese in the source code.

## Hosting a DNS server

Literally just run the server and port forward / tunnel it.

Sites are stored in data/sites.json, where you can configure websites.

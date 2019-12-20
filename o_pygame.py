

QUIT = False

class Events(object):
    def get(self):
        return []

class Display(object):
    def set_mode(self, size):
        return DisplayRender(size)

    def flip():
        pass

class DisplayRender(object):
    def __init__(self, size):
        self.canvas = document.getElementById("myCanvas")
        self.ctx = self.canvas.getContext("2d")
        self.size = size
        self.canvas.width = size[0]
        self.canvas.height = size[1]

    def fill(self, color):
        self.ctx.fillStyle = "#FF0000"
        self.ctx.fillRect(0, 0, self.size, self.size)
        pass

    def blit(self, img, dest, source):
        self.ctx.drawImage(img, source[0], source[1], source[2], source[3], dest[0], dest[1], dest[2], dest[3])

class DisplayDraw(object):
    def rect(self, ctx, color, rect):
        hexcolor = "#"
        for c in color:
            hexcolor += hex(c)[2:]

        ctx.fillStyle = hexcolor
        ctx.fillRect(rect[0], rect[1], rect[2], rect[3])

class ImageLoader(object):
    def load(self, path):
        img = __new__ (Image())
        img.src = path
        return img

display = Display()
event = Events()
draw = DisplayDraw()
image = ImageLoader()

def init():
    pass

def Rect(x, y, width, height):
    return (x, y, width, height)
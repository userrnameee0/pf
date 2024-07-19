# create output to the screen
from math import cos, pi, sin, sqrt
from typing import Callable, TypeAlias, Union

from pygame import display, font, SRCALPHA, Surface, Rect, transform

from info import assets, colors, colorType, tps
from input import clicked, derivedTick, mousePos


screenSize: tuple[int, int] = (1024, 512)
screen: Surface = display.set_mode(screenSize)
display.set_icon(Surface((0, 0)))
display.set_caption('')

# shorter notation for types used
cords: TypeAlias = tuple[float, float]
guiBased: TypeAlias = Union['gui', 'imageGui', 'textGui']
fx: TypeAlias = Callable[[float], float]

guis: list[guiBased] = []
# since they arent in a hierarchy like files on a computer, names are used to identify them in groups instead
getAllWith: Callable[[str], list[guiBased]] = lambda name: [gui for gui in guis if name in gui.name]
getFromName: Callable[[str], guiBased] = lambda name: getAllWith(name)[0]
def toggleAllWith(name: str) -> None:
    for gui in getAllWith(name):
        gui.visible = not gui.visible

guiHovered: Callable[[guiBased], bool] = lambda hoverGui: hoverGui.visible and hoverGui.surfaces[0][1].collidepoint(mousePos)
guiClicked: Callable[[guiBased], bool] = lambda button: guiHovered(button) and clicked.left
pixelize: Callable[[cords], cords] = lambda c: (c[0] * screenSize[0], c[1] * screenSize[1])
# for putting stuff inside a certain surface, like a progress bar or an image
def insetize(c: cords) -> cords:
    inset: float = min(c) * 0.25
    return (c[0] - inset, c[1] - inset)
# making animations smooth using algebra 2!!
class easing:
    sine: fx = lambda x: -cos(pi * x) / 2 + 0.5
    elastic: fx = lambda x: sin(1.25 * pi * (x - 0.5)) / sqrt(2 + sqrt(2)) + 0.5

# surfaces are used to allow transparent guis
class gui:
    def __init__(self, name: str, pos: cords, size: cords, color: colorType, zIndex: int = 1) -> None:
        self.name: str = name
        self.pos: cords = pos
        self.size: cords = size
        self.color: colorType = color
        self.zIndex: int = zIndex

        self.pixelPos: cords = pixelize(pos)
        self.pixelSize: cords = pixelize(size)

        self.visible: bool = True
        self.surfaces: list[tuple[Surface, Rect]] = []
        self.queueRefresh: bool = True
        
        self.refresh()
        self.visible = False

        guis.append(self)
        guis.sort(key = lambda g: g.zIndex)

    def stop(self) ->  None:
        guis.remove(self)
    
    def addSurface(self, surface: Surface) -> None:
        self.surfaces.append((surface, surface.get_rect(center = self.pixelPos)))

    def refreshPos(self, pos: cords) -> None:
        if self.pos == pos:
            return
        self.pos = pos
        
        if not self.visible:
            self.queueRefresh = True
            return
        
        self.pixelPos = pixelize(self.pos)
        for i, surface in enumerate(self.surfaces):
            self.surfaces[i] = (surface[0], surface[0].get_rect(center = self.pixelPos))

    def refreshColor(self, color: colorType) -> None:
        if self.color == color:
            return
        self.color = color
        
        if not self.visible:
            self.queueRefresh = True
            return
        
        self.surfaces[0][0].fill(self.color)

    def refresh(self) -> None:
        if not self.visible:
            self.queueRefresh = True
            return
        
        self.surfaces.clear()
        
        self.pixelPos = pixelize(self.pos)
        self.pixelSize = pixelize(self.size)

        bounds: Surface = Surface(self.pixelSize, SRCALPHA)
        bounds.fill(self.color)
        self.addSurface(bounds)

    def tweenCords(self, duration: float, attribute: str, endCords: cords, easingStyle: fx = easing.sine) -> None:
        totalTicks: float = duration * tps
        ticksPassed: int = 1

        startCords: cords = getattr(self, attribute)
        diffCords: cords = (endCords[0] - startCords[0], endCords[1] - startCords[1])

        @derivedTick(1)
        def tween() -> None:
            nonlocal ticksPassed
            newCords: cords = (startCords[0] + diffCords[0] * easingStyle(ticksPassed / totalTicks), startCords[1] + diffCords[1] * easingStyle(ticksPassed / totalTicks))
            setattr(self, attribute, [startCords[i] + diffCords[i] * easingStyle(ticksPassed / totalTicks) for i in range(2)])
            if attribute == 'pos':
                self.refreshPos(newCords)
            else:
                setattr(self, attribute, newCords)
                self.refresh()
            
            if ticksPassed >= totalTicks:
                tween.stop()
            ticksPassed += 1

    def draw(self) -> None:
        if self.queueRefresh:
            self.queueRefresh = False
            self.refresh()
        for (surface, rect) in self.surfaces:
            screen.blit(surface, rect)

# for progress bars
class barGui(gui):
    def __init__(self, name: str, barColor: colorType, pos: cords, size: cords, color: colorType, zIndex: int = 1) -> None:
        self.barColor: colorType = barColor
        self.percent: float = 0
        super().__init__(name, pos, size, color, zIndex)

    def refreshPos(self, pos: cords) -> None:
        # didnt add it since i dont need it, but it barGuis dont work with default gui.refreshPos()
        raise NotImplementedError

    def refresh(self) -> None:
        if not self.visible:
            self.queueRefresh = True
            return
        
        super().refresh()
        insetPos: cords = insetize(self.pixelSize)
        bar: Surface = Surface([insetPos[0] * self.percent, insetPos[1]], SRCALPHA)
        bar.fill(self.barColor) 
        # the first surface rect is the one created by the base class gui since gui.refresh()
        # is called first, so it is used for offsetting the bar towards the center
        self.surfaces.append((bar, self.surfaces[0][1].move([(self.pixelSize[i] - insetPos[i]) / 2 for i in range(2)])))

class imageGui(gui):
    def __init__(self, name: str, image: Surface, pos: cords, size: cords, color: colorType = colors.blank, zIndex: int = 1) -> None:
        self.image: Surface = image
        super().__init__(name, pos, size, color, zIndex)

    def refresh(self) -> None:
        if not self.visible:
            self.queueRefresh = True
            return
        
        super().refresh()
        self.addSurface(transform.scale(self.image, insetize(self.pixelSize)))

fontStep: int = 2
class textGui(gui):
    def __init__(self, name: str, text: str, pos: cords, size: cords, color: colorType, textColor: colorType = colors.white, zIndex: int = 1) -> None:
        self.text: str = text
        self.textColor: colorType = textColor
        super().__init__(name, pos, size, color, zIndex)

    def refreshText(self, text: str) -> None:
        if self.text == text:
            return
        self.text = text
        
        if not self.visible:
            self.queueRefresh = True
            return

        self.surfaces.pop()

        insetPos: cords = insetize(self.pixelSize)
        fontSize: int = int(insetPos[1])
        
        while fontSize > fontStep:
            fontData: font.Font = font.Font('assets/fonts/default.ttf', fontSize)
            fontSize -= fontStep

            if fontData.size(self.text)[0] < insetPos[0]:
                self.addSurface(fontData.render(self.text, True, self.textColor))
                break

    def refresh(self) -> None:
        if not self.visible:
            self.queueRefresh = True
            return
        
        super().refresh()
        insetPos: cords = insetize(self.pixelSize)
        fontSize: float = insetPos[1]
        
        while fontSize > fontStep:
            fontData: font.Font = font.Font('assets/fonts/default.ttf', int(fontSize))
            fontSize -= fontStep

            if fontData.size(self.text)[0] < insetPos[0]:
                self.addSurface(fontData.render(self.text, True, self.textColor))
                break

# decorators are supposed to return a function (called a wrapper) which replaces the function u gave it
# this function makes a decorator and makes the decorator give out a button instead of a wrapper
def derivedOnClick(button: guiBased) -> Callable[[Callable[[], None]], guiBased]:
    def decorator(event: Callable[[], None]) -> guiBased:
        @derivedTick(1)
        def clickDetector() -> None:
            if guiClicked(button):
                assets.audio.sfx.select.play()
                event()
        return button
    return decorator

hintText: textGui = textGui('hint', '', (0, 0), (0, 0.03), colors.backdrop, zIndex = 75)
hintGuis: list[guiBased] = []
def hoverText(hintGui: guiBased, hint: Callable[[], str]) -> None:
    hintGuis.append(hintGui)
    @derivedTick(1)
    def hoverDetector() -> None:
        hovered: bool = guiHovered(hintGui)
        hintText.visible = any(hG for hG in hintGuis if guiHovered(hG))
        if not hovered:
            return
        hintText.visible = True
        text: str = hint()
        height: float = hintText.size[1]
        textLength: int = len(text)

        mousePercent: cords = (mousePos[0] / screenSize[0], mousePos[1] / screenSize[1])
        size: cords = (height * textLength * 1 / 6, height)

        hintText.size = size
        hintText.pos = (mousePercent[0] + size[0] / 2, mousePercent[1] - size[1] / 2)
        hintText.text = text
        hintText.refresh()

def derivedHoverText(hintGui: guiBased) -> Callable[[Callable[[], str]], None]:
    def decorator(hint: Callable[[], str]) -> None:
        hoverText(hintGui, hint)
    return decorator
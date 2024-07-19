# handles events/inputs
from typing import Callable

from pygame import mouse


# ticks per second
ticks: list['tick'] = []

class tick:
    def __init__(self, rate: int, event: Callable[[], None], once: bool = False) -> None:
        # ex. rate = 1 means every frame
        # ex. rate = 90 means every 90frames or every 1.5sec
        self.rate: int = rate
        self.event: Callable[[], None] = event
        self.once: bool = once

        self.current: int = 1
        ticks.append(self)

    # do people really want immortality?
    # they want understanding of what they dont understand
    # they want control of their own fate, of their own death.
    def stop(self) -> None: # the easiest way to solve a problem
        ticks.remove(self)  # is to just get rid of it. which is
                            # the easiest, but not always the best

# another way of making a tick w/ decorators
def derivedTick(rate: int, once: bool = False) -> Callable[[Callable[[], None]], tick]:
    def decorator(event: Callable[[], None]) -> tick:
        return tick(rate, event, once)
    return decorator

# only implemented user input atm is left click
clickedBefore: bool = False
mousePos: list[int] = [0, 0]
class clicked:
    left: bool = False

# no modifiable priority for ticks is implemented, but since this one is created first,
# it runs first and will ensure `clicked.left` is accurate for the entire tick
@derivedTick(1)
def leftClickCheck() -> None:
    global clickedBefore, mousePos

    click = mouse.get_pressed()[0]
    mPos = mouse.get_pos()

    mousePos[0] = mPos[0]
    mousePos[1] = mPos[1]
    clicked.left = click and not clickedBefore
    clickedBefore = click
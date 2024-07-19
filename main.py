# runs the game in order
from pygame import display, event, init, QUIT, time
init()

from info import tps
from input import tick, ticks
from output import guis
import game


clock: time.Clock = time.Clock()
# tick(1, lambda: print(round(clock.get_fps())))

while all(event.type != QUIT for event in event.get()):
    # process any events/input
    for t in ticks: 
        if t.current >= t.rate:
            t.event()
            if t.once:
                t.stop()
                continue
            t.current = 0
        t.current += 1

    # then redraw the screen
    for gui in guis:
        if gui.visible:
            gui.draw()
    display.flip()
    
    clock.tick(tps)
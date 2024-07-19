# stores all kinds of info for future reference across stuff
from typing import TypeAlias

from pygame import image, mixer, Surface


colorType: TypeAlias = str | tuple[int, int, int] | tuple[int, int, int, int]

tps: int = 60

tutorialText: tuple[str, ...] = (
    'these pigs are hungry!',
    'plant thistle flowers to feed these pigs',
    'keep them alive until they are ready to sell',
    'earn coins to upgrade your farm and reach a new high score',
    'once you reach 0 pigs, game over!',
)

class rate:
    def __init__(self, value: float, age: float) -> None:
        self.value: float = value
        self.age: float = age

class ratesT:
    def __init__(self) -> None:
        self.refresh()
    
    def refresh(self) -> None:
        self.pig: rate = rate(75.00, 1 / (20 * tps))
        self.thistle: rate = rate(25.00, 1 / (5 * tps))
        self.fertlizer: rate = rate(self.thistle.value * 2, 1.25)
        self.nutritionMix: rate = rate(self.pig.value + self.thistle.value, 1.75)    

class session:
    coins: float = 100.00
    feed: float = 5.0

class gameConfig:
    userData: session = session()
    rates: ratesT = ratesT()

class colors:
    white: colorType = (255, 255, 255)
    thistle: colorType = (232, 155, 226)
    pig: colorType = (214, 90, 102)
    play: colorType = (69, 255, 174, 64)
    booster: colorType = (217, 176, 255)
    boosterPurchase: colorType = (201, 127, 187, 64)
    nav: colorType = (61, 82, 94, 128)
    black: colorType = (0, 0, 0)
    backdrop: colorType = (0, 0, 0, 192)
    blank: colorType = (0, 0, 0, 0)

# js mapping out the file system
class musicT:
    game: mixer.Sound = mixer.Sound('assets/audio/music/game.mp3')
    menu: mixer.Sound = mixer.Sound('assets/audio/music/menu.mp3')
    # "Onion Capers" and "Airport Lounge" by Kevin MacLeod (incompetech.com)
class sfxT:
    pop: mixer.Sound = mixer.Sound('assets/audio/sfx/pop.mp3')
    select: mixer.Sound = mixer.Sound('assets/audio/sfx/select.mp3')
class audioT:
    music: type[musicT] = musicT
    sfx: type[sfxT] = sfxT
class pigsT:
    beeg: Surface = image.load('assets/images/ages/pigs/beeg.png')
    medium: Surface = image.load('assets/images/ages/pigs/medium.png')
    smol: Surface = image.load('assets/images/ages/pigs/smol.png')
class thistlesT:
    beeg: Surface = image.load('assets/images/ages/thistles/beeg.png')
    medium: Surface = image.load('assets/images/ages/thistles/medium.png')
    smol: Surface = image.load('assets/images/ages/thistles/smol.png')
class agesT:
    pigs: type[pigsT] = pigsT
    thistles: type[thistlesT] = thistlesT
class bgsT:
    barn: Surface = image.load('assets/images/bgs/barn.png')
    clouds: Surface = image.load('assets/images/bgs/clouds.png')
class boostersT:
    pig: Surface = image.load('assets/images/icons/boosters/pig.png')
    thistle: Surface = image.load('assets/images/icons/boosters/thistle.png')
class navsT:
    booster: Surface = image.load('assets/images/icons/navs/booster.png')
    coin: Surface = image.load('assets/images/icons/navs/coin.png')
    feed: Surface = image.load('assets/images/icons/navs/feed.png')
    pig: Surface = image.load('assets/images/icons/navs/pig.png')
    thistle: Surface = image.load('assets/images/icons/navs/thistle.png')
class iconsT:
    boosters: type[boostersT] = boostersT
    navs: type[navsT] = navsT
class signsT:
    title: Surface = image.load('assets/images/signs/title.png')
class imagesT:
    ages: type[agesT] = agesT
    bgs: type[bgsT] = bgsT
    icons: type[iconsT] = iconsT
    signs: type[signsT] = signsT

# this now has autocomplete!!
class assets:
    audio: type[audioT] = audioT
    images: type[imagesT] = imagesT
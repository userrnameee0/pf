# creates the inputs and outputs for ur game
from math import floor
from random import randint, random, randrange
from typing import Any, Callable, IO

from pygame import Surface

from info import agesT, assets, colors, colorType, gameConfig, navsT, rate, session, tps, tutorialText
from input import derivedTick, tick
from output import derivedHoverText, derivedOnClick, cords, easing, getAllWith, getFromName, guiBased, hoverText, toggleAllWith, gui, barGui, imageGui, textGui


# region loading screen setup #
imageGui('background', assets.images.bgs.barn, (0.5, 0.5), (7 / 6, 4 / 3)).visible = True

class loadScreen:
    visible: bool = False
    cycle: tuple[str, ...] = ('•', '• •', '• • •')

    clouds: tuple[imageGui, imageGui] = (
        imageGui('loadCloudsLeft', assets.images.bgs.clouds, (0.25, 0.5), (7 / 6, 4 / 3), zIndex = 100),
        imageGui('loadCloudsRight', assets.images.bgs.clouds, (0.75, 0.5), (7 / 6, 4 / 3), zIndex = 100),
    )
    indicator: textGui = textGui('loadText', '', (0.5, 0.5), (0.2, 0.2), colors.blank, colors.black, zIndex = 100)

def toggleLoading() -> None:
    loadScreen.visible = not loadScreen.visible
    tickSpeed: int = tps
    for i in range(2):
        cloud: imageGui = loadScreen.clouds[i]
        cloud.tweenCords(tickSpeed / tps, 'pos', (0.75 if i else 0.25, 0.5) if loadScreen.visible else (1.5 if i else -0.5, 0.5))
    
    if loadScreen.visible:
        toggleAllWith('load')
        cycleStep: int = 0

        # loop the text inside of loadScreen.cycle until its not visible anymore
        @derivedTick(int(tps / 2), True)
        def doCycle() -> None:
            @derivedTick(int(tps / 2))
            def cycle() -> None:
                nonlocal cycleStep
                if not loadScreen.visible:
                    cycle.stop()
                    return
                
                loadScreen.indicator.refreshText(loadScreen.cycle[cycleStep])
                cycleStep += 1
                if cycleStep >= len(loadScreen.cycle):
                    cycleStep = 0
    
    else:
        loadScreen.indicator.refreshText('')
        tick(tickSpeed, lambda: toggleAllWith('load'), True)

toggleLoading()
# endregion

# region digital farm setup #
class bounds:
    def __init__(self, topLeft: cords, bottomRight: cords) -> None:
        self.topLeft: cords = topLeft
        self.bottomRight: cords = bottomRight
    
    def getLength(self) -> cords:
        return (
            self.bottomRight[0] - self.topLeft[0],
            self.bottomRight[1] - self.topLeft[1],
        )

    def randPosition(self) -> cords:
        length: cords = self.getLength()
        randEnd: int = 100
        randStep: int = 1
        return (
            self.topLeft[0] + length[0] * randrange(0, randEnd + randStep, randStep) / randEnd,
            self.topLeft[1] + length[1] * randrange(0, randEnd + randStep, randStep) / randEnd,
        )

class item:
    def __init__(self, p: 'pool') -> None:
        size: float = 0.1
        pos: cords = p.area.randPosition()
        zIndex: int = floor((pos[1] - p.area.topLeft[1]) / p.area.getLength()[1] * 10 + 1)

        self.stages: tuple[Surface, ...] = p.stages
        
        self.rate: float = 0
        self.icon: imageGui = imageGui(p.name + 'Item', p.stages[0], pos, (size, size * 2), zIndex = zIndex)
        self.progress: barGui = barGui(p.name + 'ItemBar', p.color, (pos[0], pos[1] - size * 0.75), (size, size / 3), colors.white, zIndex)
        self.icon.visible = True
    
    def updateStage(self) -> None:
        # if the percent is >1, it defaults to the last stage
        maxStage: int = len(self.stages)
        newImage: Surface = self.stages[min(floor(self.progress.percent * maxStage), maxStage - 1)]
        if self.icon.image != newImage:
            self.icon.image = newImage
            self.icon.refresh()
    
    def stop(self) -> None:
        self.icon.stop()
        self.progress.stop()

class pool:
    def __init__(self, name: str, area: bounds, stages: tuple[Surface, ...], color: colorType) -> None:
        self.name: str = name
        self.area: bounds = area
        self.stages: tuple[Surface, ...] = stages
        self.color: colorType = color

    def add(self, startProcess: Callable[[item], None], idleProcess: Callable[[item], None], finishProcess: Callable[[item], None]) -> None:
        i: item = item(self)
        startProcess(i)
        @derivedTick(1)
        def cycle() -> None:
            if i.progress.percent >= 1:
                cycle.stop()
                finishProcess(i)
                i.stop()
                return
            idleProcess(i)
            i.updateStage()

ages: type[agesT] = assets.images.ages
pigs: pool = pool('pig', bounds((0.1, 0.6), (0.65, 0.8)), (ages.pigs.smol, ages.pigs.medium, ages.pigs.beeg), colors.pig)
thistles: pool = pool('thistle', bounds((0.75, 0.275), (0.925, 0.625)), (ages.thistles.smol, ages.thistles.medium, ages.thistles.beeg), colors.thistle)
# endregion

# region dialog setup #
class dialog:
    active: bool = False
    prompts: list[str] = []

    cover: gui = gui('dialogCover', (0.5, 0.5), (1, 1), colors.backdrop, 90)
    prompt: textGui = textGui('dialogText', '', (0.5, 0.5), (1, 0.1), colors.blank, zIndex = 90)
    hint: textGui = textGui('dialogHint', 'click to continue', (0.5, 0.95), (1, 0.05), colors.blank, zIndex = 90)

@derivedOnClick(dialog.cover)
def dialogCover() -> None:
    if not dialog.prompts:
        dialog.active = False
        return
    dialog.prompt.refreshText(dialog.prompts.pop())

def derivedDialogPrompt(text: tuple[str, ...]) -> Callable[[Callable[[], None]], None]:
    def dialogPrompt(onCompletion: Callable[[], None]) -> None:
        dialog.active = True
        dialog.prompts.extend(text[-1:0:-1])
        toggleAllWith('dialog')
        dialog.prompt.refreshText(text[0])

        @derivedTick(1)
        def finishedCycle() -> None:
            if dialog.active:
                return
            finishedCycle.stop()
            toggleAllWith('dialog')
            onCompletion()
    return dialogPrompt
# endregion

# region data setup #
def modHighScore(fileReq: str, mod: Callable[[IO[Any]], float]) -> float:
    file: IO[Any] = open('data.txt', fileReq)
    result: float = mod(file)
    file.close()
    return result

def trySettingHighScore() -> None:
    highScore: float = modHighScore('r', lambda f: float(f.read()))
    coins: float = gameConfig.userData.coins
    if coins > highScore:
        highScore = coins
        modHighScore('w', lambda f: f.write(str(highScore)))
    menu.highscore.refreshText(f'high score: {chop(highScore)}')
# endregion

# region game setup #
gameLost: bool = False

# region gui setup #
navs: type[navsT] = assets.images.icons.navs
class navMath:
    sX: float = 0.3 - 0.025
    optionSize: cords = (sX / 3, sX / 3 * 2)
    optionPY: float = 0.3 + 0.025 / 2
    zIndex: int = 25
class navTop:
    top: gui = gui('gameNavTop', (0.15, 0.1), (navMath.sX, 0.2 - 0.05), colors.nav, navMath.zIndex)
    coinsIcon: imageGui = imageGui('gameNavTopCoinsIcon', navs.coin, (0.05, 0.1), (0.075, 0.15), zIndex = navMath.zIndex)
    coins: textGui = textGui('gameNavTopCoins', '0', (0.1 + 0.025 / 2, 0.1), (0.1, 0.1), colors.blank, zIndex = navMath.zIndex)
    feedIcon: imageGui = imageGui('gameNavTopFeedIcon', navs.feed, (0.25, 0.1), (0.075, 0.15), zIndex = navMath.zIndex)
    feedBar: barGui = barGui('gameNavTopFeedBar', colors.thistle, (0.25, 0.125), (0.0625, 0.025), colors.backdrop, navMath.zIndex)
hoverText(navTop.feedBar, lambda: 'full if you can keep the pigs fed for a while with respect to how fast thistles grow, so keep this full!')
class navBottom:
    bottom: gui = gui('gameNavBottom', (0.15, 0.6 + navMath.optionSize[1] / 2), (navMath.sX, 0.8 - 0.05 - navMath.optionSize[1]), colors.nav, navMath.zIndex)
    optionPig: imageGui = imageGui('gameNavBottomOptionPig', navs.pig, ((navMath.optionSize[0] + 0.025) / 2, navMath.optionPY), navMath.optionSize, colors.nav, navMath.zIndex)
    optionThistle: imageGui = imageGui('gameNavBottomOptionThistle', navs.thistle, (0.15, navMath.optionPY), navMath.optionSize, colors.nav, navMath.zIndex)
    optionBooster: imageGui = imageGui('gameNavBottomOptionBooster', navs.booster, ((navMath.optionSize[0] * 5 + 0.025) / 2, navMath.optionPY), navMath.optionSize, colors.nav, navMath.zIndex)
class navDetail:
    name: str = 'navDetail'
    total: textGui = textGui(name + 'Total', 'Total str: int', (0.15, 0.6), (0.2, 0.1), colors.blank, zIndex = navMath.zIndex)
    rate: textGui = textGui(name + 'Rate', 'float', (0.15, 0.7), (0.2, 0.1), colors.blank, zIndex = navMath.zIndex)
class navBooster:
    name: str = 'navBooster'
    thistle: textGui = textGui(name + 'Thistle', 'Buy thistle seeds', (0.15, 0.5), (0.2, 0.1), colors.boosterPurchase, zIndex = navMath.zIndex)
    thistleIcon: imageGui = imageGui(name + 'ThistleIcon', ages.thistles.smol, (0.05, 0.45), (0.075, 0.15), zIndex = navMath.zIndex)
    fertilizer: textGui = textGui(name + 'Fertilizer', 'Buy fertlizer for thistles', (0.15, 0.5 + 0.175), (0.2, 0.1), colors.boosterPurchase, zIndex = navMath.zIndex)
    fertilizerIcon: imageGui = imageGui(name + 'FertilizerIcon', assets.images.icons.boosters.thistle, (0.05, 0.45 + 0.175), (0.075, 0.15), zIndex = navMath.zIndex)
    nutritionMix: textGui = textGui(name + 'NutritionMix', 'Buy nutrition mix for pigs', (0.15, 0.5 + 0.35), (0.2, 0.1), colors.boosterPurchase, zIndex = navMath.zIndex)
    nutritionMixIcon: imageGui = imageGui(name + 'NutritionMixIcon', assets.images.icons.boosters.pig, (0.05, 0.45 + 0.35), (0.075, 0.15), zIndex = navMath.zIndex)
# endregion

# region nav updating stuff #
# hehe
secsFromRate: Callable[[float], float] = lambda rate: 1 / rate / tps
chop: Callable[[float], float] = lambda n: round(n, 2)

currentNav: str = ''
def swapNavTo(name: str) -> None:
    global currentNav
    if currentNav == name:
        return
    
    currentNav = name
    rawColor: tuple[int, int, int] = getattr(colors, name)
    color: colorType = (rawColor[0], rawColor[1], rawColor[2], 128)
    imagePressed: guiBased = getFromName('gameNavBottomOption' + name.capitalize())

    for img in getAllWith('gameNavBottomOption'):
        img.refreshColor(color if img == imagePressed else colors.nav)
    navBottom.bottom.refreshColor(color)

    isBooster = currentNav == 'booster'
    for g in getAllWith(navBooster.name):
        g.visible = isBooster
    for g in getAllWith(navDetail.name):
        g.visible = not isBooster

def toggleFarmBars(pig: bool, thistle: bool) -> None:
    for bar in getAllWith('pigItemBar'):
        bar.visible = pig
    for bar in getAllWith('thistleItemBar'):
        bar.visible = thistle

@derivedOnClick(navBottom.optionPig)
def swapToPig() -> None:
    swapNavTo('pig')
    toggleFarmBars(True, False)
    
@derivedOnClick(navBottom.optionThistle)
def swapToThistle() -> None:
    swapNavTo('thistle')
    toggleFarmBars(False, True)

# we need this one for later
def swapToBooster() -> None:
    swapNavTo('booster')
    toggleFarmBars(False, False)
derivedOnClick(navBottom.optionBooster)(swapToBooster)


@derivedTick(2)
def refreshNavData() -> None:
    totalPigs: int = len(getAllWith('pigItemBar'))
    if totalPigs < 1:
        return
    navTop.coins.refreshText(str(chop(gameConfig.userData.coins)))
    totalPigFeed: float = totalPigs * (gameConfig.rates.pig.age * 1.5)
    totalFeedRate: float = totalPigFeed * tps * secsFromRate(gameConfig.rates.thistle.age) * 4
    navTop.feedBar.percent = min(max(gameConfig.userData.feed / totalFeedRate, 0), 1)
    navTop.feedBar.refresh()

    if currentNav == 'pig':
        navDetail.total.refreshText(f'total pigs: {totalPigs}')
        navDetail.rate.refreshText(f'thistle feed per second: ~{chop(totalPigFeed * tps)}')
    elif currentNav == 'thistle':
        navDetail.total.refreshText(f'total thistles: {len(getAllWith('thistleItemBar'))}')
        navDetail.rate.refreshText(f'thistles can feed {chop(gameConfig.userData.feed)} pigs')
# endregion

# region pool item processes #
def introStart(i: item) -> None:
    i.progress.percent = random()
def introIdle(i: item) -> None:
    if dialog.prompts:
        i.progress.percent = 1
def spawnRandomIntro() -> None:
    for i in range(10):
        pigs.add(introStart, introIdle, lambda i: None)
        thistles.add(introStart, introIdle, lambda i: None)

def startItem(r: rate) -> Callable[[item], None]:
    def startFunc(i: item) -> None:
        i.rate = r.age + r.age * random()
    return startFunc
pigStart: Callable[[item], None] = startItem(gameConfig.rates.pig)
thistleStart: Callable[[item], None] = startItem(gameConfig.rates.thistle)

def pigIdle(p: item) -> None:
    if gameLost:
        p.progress.percent = 1
        return
    
    feed: float = gameConfig.userData.feed
    if feed > p.rate:
        p.progress.percent += p.rate
        gameConfig.userData.feed -= p.rate
        p.progress.refresh()
    else:
        currentAge: float = p.progress.percent
        @derivedTick(int(tps + tps * 2 * random()), True)
        def onStarve() -> None:
            if currentAge == p.progress.percent:
                p.progress.percent = 1
                p.rate = 0
def thistleIdle(t: item) -> None:
    if gameLost:
        t.progress.percent = 1
        return
    
    t.progress.percent += t.rate
    t.progress.refresh()

def pigFinish(p: item) -> None:
    global gameLost    
    assets.audio.sfx.pop.play()
    if p.rate > 0:
        benefit: float = gameConfig.rates.pig.value
        icon: imageGui = p.icon

        gameConfig.userData.coins += benefit
        for i in range(1, randint(3, 5)):
            pigs.add(pigStart, pigIdle, pigFinish)

        coinsConfirmation: textGui = textGui('coinConfirmation', f'+{benefit}', icon.pos, icon.size, colors.blank, zIndex = icon.zIndex)
        coinsConfirmation.visible = True
        coinsConfirmation.tweenCords(0.5, 'pos', (icon.pos[0], icon.pos[1] - 0.05))
        tick(int(tps / 2), coinsConfirmation.stop, True)
    
    if len(getAllWith('pigItemBar')) == 1:
        gameLost = True
        assets.audio.music.game.fadeout(2_000)
        @derivedTick(tps, True)
        def onComfirmation() -> None:
            @derivedDialogPrompt(('you ran out of pigs!', 'game over'))
            def onLose() -> None:
                assets.audio.music.menu.play(-1, fade_ms = 1_000)
                toggleLoading()
                @derivedTick(tps * 2, True)
                def cleanUp() -> None:
                    global gameLost, currentNav
                    trySettingHighScore()
                    gameConfig.userData = session()
                    gameConfig.rates.refresh()
                    gameLost = False
                    swapToBooster()
                    toggleAllWith(navBooster.name)
                    currentNav = ''
                    toggleAllWith('game')
                    toggleAllWith('menu')
                    spawnRandomIntro()
                    toggleLoading()
                
def thistleFinish(t: item) -> None:
    if gameLost:
        return
    
    assets.audio.sfx.pop.play()
    gameConfig.userData.feed += 0.5
# endregion

# region shop #
def coinExchange(cost: float) -> bool:
    if cost <= gameConfig.userData.coins:
        gameConfig.userData.coins -= cost
        return True
    return False

hoverText(navBooster.thistle, lambda: f'Costs {gameConfig.rates.thistle.value} coins. Keeps a pig full for a bit once grown!')
@derivedOnClick(navBooster.thistle)
def gameNavBottomBoosterThistle() -> None:
    if not coinExchange(gameConfig.rates.thistle.value):
        return
    thistles.add(thistleStart, thistleIdle, thistleFinish)

def derivedGenericRateButton(button: textGui, modRateName: str) -> Callable[[Callable[[], None]], None]:
    def genericRateButton(modSpecial: Callable[[], None]) -> None:
        @derivedOnClick(button)
        def purchaseButton() -> None:
            modRate: rate = getattr(gameConfig.rates, modRateName)
            if not coinExchange(modRate.value):
                return
            modRate.value *= modRate.age
            modSpecial()
    return genericRateButton

@derivedHoverText(navBooster.fertilizer)
def onFertlizerHover() -> str:
    cost: float = gameConfig.rates.fertlizer.value
    thistleAge: float = gameConfig.rates.thistle.age
    return f'Costs {chop(cost)} coins. Makes thistles grow faster!' +\
        f'({chop(secsFromRate(thistleAge))}sec -> {chop(secsFromRate(thistleAge * gameConfig.rates.fertlizer.age))}sec)'
@derivedGenericRateButton(navBooster.fertilizer, 'fertlizer')
def modThistleAge() -> None:
    gameConfig.rates.thistle.age *= 1.1
@derivedHoverText(navBooster.nutritionMix)
def onNutritionMixHover() -> str:
    benefit: float = gameConfig.rates.thistle.value
    return f'Costs {chop(gameConfig.rates.nutritionMix.value)} coins. Will make pigs worth {benefit} more coins!' +\
        f'({gameConfig.rates.pig.value} -> {gameConfig.rates.pig.value + benefit})'
@derivedGenericRateButton(navBooster.nutritionMix, 'nutritionMix')
def modPigValue() -> None:
    gameConfig.rates.pig.value += gameConfig.rates.thistle.value
# endregion

# endregion

# region menu setup #
class menu:
    # debounce is like giving function a cooldown
    playDebounce: bool = False

    title: tuple[imageGui, textGui] = (
        imageGui('menuTitleBorder', assets.images.signs.title, (0.5, 0.25), (0.5, 0.5)),
        textGui('menuTitleText', 'peeg simulator', (0.5, 0.25), (0.35, 0.5), colors.blank),
    )
    play: textGui = textGui('menuLowerPlay', 'play', (0.5, 0.7), (0.25, 0.1), colors.play, zIndex = 50)
    highscore: textGui = textGui('menuLowerHighScore', 'high score: 0', (0.5, 0.775), (0.25, 0.05), colors.blank, zIndex = 50)

@derivedOnClick(menu.play)
def menuPlay() -> None:
    if not menu.playDebounce:
        menu.playDebounce = True
        toggleLoading()

        @derivedTick(tps, True)
        def onFinished() -> None:
            menu.playDebounce = False
            toggleAllWith('menu')
            toggleLoading()

            assets.audio.music.menu.fadeout(4_000)
            @derivedDialogPrompt(tutorialText)
            def startGame() -> None:
                assets.audio.music.game.play(-1, fade_ms = 1_000).set_volume(0.6)
                toggleAllWith('game')
                swapToBooster()
                for i in range(2):
                    pigs.add(pigStart, pigIdle, pigFinish)
# endregion

# region play intro #
assets.audio.music.menu.play(-1, fade_ms = 1_000)
@derivedTick(180, True)
def onIntro() -> None:
    spawnRandomIntro()
    toggleLoading()

    @derivedTick(tps, True)
    def onMenuTitle() -> None:
        for titleGui in menu.title:
            pos: cords = titleGui.pos
            titleGui.refreshPos((pos[0], pos[1] - 0.5))
            titleGui.visible = True
            titleGui.tweenCords(1.25, 'pos', pos, easing.elastic)
        
        @derivedTick(int(tps * 1.5), True)
        def onMenuLower() -> None:
            trySettingHighScore()
            toggleAllWith('menuLower')
# endregion
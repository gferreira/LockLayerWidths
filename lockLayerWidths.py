from vanilla import *
from defconAppKit.windows.baseWindow import BaseWindowController
import mojo.drawingTools as ctx
from mojo.UI import getDefault, UpdateCurrentGlyphView, CurrentGlyphWindow, CurrentSpaceCenter
from mojo.roboFont import OpenWindow
from mojo.events import addObserver, removeObserver
from mojo.canvas import CanvasGroup

class GlyphWidthObserver(BaseWindowController):

    glyph   = None
    verbose = True
    modes   = ['all unlocked', 'all locked', 'glyph locks']

    padding      = 10
    buttonHeight = 25
    textHeight   = 20
    width        = 123
    height       = textHeight * 9 + buttonHeight + padding * 7

    key = 'lockLayerWidths'

    def __init__(self):

        self.w = FloatingWindow((self.width, self.height))

        x = y = p = self.padding
        self.w.modeLabel = TextBox(
                (x, y, -p, self.textHeight),
                'lock layer widths:',
                sizeStyle='small')

        y += self.textHeight
        self.w.mode = RadioGroup(
                (x, y, -p, self.textHeight * len(self.modes)),
                self.modes,
                sizeStyle='small',
                callback=self.radioGroupCallback,
                isVertical=True)
        self.w.mode.set(0)

        y += self.textHeight * len(self.modes) + p

        self.w.separator1 = HorizontalLine((x, y, -p, 1))

        y += p
        self.w.lockGlyhsLabel = TextBox(
                (x, y, -p, self.textHeight),
                'set glyph locks:',
                sizeStyle='small')

        y += self.textHeight
        self.w.currentGlyph = CheckBox(
                (x, y, -p, self.textHeight),
                'current glyph',
                value=True,
                sizeStyle='small')
        self.w.currentGlyph.enable(False)

        y += self.textHeight
        self.w.selectedGlyphs = CheckBox(
                (x, y, -p, self.textHeight),
                'font selection',
                value=True,
                sizeStyle='small')
        self.w.selectedGlyphs.enable(False)

        y += self.textHeight
        self.w.spaceCenter = CheckBox(
                (x, y, -p, self.textHeight),
                'space center',
                value=True,
                sizeStyle='small')
        self.w.spaceCenter.enable(False)

        buttonWidth = (self.width - p * 2) * 0.5
        y += self.textHeight + p
        self.w.lockGlyphsButton = SquareButton(
                (x, y, buttonWidth, self.buttonHeight),
                'lock',
                callback=self.lockGlyphsCallback,
                sizeStyle='small')
        self.w.lockGlyphsButton.enable(False)

        x += buttonWidth - 1
        self.w.unlockGlyphsButton = SquareButton(
                (x, y, buttonWidth, self.buttonHeight),
                'unlock',
                callback=self.unlockGlyphsCallback,
                sizeStyle='small')
        self.w.unlockGlyphsButton.enable(False)

        x = p
        y += self.buttonHeight + p + 2
        self.w.separator2 = HorizontalLine((x, y, -p, 1))

        y += p
        self.w.verbose = CheckBox(
                (x, y, -p, self.textHeight),
                'verbose',
                value=True,
                sizeStyle='small')

        self.setUpBaseWindowBehavior()
        addObserver(self, "drawObserver", "draw")

        self.w.open()

    # ---------
    # callbacks
    # ---------

    def lockGlyphsCallback(self, sender):
        self._setLockUnlockStatus(True)

    def unlockGlyphsCallback(self, sender):
        self._setLockUnlockStatus(False)

    def radioGroupCallback(self, sender):
        mode = sender.get()

        if mode == 0:
            removeObserver(self, "currentGlyphChanged")
            self.unsubscribeGlyph()
        else:
            addObserver(self, 'currentGlyphChangedObserver', 'currentGlyphChanged')
            addObserver(self, 'spaceCenterDrawObserver', "spaceCenterDraw")
            addObserver(self, 'drawCellObserver', 'glyphCellDrawBackground')
            self.subscribeGlyph(CurrentGlyph())

        if mode == 2:
            self.w.lockGlyhsLabel.enable(True)
            self.w.currentGlyph.enable(True)
            self.w.selectedGlyphs.enable(True)
            self.w.spaceCenter.enable(True)
            self.w.lockGlyphsButton.enable(True)
            self.w.unlockGlyphsButton.enable(True)
        else:
            self.w.lockGlyhsLabel.enable(False)
            self.w.currentGlyph.enable(False)
            self.w.selectedGlyphs.enable(False)
            self.w.spaceCenter.enable(False)
            self.w.lockGlyphsButton.enable(False)
            self.w.unlockGlyphsButton.enable(False)

        self._updateWindows()

    def windowCloseCallback(self, sender):
        self.unsubscribeGlyph()
        removeObserver(self, 'currentGlyphChanged')
        removeObserver(self, 'draw')
        removeObserver(self, 'spaceCenterDraw')
        removeObserver(self, 'glyphCellDrawBackground')
        super(GlyphWidthObserver, self).windowCloseCallback(sender)

    # ---------
    # observers
    # ---------

    def currentGlyphChangedObserver(self, notification):
        # observer for RF notification -> add defcon observer for glyph
        self.subscribeGlyph(notification["glyph"])

    def widthChangedObserver(self, notification):

        mode = self.w.mode.get()

        # observer for defcon notification -> copy width to other layers
        glyph = notification.object
        glyph = RGlyph(glyph)
        width = notification.data['newValue']

        # mode 0 : OFF
        if mode == 0:
            return

        # mode 1 : only marked glyphs
        elif mode == 2:
            f = glyph.font
            if f is None:
                return
            if self.key not in f.lib:
                return
            if glyph.name not in f.lib[self.key]:
                return

        # mode 2 : all glyphs
        elif mode == 1:
            pass

        # copy glyph width to other layers
        for layerName in glyph.font.layerOrder:
            if layerName == glyph.layer.name:
                continue
            g = glyph.getLayer(layerName)
            if self.w.verbose.get():
                print('copying width from %s.%s to %s.%s...' % (glyph.name, glyph.layer.name, glyph.name, layerName))
            g.width = width
        if self.w.verbose.get():
            print()

    def drawObserver(self, notification):

        glyph = notification['glyph']
        scale = notification['scale']

        lockStatus = self.getLockStatus(glyph)
        if not lockStatus: # is None:
            return

        lockStatusIcon = '🔒' if lockStatus else '🔓'
        ctx.save()
        ctx.fontSize(24 * scale)
        ctx.textBox(lockStatusIcon, (0, -100, glyph.width, 24 * scale), align='right')
        ctx.restore()

    def spaceCenterDrawObserver(self, notification):

        glyph = notification['glyph']
        scale = notification['scale']

        lockStatus = self.getLockStatus(glyph)
        if not lockStatus: # is None:
            return

        lockStatusIcon = '🔒' if lockStatus else '🔓' # 'L' if lockStatus else 'U'
        ctx.save()
        ctx.scale(1, -1)
        ctx.fontSize(120)
        ctx.text(lockStatusIcon, (glyph.width - 100, 30))
        ctx.restore()

    def drawCellObserver(self, notification):
        # print(notification.keys())
        # print(notification["glyphCell"])
        # print(notification["cell"])

        glyph = notification["glyph"]

        if self.w.mode.get() == 0:
            return

        lockStatus = self.getLockStatus(glyph)
        if not lockStatus: # is None:
            return

        lockStatusIcon = '🔒' if lockStatus else '🔓'
        ctx.save()
        ctx.fontSize(16)
        ctx.text(lockStatusIcon, (0, 0))
        ctx.restore()

    # -------
    # methods
    # -------

    def _updateWindows(self):

        # update glyph window
        UpdateCurrentGlyphView()

        # update font overview
        f = CurrentFont()
        if f is not None:
            f.changed()

        # update space center
        s = CurrentSpaceCenter()
        if s:
            i = s.glyphLineView.getSelection()
            s.updateGlyphLineView()
            if i is not None:
                s.glyphLineView.setSelection(i)

    def _setLockUnlockStatus(self, value):
        self.setLockStatus(value)
        self._updateWindows()

    def getGlyphs(self):

        glyphs = []

        # font window selection
        if self.w.selectedGlyphs.get():
            font = CurrentFont()
            if font is not None:
                glyphs += font.selectedGlyphs

        # current glyph window
        if self.w.currentGlyph.get():
            glyphWindow = CurrentGlyphWindow()
            if glyphWindow is not None:
                g = glyphWindow.getGlyph()
                if g is not None and g not in glyphs:
                    glyphs += [RGlyph(g)]

        # space center selection
        if self.w.spaceCenter.get():
            spaceCenter = CurrentSpaceCenter(currentFontOnly=True)
            if spaceCenter is not None:
                g = spaceCenter.glyphLineView.getSelected()
                if g is not None and g not in glyphs:
                    glyphs += [RGlyph(g)]

        return glyphs

    def getLockStatus(self, glyph):

        mode  = self.w.mode.get()

        if mode == 1:
            lockStatus = True

        elif mode == 2:
            if self.key not in glyph.font.lib:
                lockStatus = False
            else:
                lockStatus = True if glyph.name in glyph.font.lib[self.key] else False

        else: # mode == 0:
            lockStatus = None

        return lockStatus

    def subscribeGlyph(self, glyph):
        # subscribe to defcon notification
        self.unsubscribeGlyph()
        if glyph is not None:
            self.glyph = glyph
            self.glyph.addObserver(self, "widthChangedObserver", "Glyph.WidthChanged")

    def unsubscribeGlyph(self):
        # unsubscribe from defcon notification
        if self.glyph is not None:
            self.glyph.removeObserver(self, "Glyph.WidthChanged")
            self.glyph = None

    def setLockStatus(self, value):

        verbose = self.w.verbose.get()

        font = CurrentFont()
        if not font:
            return

        # ----------
        # get glyphs
        # ----------

        glyphs = self.getGlyphs()
        if not len(glyphs):
            return

        # ---------------
        # set lock status
        # ---------------

        if not self.key in font.lib:
            font.lib[self.key] = []

        for glyph in glyphs:
            if value:
                if verbose:
                    print('locking layer widths (%s)...' % glyph.name)
                if glyph.name not in font.lib[self.key]:
                    font.lib[self.key].append(glyph.name)
            else:
                if verbose:
                    print('unlocking layer widths (%s)...' % glyph.name)
                if glyph.name in font.lib[self.key]:
                    font.lib[self.key].remove(glyph.name)

            glyph.changed()

        if len(glyphs) and verbose:
            print()

# -------
# testing
# -------

OpenWindow(GlyphWidthObserver)

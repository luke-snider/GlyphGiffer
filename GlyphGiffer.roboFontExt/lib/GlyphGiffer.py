#coding=utf-8
'''
Lukas Schneider - Revolver Type Foundry - www.revolvertype.com
GlyphGiffer lets you export glyphs from a folder of .ufo files as an animated .gif.
'''
from __future__ import print_function

import os
from vanilla import *
from vanilla.dialogs import getFolder
#from robofab.interface.all.dialogs import ProgressBar
from LS_dialogs.LSdialogs import AskYesNoCancel, ProgressBar


from AppKit import NSColor

### 4 drawBot
import random
from drawBot import *
from collections import Counter
import os.path, time
from os import path
import datetime


from lib.UI.stepper import SliderEditIntStepper, EditIntStepper

class GlyphGiffer():

    def __init__(self): 
        self.widthOfTool = 360
        self.heightOfTool = 300

        self.loadedFontList = []

        self.w = FloatingWindow((self.widthOfTool, self.heightOfTool), "GlyphGiffer")
        self.w.loadFontFolder = Button((10, 10, -10, 20), "Load fonts from folder", callback=self.loadFontsFromFolder, sizeStyle="regular")
        self.w.amountOfLoadedFonts = TextBox((20, 14, 50, 20), "0", sizeStyle="small")

        self.w.glyphsInfo = TextBox((10, 42, 105, 60), "GlyphNames\nseparated by /\nor\nA-Z / a-z", sizeStyle="small")
        self.w.glyphName = EditText((110, 40, -10, 60), "a", sizeStyle="small")

        y = 120
        self.w.Info = TextBox((10, y+2, 115, 20), "Canvas Settings", sizeStyle="small")
        self.w.title = EditText((110, y, 155, 20), "", sizeStyle="small", placeholder="Title")
        self.w.titleColor = ColorWell((-30, y, 20, 20), color=NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 1, 1, 0.8), callback=self.colorWell1UserInput)
        self.w.timestamp = CheckBox((285, y, 50, 20), "Date", sizeStyle="small", value=False, callback=self.FillLikeStroke)
        y = 145
        self.w.canvasInfo = TextBox((10, y+2, 90, 20), "Height", sizeStyle="small")
        self.w.pageHeight = EditText((110, y, 40, 20), 300, sizeStyle='small', callback=self.validateUserInputPageHeight)
        #self.w.pageWidth = EditIntStepper((110, y, 60, 20), 300, sizeStyle='small', minValue=10)
        #self.w.pageWidth.show(False)
        self.w.speedInfo = TextBox((180, y+2, 150, 20), "Speed (1=fast/10=slow)", sizeStyle="small")
        self.w.speed = EditText((-40, y, 30, 20), 1, sizeStyle='small', callback=self.validateUserInputSpeed)
        ###
        self.w.canvasMarginInfo = TextBox((-85, y+2, 45, 20), "Margin", sizeStyle="small")
        self.w.canvasMargin = EditText((-40, y, 30, 20), "1.2", sizeStyle="small", callback=self.validateUserInputMargin)
        self.w.canvasMarginInfo.show(False)
        self.w.canvasMargin.show(False)
        y = 170
        self.w.colorInfo1 = TextBox((10, y+3, 100, 20), "Fill / Stroke / BG", sizeStyle="small")
        self.w.glyphFillColor = ColorWell((110, y, 40, 20), color=NSColor.colorWithCalibratedRed_green_blue_alpha_(0.3, 0, 0.9, 1), callback=self.colorWell1UserInput)
        self.w.glyphStrokeColor = ColorWell((170, y, 40, 20), color=NSColor.colorWithCalibratedRed_green_blue_alpha_(0.9, 0, 1, 1), callback=self.colorWell2UserInput)
        self.w.fillLikeStroke = CheckBox((155, y+2, 20, 20), "", sizeStyle="mini", value=True, callback=self.FillLikeStroke)
        self.FillLikeStroke(sender=None)
        self.w.backgroundColor = ColorWell((225, y, 40, 20), color=NSColor.colorWithCalibratedRed_green_blue_alpha_(0.9, 0.1, 0.1, 1))
        self.w.colorInfo4 = TextBox((-83, y+2, 40, 20), "Stroke", sizeStyle="small")
        self.w.strokeThickness = EditText((-40, y, 30, 20), "0", sizeStyle="small", callback=self.validateUserInputStrokeThickness)
        y = 195
        self.w.colorInfo3 = TextBox((10, y+2, 90, 20), "Random RGB", sizeStyle="small")
        self.w.randomFR = CheckBox((111, y, 20, 20), "", sizeStyle="mini", value=False)
        self.w.randomFG = CheckBox((125, y, 20, 20), "", sizeStyle="mini", value=False)
        self.w.randomFB = CheckBox((139, y, 20, 20), "", sizeStyle="mini", value=False)
        self.w.randomSR = CheckBox((171, y, 20, 20), "", sizeStyle="mini", value=False)
        self.w.randomSG = CheckBox((185, y, 20, 20), "", sizeStyle="mini", value=False)
        self.w.randomSB = CheckBox((199, y, 20, 20), "", sizeStyle="mini", value=False)
        self.w.randomBR = CheckBox((226, y, 20, 20), "", sizeStyle="mini", value=False)
        self.w.randomBG = CheckBox((240, y, 20, 20), "", sizeStyle="mini", value=False)
        self.w.randomBB = CheckBox((254, y, 20, 20), "", sizeStyle="mini", value=False)        
        y = 215
        self.w.transparencyInfo = TextBox((10, y+5, 90, 20), "Color Fade", sizeStyle="small")
        self.w.FTransparency = CheckBox((110, y, 50, 20), "Fill", sizeStyle="small", value=False)
        self.w.STransparency = CheckBox((155, y, 60, 20), "Stroke", sizeStyle="small", value=False)
        self.w.BTransparency = CheckBox((225, y, 50, 20), "BG", sizeStyle="small", value=False, callback=self.transparentBGUserInput)
        self.w.BGtransparentColor = ColorWell((260, y, 20, 20), color=NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 1, 1, 1), callback=self.colorWell1UserInput)
        self.w.BGtransparentColor.enable(False)

        y = 240       
        self.w.yShiftGlyphInfo = TextBox((10, y+5, 90, 20), "Y-Shift Glyph", sizeStyle="small")        
        self.w.yShiftGlyph = EditIntStepper((110, y, 60, 20), 100, sizeStyle='small')

        y = 250
        self.w.export = Button((10, y+20, -10, 20), "Export .gif", callback=self.draw, sizeStyle="regular")
        self.w.open()

    ### UI Callbacks

    def transparentBGUserInput(self, sender):
        if self.w.BTransparency.get() == 1:
            self.w.BGtransparentColor.enable(True)
        else:
            self.w.BGtransparentColor.enable(False)

    def colorWell1UserInput(self, sender):
        #print self.w.glyphFillColor.get()
        if self.w.fillLikeStroke.get() == 1:
            self.w.glyphStrokeColor.set(self.w.glyphFillColor.get())

    def colorWell2UserInput(self, sender):
        if self.w.fillLikeStroke.get() == 1:
            self.w.glyphFillColor.set(self.w.glyphStrokeColor.get())

    def validateUserInputSpeed(self, sender):
        try: 
            int(self.w.speed.get())
            if int(self.w.speed.get()) <= 0:
                self.w.speed.set(1)
            if int(self.w.speed.get()) > 10:
                self.w.speed.set(10)
        except ValueError:
            self.w.speed.set(1)        

    def validateUserInputPageHeight(self, sender):
        try: 
            int(self.w.pageHeight.get())
            if int(self.w.pageHeight.get()) <= 0:
                self.w.pageHeight.set(10)
        except ValueError:
            self.w.pageHeight.set(300)

    def validateUserInputMargin(self, sender):
        try: 
            float(self.w.canvasMargin.get())
        except ValueError:
            self.w.canvasMargin.set(1.2)

    def validateUserInputStrokeThickness(self, sender):
        try: 
            int(self.w.strokeThickness.get())
            if int(self.w.strokeThickness.get()) < 0:
                self.w.strokeThickness.set(0)
        except ValueError:
            self.w.strokeThickness.set(0)

    def FillLikeStroke(self, sender):
        if self.w.fillLikeStroke.get() == 1:
            self.w.glyphStrokeColor.set(self.w.glyphFillColor.get())



    def loadFontsFromFolder(self, sender):
        ### LOADING FONTS FROM FOLDER
        folder_imported_OTFs = getFolder()
        if folder_imported_OTFs != None:
            ### closing all previous opened fonts from folder! + clearing the output
            if len(self.loadedFontList) != 0:
                for f in self.loadedFontList:
                    f.close()
                self.loadedFontList = []      
            self.imported_files_folder = folder_imported_OTFs[0]
        else:
            return
        if self.imported_files_folder is not None:
            _imported_OTF_path = self.walk(self.imported_files_folder)
            if len(_imported_OTF_path) > 0:
                    for i, imported_OTF_path in enumerate(_imported_OTF_path):
                        progressBar = ProgressBar(title="opening font %s of %s" % (str(i+1), str(len(_imported_OTF_path))), label="...")
                        self.loadedFontList.append(OpenFont(imported_OTF_path, showUI=False))
                        progressBar.close()
        self.w.amountOfLoadedFonts.set(len(self.loadedFontList))
        
    def walk(self, folder):
        files = []
        names = os.listdir(folder)
        for n in names:
            p = os.path.join(folder, n)
            file_name, file_extension = os.path.splitext(n)
            if file_extension[1:] in ["ufo"]:
                files.append(p)
        return files
 


    def _colorRandomRGBList(self):
        ### randomization Check
        fillcolorRandomsRGB = [self.w.randomFR.get(), self.w.randomFG.get(), self.w.randomFB.get(), self.w.FTransparency.get()]
        strokecolorRandomsRGB = [self.w.randomSR.get(), self.w.randomSG.get(), self.w.randomSB.get(), self.w.STransparency.get()]
        backgroundcolorRandomsRGB = [self.w.randomBR.get(), self.w.randomBG.get(), self.w.randomBB.get(), self.w.BTransparency.get()]
        
        fillRandomValues = []
        for i, value in enumerate(fillcolorRandomsRGB):
            if value == 1:
                fillRandomValues.append(i)
        strokeRandomValues = []
        for i, value in enumerate(strokecolorRandomsRGB):
            if value == 1:
                strokeRandomValues.append(i)
        backgroundRandomsValues = []
        for i, value in enumerate(backgroundcolorRandomsRGB):
            if value == 1:
                backgroundRandomsValues.append(i)
                
        return fillRandomValues, strokeRandomValues, backgroundRandomsValues


    def _getTransparencyMultipliers(self):
        
        self.transparencyFactors = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2]
        
        extendFactorsBy = (len(self.w.glyphsInfo.get())*len(self.loadedFontList))*int(str(self.w.speed.get()))
        
        for i in range(1,1000):            
            if len(self.transparencyFactors) < extendFactorsBy:
                self.transparencyFactors = self.transparencyFactors+self.transparencyFactors
            else:
                pass
        return self.transparencyFactors


    def _convertNSColors(self, colorList):
        finalColorList = []
        for a in colorList:
            try:
                finalColorList.append(float(a))
            except ValueError:
                pass
        return finalColorList


    def _colorization(self, countForTransparency):
        ### transparency
        transparenyFactors = self._getTransparencyMultipliers()
        transpFactor = transparenyFactors[countForTransparency]
        
        ### randomization Check
        fillRandomValues = self._colorRandomRGBList()[0]
        strokeRandomValues = self._colorRandomRGBList()[1]
        backgroundRandomsValues = self._colorRandomRGBList()[2]

        ############ Fill COLOR
        colorList = str(self.w.glyphFillColor.get()).split(" ")
        fillColor = self._convertNSColors(colorList)

        finalGlyphFillcolor = []
        for i, value in enumerate(fillColor):
            if i in fillRandomValues:
                if i != 3:
                    finalGlyphFillcolor.append(value*random())
                    #transparency
                if i == 3:
                    finalGlyphFillcolor.append(transpFactor)
            else:
                finalGlyphFillcolor.append(value)
        finalGlyphFillcolor = map(float, finalGlyphFillcolor)
        
        ############ Stroke COLOR
        colorList = str(self.w.glyphStrokeColor.get()).split(" ")
        strokecolor = self._convertNSColors(colorList)

        finalStrokecolor = []
        for i, value in enumerate(strokecolor):
            if i in strokeRandomValues:
                if i != 3:
                    finalStrokecolor.append(value*random())
                #transparency
                if i == 3:
                    finalStrokecolor.append(transpFactor)                
            else:
                finalStrokecolor.append(value)
        finalStrokecolor = map(float, finalStrokecolor)

        ############ BG COLOR
        colorList = str(self.w.backgroundColor.get()).split(" ")
        bgcolor = self._convertNSColors(colorList)

        finalBGcolor = []
        for i, value in enumerate(bgcolor):
            if i in backgroundRandomsValues:
                if i != 3:
                    finalBGcolor.append(value*random())
                #transparency
                if i == 3:
                    finalBGcolor.append(transpFactor) 
            else:
                finalBGcolor.append(value)
        finalBGcolor = map(float, finalBGcolor)
        
        return finalGlyphFillcolor, finalStrokecolor, finalBGcolor



    def _drawGlyph(self, glyph):
        
        path = glyph.naked().getRepresentation("defconAppKit.NSBezierPath")
        drawPath(path)
        # draw bounding box
        #strokeWidth(0) 
        #fill(1,1,1,0.5)
        #rect(glyph.box[0],glyph.box[1],glyph.box[2]-glyph.box[0],glyph.box[3]-glyph.box[1])

    
    def glyphNamesInputCheck(self):
        glyphNames = str(self.w.glyphName.get()).replace(" ","")
        if "/" in glyphNames:
            glyphNames = [x for x in glyphNames.split("/") if x]
        else:
            glyphNames = list(glyphNames)
        return glyphNames

    def draw(self, sender):

        if len(self.loadedFontList) == 0:
            self.w.amountOfLoadedFonts.set("!!! --->")
            return
        
        glyphNames = self.glyphNamesInputCheck()
        
        #pageWidth = self.w.pageWidth.get()
        pageHeight = int(self.w.pageHeight.get())
        pageWidth = pageHeight
        extraSpace = float(self.w.canvasMargin.get())

        countForTransparency = 0
        
        newDrawing()

        tickCount = (len(glyphNames)*int(str(self.w.speed.get())))*len(self.loadedFontList)
        tick = 0 
        progressBar = ProgressBar(title="", ticks=tickCount, label="generating .gifs ...")

        for i, glyphName in enumerate(glyphNames):

            tick = tick+1
            progressBar.tick(tick)
            
            for thisFont in self.loadedFontList:
                
                tick = tick+1
                progressBar.tick(tick)
                
                countForTransparency += 1
                
                UPM = thisFont.info.unitsPerEm
                descender = thisFont.info.descender
                #xHeight = thisFont.info.xHeight
                #capHeight = thisFont.info.capHeight
                #ascender = thisFont.info.ascender
                
                #pointSize = 200
                sc = pageHeight / ((UPM) * extraSpace)

                
                for index in range(int(str(self.w.speed.get()))):
                    
                    tick = tick+1
                    progressBar.tick(tick)
                    
                    newPage(pageWidth, pageHeight)

                    ############ START Drawing BG
                    save()
                    # getting colors (including Random if used)
                    glyphFillColor = self._colorization(countForTransparency)[0]
                    glyphStrokeColor = self._colorization(countForTransparency)[1]
                    backgroundColor = self._colorization(countForTransparency)[2]
                                     
                    # draw background 
                    # draw additional BLACK background if Background Transparency fade is active
                    if self.w.BTransparency.get() == 1: 
                        fill(self.w.BGtransparentColor.get())
                        rect(0,0, pageWidth, pageWidth)
                    else:
                        fill(1,1,1,1)
                        rect(0,0, pageWidth, pageWidth)
                        
                    fill(*backgroundColor) 
                    rect(0,0, pageWidth, pageWidth)
                    ############### END Drawing BG
            
                    ## ONLY IF THE GLYPH EXISTS IN FONT: DRAW GLYPH                   
                    if glyphName in thisFont.keys():
                        glyph = thisFont[glyphName]

                        ############ START Glyph(s)
                        # set scale/shift for drawing glyph(s) to pagesize 
                        scale(sc)
                        translateY = -descender+(self.w.yShiftGlyph.get())
                        translateX = ((pageHeight / sc) - glyph.width) / 2
                        translate(translateX,translateY)
                        # set colors for fill and stroke and Stroke thickness of Glyph Drawing
                        stroke(*glyphStrokeColor)
                        strokeWidth(int(str(self.w.strokeThickness.get())))
                        fill(*glyphFillColor)
                        # drawGlyph
                        self._drawGlyph(glyph)
                    ## if the glyph doesn't exist: DRAW ONLY BACKGROUND
                    else:
                        print (glyphName, "glyph doesn't exist in one of the fonts!")
                                    
                    restore()
                    ############### END Glyph(s)

                    ############### START title and time stamp
                    stamp = self.AddStamp(thisFont)
                    if len(stamp) == 0:
                        pass
                    else:
                        save()
                        x, y, w, h = 0, 5, int(self.w.pageHeight.get()), 10
                        fill(self.w.titleColor.get())
                        #fill(1, 0, 0, 0.2)
                        fontSize(7)
                        overflow = textBox("  ".join(stamp).strip("  "), (x, y, w, h), align="center")
                        restore()
                    ############### END title and time stamp
                       
        exportstring = str(os.path.expanduser('~'))+"/Desktop/"+glyphName+".gif"
        
        ## check if file exists - in order not to write a new file instead of overwriting it.
        PATH = os.path.expanduser('~') + "/Desktop/"+glyphName+".gif"
        if path.isfile(PATH) == True:
            now = datetime.datetime.now()
            date = "_%d-%d-%d_%dh-%dm-%ds" % (now.day, now.month, int(str(now.year)[2:]), now.hour, now.minute, now.second)
            exportstring = str(os.path.expanduser('~'))+"/Desktop/"+glyphName+date+".gif"

        
        saveImage(exportstring)
        endDrawing()
        
        progressBar.close()

    def AddStamp(self, thisFont):
        stamp = []
        if len(self.w.title.get()) != 0:
            stamp.append(str(self.w.title.get()))
        if self.w.timestamp.get() == 1:
            modified = time.strftime('%d/%m/%Y', time.gmtime(os.path.getmtime(thisFont.path)))
            hourAndMinute = time.strftime('%H:%M', time.gmtime(os.path.getmtime(thisFont.path)))
            finalModificationDate = modified[:-4]+modified[-2:]+"  "+hourAndMinute
            stamp.append(finalModificationDate)
        return stamp

           
GlyphGiffer()

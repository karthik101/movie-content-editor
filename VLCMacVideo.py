#! /usr/bin/python

#import vlc
import sys
from PyQt4 import QtGui, QtCore
from Foundation import *
from AppKit import NSView
from Quartz import *
from CoreFoundation import *
import objc
from objc import YES, NO, NULL
import sip

#objc.loadBundle("VLCKit",globals(),bundle_path=objc.pathForFramework("/Users/slloyd/Downloads/vlc/projects/macosx/framework/build/Debug/VLCKit.framework"))
d='/Users/slloyd/Downloads/vlc/projects/macosx/framework/build/vlc_build_dir'
d='/Applications/VLC.app/Contents/MacOS'
TIME_RES = 10000

"""The ideal way to do this would be to use the objc.loadBundle method to import the VLCKit framework already built for VLC.
This would ideally build Python wrappers around all of the custom VLC objects we need and allow us to create them in Python
directly without having to define the classes ourselves. I wasn't able to get this to work, so for now, I've defined just one
of these classes myself (the VLCVideoView class) to allow us to have something that works"""



"""Objective C class defined in Python. Lots of signatures to tell objc which methods to call. Some of them are apparently 
unnecessary, but it wasn't clear to me which were needed and which weren't, so I left them all in. I suspect that they are
unnecessary when overriding methods of a parent class, but I haven't confirmed that."""
class VLCVideoView(NSView):

    objc.synthesize('delegate', copy=True)
    objc.synthesize('backColor',copy=True)
    objc.synthesize('hasVideo', copy=True)
    
    #Initialize the VLCVideoView object. If running in 64-bit on SnowLeopard, it expects a CGRect rather than an NSRect
    @objc.signature("@@:{_NSRect={_NSPoint=ff}{_NSSize=ff}}")
#    @objc.signature("@@:{CGRect={CGPoint=dd}{CGSize=dd}}")
    def initWithFrame_(self,rect):
        self = super(VLCVideoView, self).initWithFrame_(rect)
        if self is None: return None
        self._delegate = None
        self._backColor = NSColor.blackColor()
        self._fillScreen = NO
        self._hasVideo = NO
        self.setStretchesVideo_(NO)
        self.setAutoresizesSubviews_(YES)
        
        #probably need to figure out how to assign an appropriate layoutManager, but for now it's None
        self.layoutManager =  None
        return self
    
    @objc.signature("@@:")
    def backColor(self):
        return self._backColor
    
    @objc.signature("c@:")        
    def hasVideo(self):
        return self._hasVideo
    
    @objc.signature("@@:")
    def delegate(self):
        return self._delegate
    
    @objc.signature("v@:")    
    def dealloc(self):
        self._delegate = None
        self._backColor = None
        if self.layoutManager:
            self.layoutManager.release()
        super(VLCVideoView,self).dealloc()
        
    @objc.signature("v@:{_NSRect={_NSPoint=ff}{_NSSize=ff}}")    
    def drawRect_(self,aRect):
        self.lockFocus()
        self.backColor().set()
        NSRectFill(aRect)
        self.unlockFocus()
    
    @objc.signature("c@:")        
    def isOpaque(self):
        return YES
        
        
    @objc.signature("c@:")
    def fillScreen(self):
        if self.layoutManager:
            return self.layoutManager.fillScreenEntirely()
        return NO
        
    @objc.signature("v@:c")
    def setFillScreen_(self,fillScreen):
        #need to implement
        return NO


    @objc.signature("v@:{CALayer=#{_CALayerIvars=iII^{__CFArray}@^{_CALayerState}^{_CALayerState}^{_CALayerAnimation}[3^{_CALayerTransaction}]}}")
    def addVoutLayer_(self, aLayer):
        CATransaction.begin()
        self.setWantsLayer_(YES)
        rootLayer = self.layer()
        aLayer.name = u"vlcopengllayer"
        if self.layoutManager:
            self.layoutManager.setOriginalVideoSize_(aLayer.bounds().size())
        
        rootLayer.setLayoutManager_(layoutManager)
        rootLayer.insertSublayer_atIndex_(aLayer, 0)
        aLayer.setNeedsDisplayOnBoundsChange_(True)
        
        CATransaction.commit()
        self._hasVideo = YES
        
    @objc.signature("v@:@")    
    def removeVoutLayer_(self, voutLayer):
        CATransaction.begin()
        voutLayer.removeFromSuperlayer()
        CATransaction.commit()
        self._hasVideo = NO
        
    @objc.signature("v@:c")
    def setStretchesVideo_(self,value):
        self._stretchesVideo = value;
        
           
    @objc.signature("v@:@")    
    def addVoutSubview_(self, aView):
        aView.setFrame_(self.bounds())
        self.addSubview_(aView)
        aView.setAutoresizingMask_((NSViewHeightSizable|NSViewWidthSizable))

    @objc.signature("v@:@")
    def removeVoutSubview_(self, view):
        #not doing anything right now
        pass
        
    @objc.signature("c@:")    
    def stretchesVideo(self):
        return self._stretchesVideo
        
    @objc.signature("v@:@")    
    def didAddSubview_(self, subview):
        pass
#        NSLog(u'A subview was added')
        
#    def __del__(self):
#        self._delegate = None
#        self._backColor = None
#        self.layoutManager = None

#app = QtGui.QApplication(sys.argv)


"""This is the QtGui widget that will actually hold our video NSView video object defined above"""
class MacVideo(QtGui.QWidget):
    
    def __init__(self, parent=None):
        super(MacVideo,self).__init__(parent)    
        self.videoLayout = QtGui.QVBoxLayout()
        self.videoLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.videoLayout)
        
        
    def createVideoWindow(self,media_player):    
        videoWidget = QtGui.QMacCocoaViewContainer(None)
        self.videoLayout.addWidget(videoWidget)
        videoView = VLCVideoView.alloc().init()
        videoWidget.setCocoaView(sip.voidptr(objc.pyobjc_id(videoView)))
        media_player.set_nsobject(objc.pyobjc_id(videoView))
        videoView.release()
        
        
    

class MacPlayer(QtGui.QWidget):

    
    def __init__(self, player, parent=None):
        super(MacPlayer,self).__init__(parent)
        self.media_player = player
        self.instance = self.media_player.get_instance()
#        vlc_args = ("-I dummy --verbose=1 --ignore-config --plugin-path=" + d + "/modules --vout=minimal_macosx --opengl-provider=minimal_macosx")
#        self.instance = vlc.Instance(vlc_args)
#        self.media_player = self.instance.media_player_new()
#        self.media_descr = None
        self.videoWidget = None
        buttonLayout = QtGui.QHBoxLayout()
        mainLayout = QtGui.QVBoxLayout()
        videoLayout = QtGui.QHBoxLayout()
        
        mainLayout.setContentsMargins(0,0,0,0)
        videoLayout.setContentsMargins(0,0,0,0)
        buttonLayout.setContentsMargins(0,0,0,0)
        pauseButton = QtGui.QPushButton('Play/Pause')
        pauseButton.setCheckable(True)
        pauseButton.clicked.connect(self.play_pause)
                
        stopButton = QtGui.QPushButton('Stop')
        stopButton.clicked.connect(self.stop)
        
        buttonLayout.addWidget(pauseButton)
        buttonLayout.addWidget(stopButton)
        

        self.positionSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.positionSlider.setMaximum(TIME_RES)
        self.positionSlider.setMinimum(0)
        self.positionSlider.setToolTip("Video position")

        buttonLayout.addWidget(self.positionSlider)


        volumeSlider = QtGui.QSlider(QtCore.Qt.Vertical)
        volumeSlider.setMaximum(100);
        volumeSlider.setMinimum(0);
        volumeSlider.setToolTip("Volume")



        slidersLayout = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight)
        slidersLayout.addWidget(volumeSlider)
        slidersLayout.addWidget(self.positionSlider)

        volumeSlider.setSliderPosition(self.instance.audio_get_volume())
        volumeSlider.setTracking(True)
        self.positionSlider.setTracking(True)
        self.poller = QtCore.QTimer(self)
        self.poller.timeout.connect(self.updateInterface)
        volumeSlider.valueChanged.connect(self.changeVolume)
        self.positionSlider.sliderPressed.connect(self.positionChanging)
        self.positionSlider.sliderReleased.connect(self.positionChanged)
        
        self.isPlaying = False
        self.poller.start(100)
        self.setLayout(mainLayout)
#        self.load()

        videoWidget = MacVideo()
        videoWidget.createVideoWindow(self.media_player)
        videoLayout.addWidget(volumeSlider)
        videoLayout.addWidget(videoWidget)
        mainLayout.addLayout(videoLayout)
        mainLayout.addLayout(buttonLayout)
        self.resize(640,480)
        self.show()
        

    
            
               
#    def load(self):
#        if self.media_descr:
#            vlc.media_release(self.media_descr)
#        self.media_descr = self.instance.media_new("/Users/slloyd/movieEditor/XCode/movieEditor/Wildlife.wmv")
#        self.media_descr = self.instance.media_new("/Users/slloyd/movieEditor/The_Sign_Of_Four.m4v")
#        self.media_player.set_media(self.media_descr)
        
        

        
        
    def play(self):
        self.media_player.play()
        self.show()
#        if self.videoWidget:
#            self.show()
#            self.videoWidget.show()
#        self.show()
        self.isPlaying = True


# right now if you try to stop the player on a mac, it crashes the program
    def stop(self, checked):
#        if self.videoWidget:
#            self.videoWidget= None
#        if self.media_player.get_media() is not None and self.media_descr is not None:
#            self.media_player.stop()
#        self.isPlaying = False
#        self.media_player.stop()
        return
            
    def changeVolume(self, newVolume):
        self.instance.audio_set_volume(newVolume)
        
    def positionChanging(self):
        self.poller.stop()
    
    def positionChanged(self):
        self.changePosition()
        self.poller.start(100)
        
    def play_pause(self,checked):
        if checked or self.media_player.is_playing(): 
            self.media_player.pause()
        else:
            self.media_player.play()
    
    def changePosition(self, newPosition=None):
        if not self.media_player.is_playing():
            return
        if self.media_player.get_media() is None:
            return
        newPosition = self.positionSlider.sliderPosition()
#        NSLog(str(newPosition))
        self.media_player.set_position(float(newPosition)/float(TIME_RES))
        
        
        
    def updateInterface(self):
        if not self.media_player.is_playing():
            return
        if self.media_player.get_media() is None:
            return
#        NSLog(u'Updating interface')
        a = self.media_player.get_position()
        self.positionSlider.setValue(self.media_player.get_position()*TIME_RES)
        

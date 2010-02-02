import vlc
import time
import ctypes
import sys
import threading


DEBUG = True

# TODO: not using any of these callback methods right now
callbackmethod=ctypes.CFUNCTYPE(None, vlc.Event, ctypes.c_void_p) 

@callbackmethod
def func(event,data):
    sendDebug("hi")
    sys.exit(0)


def sendDebug(msg, newline=1):
    global DEBUG
    if DEBUG:
        if newline:
            print ' '
        print msg

# TODO: remove hard-coded path  
path = "C:\Users\YourName\Documents\Movie Editor\"

# ------ pre-process sections to mute -----------
f = open(path + "mute.txt")
i = 0
start = []
finish = []
for line in f:
    separate = line.strip().split()
    start.append(float(separate[0])*1000)
    finish.append(float(separate[1])*1000)
# ------------------------------------------------

# -------- Load and start movie ----------------
instance = vlc.Instance()
#instance.add_intf(None)
media = instance.media_new(path + "Wildlife.wmv")
player = instance.media_player_new()
player.set_media(media)
player.play()
mc = vlc.MediaControl(instance)
# -------------------------------------------------



# pause for one second to let player load
time.sleep(1)

# turn on subtitles
#player.video_set_spu(1)
player.video_set_subtitle_file(path + "panda_edit.srt');

# (temporary) skipping over intro to get to good stuff
player.set_time(35000)

startTime = time.time()*1000 - player.get_time()

event = vlc.EventType.MediaPlayerTimeChanged;

eventManage = player.event_manager()
#eventManage.event_attach(event,func,None)

def mute(instance,tWait):
    instance.audio_set_mute(1)
    time.sleep(tWait)
    instance.audio_set_mute(0)
    sendDebug("muted")
    return

def skip(player,tSkip):
    player.set_time(player.get_time() + long(tSkip*1000))
    sendDebug("skipped")
    return

def stop(player):
    sendDebug("done")
    player.stop()
    sys.exit(0)

for i in range (0,len(start)):
    tWait = (finish[i]-start[i])/1000
    arg1 = (instance,tWait)
    t1 = threading.Timer((start[i]-player.get_time())/1000,mute,arg1)
    t1.start()

#arg2 = (player,)
#t2 = threading.Timer(80-player.get_time()/1000,stop,arg2)
#t2.start()

# this is temporary just so player doesn't go on for long time
time.sleep(80-player.get_time()/1000)
stop(player)


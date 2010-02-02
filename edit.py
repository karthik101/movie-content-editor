import vlc
import sys
import time
import threading

DEBUG = True

def sendDebug(msg, newline=1):
    global DEBUG
    if DEBUG:
        if newline:
            print ' '
        print msg

# ------ pre-process sections to mute -----------
try:
    f = open('mute.txt','r')
    i = 0
    start = []
    finish = []
    for line in f:
        separate = line.strip().split()
        start.append(float(separate[0])*1000)
        finish.append(float(separate[1])*1000)
    f.close()
except IOError:
    print("File not found")
    sys.exit()
# ------------------------------------------------

# -------- Load and start movie ----------------
instance = vlc.Instance()
instance.add_intf(None)
media = instance.media_new("Kung Fu Panda.m4v")
player = instance.media_player_new()
player.set_media(media)
player.play()
#mc = vlc.MediaControl(instance)
# -------------------------------------------------

# I use this for testing with Panda
player.set_time(35000)

# turn on subtitles
player.video_set_subtitle_file("panda_edit.srt")

# ------ defined functions for editing ----------
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
    player.stop()
    sys.exit()
# --------------------------------------------

# ---- initiate threads for the edit commands -----
for i in range (0,len(start)):
    tWait = (finish[i]-start[i])/1000
    arg1 = (instance,tWait)
    t1 = threading.Timer((start[i]-player.get_time())/1000,mute,arg1)
    t1.start()
# -----------------------------------------------

# this is temporary just so player doesn't go on for long time
time.sleep(80-player.get_time()/1000)
stop(player)



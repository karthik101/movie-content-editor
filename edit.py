import vlc
import sys
import time
from threading import Thread
from subtitle import readSrt
from mergeCommands import merge

DEBUG = True

def sendDebug(msg, newline=1):
    global DEBUG
    if DEBUG:
        if newline:
            print ' '
        print msg

# For now I need to define the path, I commented out so it should work for you guys
path = 'C:\Users\Kimberly\Desktop\Andrew\Movie Editor\\'
#path = ''


badwordsFile = "badwords.txt"
movieFile = "Kung Fu Panda.m4v"
subtitleFile = "panda.srt"
customFile = "panda_custom.txt"

# ------  create edited subtitle file ------
subtitleEdit = readSrt(path,subtitleFile,badwordsFile)
# --------------------------------------------

# ------- create list of commands ----------
commands = merge(path,customFile)
# -----------------------------------------

# ------ separate commands for convenience -----
cType = []
sTime = []
fTime = []
for item in commands:
    cType.append(int(item[0])) # command type
    sTime.append(float(item[1])*1000) # command start time in ms
    fTime.append(float(item[2])*1000) # command finish time in ms
# -------------------------------------------


# -------- Load and start movie ----------------
instance = vlc.Instance()
instance.add_intf("qt")
media = instance.media_new(path + movieFile)
player = instance.media_player_new()
player.set_media(media)
player.play()
# -------------------------------------------------

# I use this for testing with Panda
player.set_time(33000)

# turn on subtitles
player.video_set_subtitle_file(path + subtitleEdit)


# ------------- subclass off of Thread ---------------
class editThread (Thread):
        
    # right now this only handles mute and will need to include a
    # check in case it is interrupted by another thread.  
    def run ( self ):
        for i in range (0,len(sTime)):
            
            # sleep until time for next action
            tSleep = (sTime[i] - player.get_time())/1000
            if (tSleep > 30):
                time.sleep(tSleep-30)
                tSleep = (sTime[i] - player.get_time())/1000
            time.sleep(tSleep)
            
            # perform action
            if (cType[i] == 0):
                onMute()
            elif (cType[i] == 1):
                offMute()
            elif (cType[i] == 2):
                skip(fTime[i] - sTime[i])
                
        return
# ------------------------------------------------------

# ------- methods -------------------------
def onMute ():
    instance.audio_set_mute(1)
    return
    
def offMute ():
    instance.audio_set_mute(0)
    return

def skip(tSkip):
    player.set_time(player.get_time() + long(tSkip))
    return

def stop(player):
    player.stop()
    sys.exit()
# --------------------------------------------

thread1 = editThread()
thread1.start()

print player.get_time()
# this is temporary just so player doesn't go on for long time
time.sleep(80-player.get_time()/1000)
stop(player)



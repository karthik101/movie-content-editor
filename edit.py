import vlc
import sys
import time
from threading import Thread

DEBUG = True

def sendDebug(msg, newline=1):
    global DEBUG
    if DEBUG:
        if newline:
            print ' '
        print msg

# For now I need to define the path, I commented out so it should work for you guys
#path = 'C:\Users\Kimberly\Desktop\Andrew\Movie Editor\movie-editor'
path = '.'

# ------ pre-process sections to mute -----------
try:
    f = open(path + '\mute.txt','r')
    i = 0
    begin = []
    finish = []
    for line in f:
        separate = line.strip().split()
        begin.append(float(separate[0])*1000)
        finish.append(float(separate[1])*1000)
    f.close()
except IOError:
    print("File not found")
    sys.exit()
# ------------------------------------------------

# -------- Load and start movie ----------------
instance = vlc.Instance()
#instance.add_intf(None)
media = instance.media_new(path + "\Kung Fu Panda.m4v")
player = instance.media_player_new()
player.set_media(media)
player.play()
# -------------------------------------------------

# I use this for testing with Panda
player.set_time(35000)

# turn on subtitles
player.video_set_subtitle_file(path + "\panda_edit.srt")


# ------------- subclass off of Thread ---------------
class editThread (Thread):

    # override default behavior
    def __init__ (self,player,begin,finish):
        Thread.__init__ ( self )
        self.player = player
        self.begin = begin
        self.finish = finish
        
    # right now this only handles mute and will need to include a
    # check in case it is interrupted by another thread.  
    def run ( self ):
        for i in range (0,len(begin)):
            tAction = (finish[i] - begin[i])/1000
            
            # sleep until time for next action
            tSleep = (begin[i] - player.get_time())/1000
            if (tSleep > 30): # don't know that 30 sec is the right number per se
                time.sleep(tSleep-30)
                tSleep = (begin[i] - player.get_time())/1000
            time.sleep(tSleep)
            
            mute(tAction)
        return
# ------------------------------------------------------

# ------- methods -------------------------
def mute (tMute):
    instance.audio_set_mute(1)
    time.sleep(tMute)
    instance.audio_set_mute(0)
    return
    

def skip(tSkip):
    player.set_time(player.get_time() + long(tSkip*1000))
    sendDebug("skipped")
    return

def stop(player):
    player.stop()
    sys.exit()
# --------------------------------------------

thread1 = editThread(player, begin, finish)
thread1.start()

# this is temporary just so player doesn't go on for long time
time.sleep(80-player.get_time()/1000)
stop(player)



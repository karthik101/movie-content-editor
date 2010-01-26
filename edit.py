import vlc
import time

# ------ pre-process sections to mute -----------
f = open('C:\Users\Kimberly\Desktop\Movie Editer\mute.txt')
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
media = instance.media_new("C:\Users\Kimberly\Movies (Full Size)\Kung Fu Panda\VIDEO_TS\VTS_10_1.vob")
player = instance.media_player_new()
player.set_media(media)
player.play()
# -------------------------------------------------

# pause for one second to let player load
time.sleep(1)

# turn on subtitles
#player.video_set_spu(1)
player.video_set_subtitle_file('C:\Users\Kimberly\Desktop\Movie Editer\panda_edit.srt');

# (temporary) skipping over intro to get to good stuff
player.set_time(20000)


# ------- check for sections to mute (& skip - not implemented) ----------
while player.is_playing():
    
    if player.get_time() > start[i] and player.get_time() < finish[i]:
        instance.audio_set_mute(1)
    else:
        instance.audio_set_mute(0)

    if player.get_time() > finish[i]:
        i+=1

    # (temporary) to prevent movie from going on forever
    if player.get_time() > 80000:
        player.stop()
# --------------------------------------------------------

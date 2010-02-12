'''
Created on Feb 11, 2010

@author: S. Andrew Ning
'''

import sys
import operator

def merge(path,custom):
    """
    Merges an automatically generate mute file with a custom file containing mute/skip commands.
    
    @param path - path to the files
    @param custom - a custom edit file
    @return a list of tuples containing commands for vlc to execute
    """
    
    # ------ open files --------
    try:
        fMute = open(path + "mute.txt", 'r')
        fCustom = open(path + custom,'r')
    except IOError:
        print("File not found") #TODO: add a more descriptive error
        sys.exit()
    # ---------------------------
    
    # -------- commands ------------
    mute = -1 # mute start and finish (only used for convenience in this module)
    muteS = 0 # mute start
    muteF = 1 # mute finish
    skip = 2  
    
    commands = []
    # -----------------------------
    
    # ---- read in automatically generate mute times -----
    for line in fMute:
        separate = line.strip().split()
        muteT = (mute,float(separate[0]),float(separate[1]))
        commands.append(muteT)
    fMute.close()
    # ----------------------------------------------
    
    # ----- read in custom file -----------
    for line in fCustom:
        if (line == "\n"): break
        separate = line.strip().split()
        command = separate[0].lower()
        if (command in ("mute","m")):
            muteT = (mute,float(separate[1]),float(separate[2]))
            commands.append(muteT)
        elif (command in ("skip","s")):
            skipT = (skip,float(separate[1]),float(separate[2]))
            commands.append(skipT)
    # -------------------------------------
    
    # sort by start time
    commands.sort(key = operator.itemgetter(1))
    
    #TODO: i need to test all of these cases some more
    # ---- remove redundancies and collisions ------
    prev = commands[0]
   
    idx = 1
    while (idx < len(commands)):
        prev = commands[idx-1]
        curr = commands[idx]
        
        # rename for readibility
        cmd1 = prev[0]
        cmd2 = curr[0]
        start1 = prev[1]
        start2 = curr[1]
        finish1 = prev[2]
        finish2 = curr[2]
        
        # check for swallowed commands
        if (cmd1 == cmd2 and finish2 < finish1):
            commands.remove(curr)
            idx -= 1
        
        # check for overlapping commands
        elif (cmd1 == cmd2 and start2 < finish1): 
            commands[idx][1] = commands[idx-1][1]
            commands.remove(prev)
        
        # check for mute inside of a skip
        elif (cmd1 == skip and cmd2 == mute and finish2 < finish1):
            commands.remove(curr) # remove the mute
            idx -= 1
            
        # for skip inside mute - don't need to do anything.
        
        # check for skip overlapping a mute
        elif (cmd1 == mute and cmd2 == skip and start2 < finish1):
            commands[idx-1][2] = commands[idx][1] - .1; #TODO: figure out what the right offset should be
        
        # check for mute overlapping a skip
        elif (cmd1 == skip and cmd2 == mute and start2 < finish1):
            commands[idx][1] = commands[idx-1][2] + .1; #TODO: same here
        
        idx +=1;
    # ----------------------------------------------
    
    # ------- separate mute commands to begin and end -------
    newCommands = []
    for c in commands:
        if (c[0] == mute):
            sMuteT = (muteS,c[1],0)
            fMuteT = (muteF,c[2],0)
            newCommands.append(sMuteT)
            newCommands.append(fMuteT)
        else: # skips remained un-modified
            newCommands.append(c)
    # ------------------------------------------------------
    
    # re-sort
    newCommands.sort(key = operator.itemgetter(1))
    
    return newCommands

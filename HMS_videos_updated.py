#######################################
### video task HMS ###
### CNLab                           ###
### JULY 2019                        ###
### cscholz     ###
#######################################

############
# HMS: Video Task
# Outline
# exposure period
############

############
## PREP
############

# Import PsychoPy
import csv, math, sys
import pdb

from psychopy import visual, os, core, gui, event, logging, microphone, data, sound
from psychopy.hardware.emulator import launchScan

####### SET UP

full_screen = 'n' #y/n
DEBUG = False
EMULATE = False
COUNT_DOWN_DURATION = 3
ONE_COUNT_DURATION = 1

                                 
# Prompt for subjID and Run
subjDlg = gui.Dlg(title="Video Task")
subjDlg.addField('Enter Participant ID:')
subjDlg.show()

if gui.OK:
    subj_id = subjDlg.data[0]
    if(not subj_id):
        print("You need to enter a subject ID! Please consult the participant folder for the correct ID.")
        sys.exit()
else:
    sys.exit()
    

# Logs
expdir = os.getcwd()
logdir = '%s/logs' % (expdir)
log_filename = 'logs/%s.csv' % (subj_id)

log_file = logging.LogFile("%s/%s.log" % (logdir, subj_id),  level=logging.DATA, filemode="w")


# Screen setup
win = visual.Window([1200,800],   #1080,762], #[800,600], ###1920,1080], 
                monitor="testMonitor", 
                fullscr=False, #full_screen, 
                units='deg') #,
                #rgb=(-0.8,-08,-0.8))              

ready_screen = visual.TextStim(win, text="Ready..... \n\n (Press 't' to continue)", height=1.5, color="#FFFFFF")
                               # run-ending screen
run_end_screen = visual.TextStim(win, text="The session has finished (Press 'SPACE' to exit)", height=1.5, color="#FFFFFF")

globalClock = core.Clock()

videoPath = 'videos/Video Clips/running.mp4'
#pdb.set_trace()
mov = visual.MovieStim3(win, videoPath,
                       size = (1200, 800) , #800,600), #size=(960,540),
                       pos=[0, 0],
                       flipVert=False,
                       flipHoriz=False,
                       loop=False)
                       
##Rating screen
rating_screen = visual.TextStim(win, text='How effective was this commercial?', pos=(0,3), color="#FFFFFF", colorSpace=(0,0,0), height=1.75, wrapWidth=20)
button_labels = { '1': 0, '2': 1, '3': 2, '4': 3, '5': 4 }

## .keys gives you the first element of a pair in a dictionairy (the second is called value) - so button_labels.keys()
buttons = button_labels.keys()

anchor1 = visual.TextStim(win, text='Not \nat all', pos=(-8,-2), height=1)
anchor5 = visual.TextStim(win, text='Very \nmuch', pos=(8,-2), height=1)

ratingStim=[]

xpos = [-8, -4, 0, 4, 8]

for rating in (1,2,3,4,5):
    ratingStim.append(visual.TextStim(win, text='%i' % rating, pos=(xpos[rating-1],-4.2), height=1))
    


# Get playing order from PSA_retrans task
stims=[ row for row in csv.DictReader(open('stims_test.csv', 'rU'),delimiter=',')]

trials = data.TrialHandler(stims, 1, method='random')

#pdb.set_trace()

# RUN TASK
# display ready screen and wait for 'T' to be sent to indicate scanner trigger
ready_screen.draw()
win.flip()
event.waitKeys(keyList='t')

# reset globalClock
globalClock.reset()
logging.log(level=logging.DATA, msg='******* START (trigger from scanner) - *******')

localClock = core.Clock()  

for tidx, trial in enumerate(trials):

    # Count down 3 seconds---------------------------------    
    count = 1
    
    while count <= COUNT_DOWN_DURATION:
        localClock.reset()
        # pdb.set_trace()
        while localClock.getTime() < ONE_COUNT_DURATION:
            count_text = (COUNT_DOWN_DURATION - count) + 1 # count: 3, 2, 1
            counter = visual.TextStim(win,text=count_text, height=5, color="#FFFFFF") # Show the count down (seconds)
            counter.draw()
            win.flip()

        count += 1

    # ---------------------------------
    ## Reset rating scale color
    for rate in ratingStim:
        rate.setColor('#FFFFFF')
    
    localClock.reset()
    # pdb.set_trace()
    videoFilePath = trial['path']
    
    #mov._reset()
    mov.loadMovie(videoFilePath)
    #mov._createAudioStream()
    mov_length = mov.duration
    

    start_time = localClock.getTime()
    video_onset_time = globalClock.getTime()
    trials.addData('video_onset', video_onset_time)

    logging.log(level=logging.DATA, msg="current video path: %s - " % (videoFilePath))
    
    mov.play() 
    
    while localClock.getTime() <  start_time+mov_length: 
        mov.draw()
        win.flip()
        
        if event.getKeys(['escape']):  # this is to be able to interrupt
           trials.saveAsText(fileName=log_filename)
           win.close()  
           core.quit()
     
    # Present Rating Screen
    ## Clear Stuff from previous block and set up for new one
                
    event.clearEvents()
    keypress = None
    rt = None
        
    curTime=localClock.getTime()
    startTime=curTime
    
    rating_q_onset=globalClock.getTime()
    trials.addData('rating_question_onset', rating_q_onset)
    
    while curTime < (3.0+startTime):
        rating_screen.draw()
        anchor1.draw()
        anchor5.draw()
        for resp in ratingStim:
            resp.draw()
        win.flip()
        curTime=localClock.getTime()
        
        resp = event.getKeys(keyList = buttons)
                        
        if keypress==True:
            pass
        else:
            if len(resp) > 0 : 
                resp_value = button_labels[resp[0]]
                ratingStim[resp_value].setColor('red')
                keypress=True
                trials.addData('rating', resp_value)
                trials.addData('rating_rt', localClock.getTime() - startTime)
                
    trial2=trial.pop('vidID')
    # pdb.set_trace()
    # print('video path: '+ trial['path'])
    # Logging: end of the movie
    logging.log(level=logging.DATA, msg='******* END movie %i *******' % tidx)

    # pdb.set_trace()

    #logging.log(level=logging.DATA, msg='PresentMovie:\t{}\tDuration:\t{}\tOnset:\t{}\tOnsetTR:\t{}\tOffsetTR:\t{}'.format(trial['content'], (end_time - start_time), globalClock.getTime(), curr_onset_tr, curr_offset_tr ))
    mov.stop()   
    
# Logging: Send END log event
logging.log(level=logging.DATA, msg='******* END the whole session *******')
logging.flush()
#pdb.set_trace()
#trials.saveAsText(log_filename, delim=',')
trials.saveAsWideText(log_filename)
# Show the run-ending slide
run_end_screen.draw()
win.flip()
event.waitKeys(keyList=('space'))  

# pdb.set_trace()
win.close()
core.quit()







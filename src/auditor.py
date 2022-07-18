#! /usr/bin/python3
"""
    File: auditor.py:
    See changelog
    Date: Sun, 17/07/2022
    Author: Coolbrother

"""

import warnings
import os, sys
from os import path
import curses
curses.initscr()
import audimixer as aumix

#------------------------------------------------------------------------------

### brouillon pour effacer
DEBUG =1 
# float equality
_epsilon = 0.000001
curdir = path.dirname(__file__) # directory for the current script
_basedir = path.dirname(curdir) # base directory for the application
_mediadir = path.join(_basedir, "media")

def debug(msg="", title="", bell=True):
    if DEBUG:
        print("%s: %s" %(title, msg))
        if bell:
            curses.beep()
    
#------------------------------------------------------------------------------

class Auditor(object):
    """ 
    main object auditor 
    from Auditor object
    """

    def __init__(self):
        self.mixer = aumix.AudiMixer()

    #-----------------------------------------

    def init(self):
        """ init all things through auditor object
        """

        """
        if self.mixer:
            self.mixer.init()
            # self._audio_driver.init_audio()
        """
    
    #--------------------------------------
     
    def __del__(self):
        self.close()

    #-----------------------------------------

    def close(self):
        """ close the mixer through the auditor object
        """
        if self.mixer:
            self.mixer.close()

    #-----------------------------------------
       
#========================================

aud = Auditor()
mixer = aud.mixer
mixer.init()
aud.init()

fname1 = path.join(_mediadir, "drumloop.wav")
fname2 = path.join(_mediadir, "funky.wav")
fname3 = path.join(_mediadir, "latin.wav")
fname4 = path.join(_mediadir, "wave.wav")
fname5 = path.join(_mediadir, "singing.wav")

snd1 = mixer.create_sample(fname1)
snd2 = mixer.create_sample(fname2)
snd3 = mixer.create_sample(fname3)
snd4 = mixer.create_stream(fname4)
snd5 = mixer.create_stream(fname2)
snd6 = mixer.create_stream(fname5)

# snd4 = snd3
chan1 = mixer.create_channel(1)
# chan1.setvolume(16)
# chan1.setpanning(127, 0)
chan2 = mixer.create_channel(2)
chan3 = mixer.create_channel(3)
chan4 = mixer.create_channel(4)
chan5 = mixer.create_channel(5)
chan6 = mixer.create_channel(6)

class MainApp(object):
    def __init__(self):
        self.win = None

    #-------------------------------------------

    def Display(self, msg):
        self.win.move(2, 0)
        self.win.clrtoeol()
        self.win.refresh()
        self.win.addstr(2, 0, msg)

    #-------------------------------------------

    def Test(self):
        snd = snd5
        # len1 = len(snd._wavbuf_lst)
        len1 = snd._length
        curpos = snd.get_position()
        endpos = snd.get_end_position()
        # debug("voici filename: %s, et curpos: %d, endpos: %d, length: %d" %(snd._filename, curpos, endpos, len1))

        """
        input_lst, output_lst = mixer.audio_driver.get_device_names()
        debug("voici input names: %s et output names: %s" %(input_lst, output_lst))
         if mixer.audio_driver.set_output_device_index(rate=48000, device=5, channels=2, format=8):
            debug("Output device is ok")
        else:
            debug("Unable to set the output settings")
        """
        
        """
        debug("voici driver names : %s" % mixer.audio_driver.get_driver_names())
        debug("voici default driver  : %s" % mixer.audio_driver.get_driver_info_by_index(0))
        debug("voici devices list: %s" % mixer.audio_driver.get_device_list())
        debug("voici device info by driver device index: %s" % mixer.audio_driver.get_device_info_by_driver_device_index(0, 0))
        # debug("voici portaudio version : %d" % mixer.audio_driver.get_version())
        # debug("voici portaudio version texte : %s" % mixer.audio_driver.get_version_text())
        input_lst, output_lst = mixer.audio_driver.get_device_by_driver(0)
        debug("voici inputs by driver index: %s" % input_lst)
        debug("voici outputs by driver index: %s" % output_lst)
        """

        # test beep
        # mixer.beep(880, 0.5)
        
        """
        # test crop sample
        snd6 = mixer.create_sample(fname4)
        curses.beep()
        rate = 44100
        curses.beep()
        snd6 = snd6.crop_sample(2*rate, 17*rate)
        # snd6 = snd6.cut_sample(0, 3*rate)
        chan1.play(snd6)
        """

        """
        version = pyaudio.get_portaudio_version_text()
        debug("voici la version : %s" % version)
        """

        """
        cur_player = audi_ex.cur_player
        # problem with bpm=199, type_click=1
        cur_player.change_bpm(300)
        cur_player.change_type_click(1)
        # print "voici name : ",cur_player.get_cur().name
        # trp = CAudiTransportBase()
        # print "voici transport : ", trp.is_stoped()
        # print "voici snd1 : ",snd1.get_sound_dur()
        # print "snd1: %s, snd2: %s" %(snd1, snd2)
        # print snd1 == snd4 # cmp(snd1, snd2)
        """

        """
        global snd4
        # snd4 = aud.mix_sample(snd2, snd3, 0, snd3.get_length())
        # snd4 = aud.mix_sample(snd2, snd3, 0, snd3.get_length(), 44100)
        # snd4 = aud.concatesample(snd2, snd3)
        # snd4 = aud.cut_sample(snd2, 88200, 0)
        # snd4 = aud.erase_sample(snd2, 88200, -1)
        # snd4 = aud.tone(0, 440, 44100)

        # snd4 = snd2.mix_sample(snd3, 0, snd3.get_length(), 44100)
        # snd4 = snd2.concat_sample(snd3)
        # snd4 = snd2.cut_sample(88200, 0)
        # snd4 = snd2.erase_sample(88200, -1)
        snd4 = ausnd.AudiSample(mode=1) # empty sample
        snd4 = snd4.tone(0, 440, 44100)

        chan2.play(snd4, 0)
        # snd3 = None
        """
        
        """
        snd = aud.emptysample(bits=16, rate=44100, channels=2, nbsamples=44100)
        snd.set_position(22050)
        curpos = snd.get_position()
        nbsamp = snd.getnbframes()
        lensamp = snd.get_length()
        # print "voici position: %d samples, total samples: %d, length: %d" %(curpos, nbsamp, lensamp)
        """

        """
        snd3.set_position(22050)
        curpos = snd3.get_position()
        nbsamp = snd3.getnbframes()
        lensamp = snd3.get_length()
        print "voici position: %d samples, total samples: %d, length: %d" %(curpos, nbsamp, lensamp)
        """
        
        curses.beep()
        pass

    #-------------------------------------------

    def Main(self, stdscr):
        # stdscr is passing by curses.wrapper function
        self.win = stdscr
        msg = "Press a key..."
        self.Display(msg)
        while 1:
            key = self.win.getch() # pauses until a key's hit
            if key < 128:
                key = chr(key)
            if key == 'Q':
                aud.close()
                #aud1.close()
                break
            elif key == 'f':
                # chan1.setmute(1, 0)
                chan1.play(snd1)
            elif key == 'g':
                snd2.set_loop_count(2)
                snd2.set_loop_mode(1)
                # snd2.set_loop_points(0, 1, unit=1) # in seconds
                chan2.play(snd2, loops=-1)
            elif key == 'h':
                snd3.reverse()
                snd3.set_loop_mode(1)
                chan3.play(snd3, loops=-1)
            elif key == 'j':
                # test different sound on same channel
                chan2.play(snd4, 0)
            elif key == 'k':
                # stream test
                # snd4.set_loop_mode(1)
                snd4.set_loop_points(5, 10, 1)
                chan4.play(snd4, -1)
            elif key == 'l':
                snd5.set_loop_mode(1)
                loops =-1 # infinitely
                chan5.play(snd5, loops)
                pass
            elif key == 'm':
                chan6.play(snd6)
            elif key == 'x':
                # aud.mixer.play()
                pass
            elif key == 'c':
                aud.mixer.pause()
            elif key == 'v':
                # stop all channels
                aud.mixer.stop()
            elif key == 'b':
                chan1.forward(1)
            elif key == 'z':
                chan1.rewind(1)
            elif key == 'G':
                curpos = chan1.get_position(1)
                dur = chan1.get_length(1)
            elif key == 't': # test
                self.Test()
            elif key == 'u':
                print("Status: channels: %d, samplewidth: %d, rate: %d" %(aud.getfileinfo()))
            elif key == '<':
                chan1.setstart()
            elif key == '>':
                chan1.setend()
            else:
                curses.beep()

    #-------------------------------------------

#========================================

app = MainApp()
curses.wrapper(app.Main)

#-------------------------------------------

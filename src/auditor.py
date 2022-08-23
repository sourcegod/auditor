#! /usr/bin/python3
"""
    File: auditor.py:
    See changelog
    Date: Sun, 17/07/2022
    Author: Coolbrother

"""

import os, sys
import time
import audiport as aup
import interfaceapp as intapp
import curses
curses.initscr()

#------------------------------------------------------------------------------


class MainApp(object):
    def __init__(self, audio_driver=None, output_index=None):
        self.win = None
        self.iap = None
        self.mixer = None

    #-------------------------------------------

    def display(self, msg):
        self.win.move(2, 0)
        self.win.clrtoeol()
        self.win.refresh()
        # waiting for changes for the speech synthesis
        time.sleep(0.1)
        self.win.addstr(2, 0, msg)

    #-------------------------------------------

    def beep(self):
        curses.beep()

    #-------------------------------------------

    def Test(self):
        """
        testing the app
        from MainApp object
        """

        pass

    #-------------------------------------------
    
    def play_key(self, key):
        """
        play sound from key
        from MainApp object
        """
        key0 =16
        
        if key == 'f':
            (chan, snd) = self.mixer.get_chan_sound(key0, key0)
            # if snd: self.player.play_channel(key0, key0)

    #-------------------------------------------

    def main(self, stdscr, audio_driver=None, output_index=None):
        # stdscr is passing by curses.wrapper function
        self.win = stdscr
        self.iap = intapp.InterfaceApp(self)
        self.iap.init_app(audio_driver, output_index)
        self.mixer = self.iap.mixer
        len_chan_lst = len(self.mixer.get_channels())
        self.player = self.iap.player
        key0 =0
        msg = "Press a key..."
        self.display(msg)
        while 1:
            key = self.win.getch() # pauses until a key's hit
            if key >=48 and key <=57:
                num = key -48
                num += key0
                if num < len_chan_lst:
                    self.iap.play_mode(num)
                else:
                    self.beep()
                continue
                
            elif key < 128:
                key = chr(key)
            if key == 'Q':
                self.iap.close()
                break
            elif key == '.':
                self.player.stop_all()
            elif key == 'f':
                self.iap.change_pitch(step=0.25, adding=1)
            elif key == 'F':
                self.iap.change_pitch(step=-0.25, adding=1)

            elif key in ('g', 'h',
                    'i', 'j', 'k', 
                    'l', 'm', 
                    ):
                self.play_key(key)    
                # (chan, snd) = self.mixer.get_chan_sound(key0, key0)
                # if snd: self.player.play_channel(key0, key0)
            elif key == 'g':
                key0 +=1
                (chan, snd) = self.mixer.get_chan_sound(key0, key0)
                if snd: 
                    snd.set_loop_mode(1)
                    self.player.play_channel(1, 1, loops=-1)
            elif key == 'h':
                key0 +=3
                (chan, snd) = self.mixer.get_chan_sound(key0, key0)
                if snd: 
                    snd.reverse()
                    snd.set_loop_mode(1)
                    if chan: chan.play(snd, loops=-1)
            elif key == 'j':
                # test different sound on same channel
                (chan, snd) = self.mixer.get_chan_sound(key0+2, key0+4)
                if chan: chan.play(snd, 0)
            elif key == 'k':
                # stream test
                # snd4.set_loop_mode(1)
                (chan, snd) = self.mixer.get_chan_sound(key0+4, key0+4)
                if snd: 
                    snd.set_loop_points(5, 10, 1)
                    if chan: chan.play(snd, -1)
            elif key == 'l':
                (chan, snd) = self.mixer.get_chan_sound(key0+5, key0+5)
                if snd: 
                    snd.set_loop_mode(1)
                loops =-1 # infinitely
                if chan: chan.play(snd, loops)
            elif key == 'm':
                (chan, snd) = self.mixer.get_chan_sound(key0+6, key0+6)
                if chan: chan.play(snd)
            elif key == 'x':
                # aud.mixer.play()
                pass
            elif key == 'c':
                self.mixer.pause()
            elif key == 'v':
                # stop all channels
                self.player.stop_all()
            elif key == 'V':
                # stop the audio engine
                self.iap.stop_audio_engine()
            elif key == 'b':
                self.mixer.forward(1)
            elif key == 'z':
                self.mixer.rewind(1)
            elif key == 'G':
                (chan, snd) = self.mixer.get_chan_sound(0, 0)
                curpos = chan.get_position(1)
                dur = chan.get_length(1)
            elif key == 'S': 
                # stop midi thread
                self.iap.stop_midi_thread()
            elif key == 'T': # test
                # self.Test()
                self.iap.test()
            elif key == 'u':
                # print("Status: channels: %d, samplewidth: %d, rate: %d" %(aud.getfileinfo()))
                pass
            elif key == '<':
                (chan, snd) = self.mixer.get_chan_sound(0, 0)
                chan.setstart()
            elif key == '>':
                (chan, snd) = self.mixer.get_chan_sound(0, 0)
                chan.setend()
            elif key == '/':
                self.iap.select_mode(step=-1, adding=1)
            elif key == '*':
                self.iap.select_mode(step=1, adding=1)
            elif key == '-':
                self.iap.select_key0(step=-1, adding=1)
                key0 = self.iap.get_key0()
            elif key == '+':
                self.iap.select_key0(step=1, adding=1)
                key0 = self.iap.get_key0()
            else:
                curses.beep()
                pass

    #-------------------------------------------

#========================================

if __name__ == "__main__":
    audio_driver = aup.PortAudioDriver()
    output_index =6 # 6 # None for default output port
    app = MainApp()
    # app.init_app(audio_driver=audio_driver, output_index=output_index)
    curses.wrapper(app.main, audio_driver=audio_driver, output_index=output_index)

#-------------------------------------------

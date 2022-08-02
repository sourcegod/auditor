#! /usr/bin/python3
"""
    File: auditor.py:
    See changelog
    Date: Sun, 17/07/2022
    Author: Coolbrother

"""

import os, sys
import audiport as aup
import interfaceapp as intapp
import curses
curses.initscr()

#------------------------------------------------------------------------------


class MainApp(object):
    def __init__(self, audio_driver=None, output_index=None):
        self.win = None
        self.iap = intapp.InterfaceApp(audio_driver, output_index)
        # self.iap.init_app(audio_driver, output_index)
        self.mixer = self.iap.mixer


    #-------------------------------------------

    def Display(self, msg):
        self.win.move(2, 0)
        self.win.clrtoeol()
        self.win.refresh()
        self.win.addstr(2, 0, msg)

    #-------------------------------------------

    def Test(self):
        """
        testing the app
        from MainApp object
        """

        pass

    #-------------------------------------------

    def main(self, stdscr):
        # stdscr is passing by curses.wrapper function
        self.win = stdscr
        self.iap.init_app()
        msg = "Press a key..."
        self.Display(msg)
        while 1:
            key = self.win.getch() # pauses until a key's hit
            if key < 128:
                key = chr(key)
            if key == 'Q':
                self.iap.close()
                break
            elif key == 'f':
                # chan1.setmute(1, 0)
                (chan, snd) = self.mixer.get_chan_sound(0, 0)
                if snd: self.mixer.play_channel(0, 0)
            elif key == 'g':
                (chan, snd) = self.mixer.get_chan_sound(1, 1)
                if snd: 
                    snd.set_loop_mode(1)
                    self.mixer.play_channel(1, 1, loops=-1)
            elif key == 'h':
                (chan, snd) = self.mixer.get_chan_sound(3, 3)
                if snd: 
                    snd.reverse()
                    snd.set_loop_mode(1)
                    if chan: chan.play(snd, loops=-1)
            elif key == 'j':
                # test different sound on same channel
                (chan, snd) = self.mixer.get_chan_sound(2, 4)
                if chan: chan.play(snd, 0)
            elif key == 'k':
                # stream test
                # snd4.set_loop_mode(1)
                (chan, snd) = self.mixer.get_chan_sound(4, 4)
                if snd: 
                    snd.set_loop_points(5, 10, 1)
                    if chan: chan.play(snd, -1)
            elif key == 'l':
                (chan, snd) = self.mixer.get_chan_sound(5, 5)
                if snd: 
                    snd.set_loop_mode(1)
                loops =-1 # infinitely
                if chan: chan.play(snd, loops)
            elif key == 'm':
                (chan, snd) = self.mixer.get_chan_sound(6, 6)
                if chan: chan.play(snd)
            elif key == 'x':
                # aud.mixer.play()
                pass
            elif key == 'c':
                self.mixer.pause()
            elif key == 'v':
                # stop all channels
                self.mixer.stop_all()
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
            else:
                curses.beep()

    #-------------------------------------------

#========================================

if __name__ == "__main__":
    audio_driver = aup.PortAudioDriver()
    output_index = 6 # None for default output port
    app = MainApp(audio_driver=audio_driver, output_index=output_index)
    curses.wrapper(app.main)

#-------------------------------------------

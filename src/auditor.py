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
                self.iap.chan1.play(self.iap.snd1)
            elif key == 'g':
                # self.iap.snd2.set_loop_count(2)
                self.iap.snd2.set_loop_mode(1)
                # snd2.set_loop_points(0, 1, unit=1) # in seconds
                self.iap.chan2.play(self.iap.snd2, loops=-1)
            elif key == 'h':
                self.iap.snd3.reverse()
                self.iap.snd3.set_loop_mode(1)
                self.iap.chan3.play(self.iap.snd3, loops=-1)
            elif key == 'j':
                # test different sound on same channel
                self.iap.chan2.play(self.iap.snd4, 0)
            elif key == 'k':
                # stream test
                # snd4.set_loop_mode(1)
                self.iap.snd4.set_loop_points(5, 10, 1)
                self.iap.chan4.play(self.iap.snd4, -1)
            elif key == 'l':
                self.iap.snd5.set_loop_mode(1)
                loops =-1 # infinitely
                self.iap.chan5.play(self.iap.snd5, loops)
                pass
            elif key == 'm':
                self.iap.chan6.play(self.iap.snd6)
            elif key == 'x':
                # aud.mixer.play()
                pass
            elif key == 'c':
                self.iap.mixer.pause()
            elif key == 'v':
                # stop all channels
                self.iap.mixer.stop()
            elif key == 'V':
                # stop the audio engine
                self.iap.stop_audio_engine()
            elif key == 'b':
                self.iap.chan1.forward(1)
            elif key == 'z':
                self.iap.chan1.rewind(1)
            elif key == 'G':
                curpos = self.iap.chan1.get_position(1)
                dur = self.iap.chan1.get_length(1)
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
                self.iap.chan1.setstart()
            elif key == '>':
                self.iap.chan1.setend()
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

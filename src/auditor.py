#! /usr/bin/python3
"""
    File: auditor.py:
    See changelog
    Date: Sun, 17/07/2022
    Author: Coolbrother

"""

import warnings
import os, sys
import time
from os import path
import curses
curses.initscr()
import audimixer as aumix
import audiport as aup
import midutils as mid
import threading
import multiprocessing


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

class InstruObj(object):
    """ Instrument parameters container """
    def __init__(self):
        self.id =0
        self.name = "" # instrument's name
        self.key =0
        self.m_type = "" # midi message type
        self.m_vel =0 # velocity
        self.snd = None
        self.chan = None
        # chan_mode 0: stopping when note off, 1: continue playing, 2: overlapping sound
        self.chan_mode =0 
        self.loop_mode = False
        self.loop_count =0

    #------------------------------------------------------------------------------

#========================================

class MyThread(threading.Thread):
    def __init__(self, ev_callback=None, sleep_time=0.1):
        """ call base class constructor """
        super().__init__()
        self._stop_event = threading.Event()
        self._ev_callback = ev_callback
        self._sleep_time = sleep_time

    #-------------------------------------------

    def run(self):
        """main control loop"""
        while not self._stop_event.isSet():
            #do work
            self._ev_callback(1, 4)
            # print("hi")
            self._stop_event.wait(self._sleep_time)

    #-------------------------------------------

    def stop(self, timeout=None):
        """set stop event and join within a given time period"""
        self._stop_event.set()
        super().join(timeout)
        print("End of Threading...")

    #-------------------------------------------
           
#========================================

"""
    t = MyThread()
    t.start()
    time.sleep(5)
    t.join(1) #wait 1s max
"""

class MyProcess(multiprocessing.Process):
    def __init__(self, ev_callback=None, sleep_time=0.1):
        """ call base object constructor """
        super().__init__()
        self._exit = multiprocessing.Event()
        self._ev_callback = ev_callback
        self._sleep_time = sleep_time

    #-------------------------------------------

    def run(self):
        """main control loop"""
        while not self._exit.is_set():
        # if 1:
            self._ev_callback()
            time.sleep(0.1)
        print("Loop Exiting")

    #-------------------------------------------

    def stop(self, timeout=None):
        """set stop event and join within a given time period"""
        self._exit.set()
        super().join(timeout)
        print("End of Threading...")

    #-------------------------------------------
           
#========================================


class Auditor(object):
    """ 
    main object auditor 
    from Auditor object
    """

    def __init__(self, audio_driver=None):
        self.audio_driver = audio_driver
        self.mixer = aumix.AudiMixer(audio_driver)

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
        """ 
        close the mixer
        from Auditor object
        """
        
        if self.mixer:
            self.mixer.close()

    #-----------------------------------------
       
#========================================

class InterfaceApp(object):
    """ Interface app manager """
    def __init__(self, audio_driver=None, output_index=None):
        self.audio_driver = audio_driver # aup.PortAudioDriver()
        if self.audio_driver:
            self.audio_driver.set_output_device_index(output_index)
            self.audio_driver.parent = self
        self.aud = Auditor(audio_driver=self.audio_driver)
        self.mixer = self.aud.mixer
        self.mixer.init()
        self._thr = None
        self._midi_in = None
        self._midi_out = None
        self._instru_lst = []

        fname1 = path.join(_mediadir, "drumloop.wav")
        fname2 = path.join(_mediadir, "funky.wav")
        fname3 = path.join(_mediadir, "latin.wav")
        fname4 = path.join(_mediadir, "wave.wav")
        fname5 = path.join(_mediadir, "singing.wav")

        self.snd1 = self.mixer.create_sample(fname1)
        self.snd2 = self.mixer.create_sample(fname2)
        self.snd3 = self.mixer.create_sample(fname3)
        self.snd4 = self.mixer.create_stream(fname4)
        self.snd5 = self.mixer.create_stream(fname2)
        self.snd6 = self.mixer.create_stream(fname5)

        # snd4 = snd3
        self.chan1 = self.mixer.create_channel(1)
        # chan1.set_volume(16)
        # chan1.set_panning(127, 0)
        self.chan2 = self.mixer.create_channel(2)
        self.chan3 = self.mixer.create_channel(3)
        self.chan4 = self.mixer.create_channel(4)
        self.chan5 = self.mixer.create_channel(5)
        self.chan6 = self.mixer.create_channel(6)

    #-----------------------------------------
    
    def init_app(self, audio_driver=None, output_index=None):
        """
        init app
        from InterfaceApp object
        """

        self.gen_instruments()
        self.audio_driver.start_engine()
        self.start_midi_thread()

    #-----------------------------------------

    def close(self):
        """
        close the app
        from InterfaceApp object
        """

        self.stop_midi_thread()

    #-----------------------------------------
     
    def gen_instruments(self, count=16):
        """
        generate instruments list
        from InterfaceApp object
        """

        id =1
        self._instru_lst = []
        key0 = 36
        chan_lst = self.mixer.get_channels()
        snd_lst = self.mixer.get_sounds()

        for (i, item) in enumerate(chan_lst):
            instru = InstruObj()
            instru.id = i+1
            instru.key = key0 +i
            if i < len(snd_lst): instru.snd = snd_lst[i]
            instru.chan = chan_lst[i]
            
            self._instru_lst.append(instru)

        
        for instru in self._instru_lst:
            if instru.key in (37,):
                instru.chan_mode =1 # mode continue
            if instru.key == 38:
                # instru.snd.set_loop_count(2)
                instru.snd.set_loop_mode(1)
                instru.chan_mode =1
                instru.loop_mode =1
                instru.loop_count =-1

            if instru.key == 40: # no velocity
                instru.m_vel =-1
                instru.chan.set_vel(-1)

    #-----------------------------------------
    
    def play_notes(self, m_type, m_note, m_vel):
        """
        send note number to the mixer
        from InterfaceApp
        object
        """
        
        # print(f"note_num: {note_num}")
        if m_note >= 36: m_note -= 36
        loop_count =0
        if m_note >= len(self._instru_lst):
            print("\a")
            return
        
        instru = self._instru_lst[m_note]
        if m_type == "note_on":
            # print("\a")
            if instru.loop_mode: loop_count = instru.loop_count
            instru.m_type = m_type
            if instru.chan.is_vel():
                instru.m_vel = m_vel
                instru.chan.set_vel(m_vel)
            instru.chan.play(instru.snd, loop_count)
        elif m_type == "note_off":
            if instru.chan_mode == 0: instru.chan.stop()

    #-----------------------------------------

    def _midi_handler(self, msg, inport=0, outport=0, printing=False):
        """ 
        Handling midi messages 
        from InterfaceApp
        """
        
        # midi_in = mid.open_input(1)
        # midi_out = mid.open_output(outport)

        # msg = self._midi_in.poll()
        # better for performance to blocking port
        # msg = self._midi_in.receive(block=True)
        if msg:
            # print("\a") # beep
            m_type = msg.type
            if m_type in ['note_on', 'note_off']:
                m_note = msg.note
                m_vel = msg.velocity
                # Note off
                if m_type == "note_on" and m_vel == 0:
                    m_type = "note_off"
                    self.play_notes(m_type, m_note, m_vel)
                    if printing:
                        print("Midi_in Message: ")
                        print(f"Note_off, Midi Number: {m_note}, Name: {mid.mid2note(m_note)}")
                        print(f"Details: {msg}")
                # Note on
                elif m_type == "note_on" and m_vel >0:
                    self.play_notes(m_type, m_note, m_vel)
                    if printing:
                        print(f"Note_on, Midi Number: {m_note}, Name: {mid.mid2note(m_note)}")
                        freq = mid.mid2freq(m_note)
                        print(f"Freq: {freq:.2f}")
                        print(f"Details: {msg}")
            else:# others messages
                if printing:
                    print("Unknown message")
                    print(f"Details: {msg}")
            if  self._midi_out:
                self._midi_out.send(msg)
                if printing: 
                    print("Midi_out message.")
            # beep
            if printing: 
                print("\a")
        # time.sleep(0.1)
        # for testing performance
        self._count +=1
        # print(f"Callback Count: {self._count}")

    #-------------------------------------------

    def start_midi_thread(self):
        """
        Attach callback function to the Midi port Callback
        from InterfaceApp
        """

        self._count =0
        self._midi_in = mid.open_input(1)
        self._midi_in.callback = self._midi_handler
        self._midi_out = mid.open_output(0)
        self._midi_running = True

        """
        # Note: no need threading, just attach callback function to the input port
        if self._thr is None:
            self._thr = MyThread(self.play_midi)
            # self._thr = threading.Thread(target=self.play_midi,  args=(self._kill_ev, 1, 4))
            # self._thr = MyProcess(self.play_midi, )
            self._thr.start()
        """
        
    #-------------------------------------------

    def stop_midi_thread(self):
        """
        Stopping Midi callback
        from InterfaceApp
        """

        if self._midi_running:
            if self._midi_in:
                self._midi_in.callback = None
                self._midi_in.close()
            if self._midi_out:
                self._midi_out.close()
            self._midi_running = False

        """
        if self._thr:
            if self._midi_in:
                self._midi_in.close()
            if self._midi_out:
                self._midi_out.close()
            self._thr.stop()
        self._thr = None
        """
    
    #-------------------------------------------

    def start_audio_engine(self):
        """
        start the audio driver engine
        from InterfaceApp
        """
        
        if self.audio_driver:
            self.audio_driver.start_engine()

    #-------------------------------------------

    def stop_audio_engine(self):
        """
        stop the audio driver engine
        from InterfaceApp
        """
        
        if self.audio_driver:
            self.audio_driver.stop_engine()

    #-------------------------------------------

     
    def test(self):
        """
        Testing the app
        from InterfaceApp object
        """

        print("Test from InterfaceApp object")
        self.start_midi_thread()


    #-------------------------------------------

#========================================

class MainApp(object):
    def __init__(self, audio_driver=None, output_index=None):
        self.win = None
        self.iap = InterfaceApp(audio_driver, output_index)
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
                self.iap.aud.close()
                self.iap.close()
                #aud1.close()
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

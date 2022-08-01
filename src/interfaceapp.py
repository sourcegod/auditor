#! /usr/bin/python3
"""
    File: AudiMan.py:
    See changelog
    Date: Sun, 17/07/2022
    Author: Coolbrother

"""

import os, sys
from os import path
import audimixer as aumix
import midutils as mid
#------------------------------------------------------------------------------

### brouillon pour effacer
DEBUG =1 
curdir = path.dirname(__file__) # directory for the current script
_basedir = path.dirname(curdir) # base directory for the application
_mediadir = path.join(_basedir, "media")

def debug(msg="", title="", bell=True):
    if DEBUG:
        print("%s: %s" %(title, msg))
        if bell:
            print("\a")
    
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

class AudiMan(object):
    """ 
    Auditor manager
    from AudiMan object
    """
    def __init__(self, audio_driver=None):
        self.audio_driver = audio_driver
        self.mixer = aumix.AudiMixer(audio_driver)
        self.mixer.init()

    #-----------------------------------------

    def init(self):
        """ 
        init all things for auditor
        from AudiMan object
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
        from AudiMan object
        """
        
        if self.mixer:
            self.mixer.close()
            self.mixer = None

    #-----------------------------------------
       
#========================================

class InterfaceApp(object):
    """ Interface app manager """
    def __init__(self, audio_driver=None, output_index=None):
        self.audio_driver = audio_driver # aup.PortAudioDriver()
        if self.audio_driver:
            self.audio_driver.set_output_device_index(output_index)
            self.audio_driver.parent = self
            
        self.aud = AudiMan(audio_driver=self.audio_driver)
        self.mixer = self.aud.mixer
        self._thr = None
        self._midi_in = None
        self._midi_out = None
        self._instru_lst = []

    #-----------------------------------------
    
    def init_app(self, audio_driver=None, output_index=None):
        """
        init app
        from InterfaceApp object
        """

        if self.audio_driver:
            self.gen_channels()
            self.gen_instruments()
            if self.mixer:
                cacher = self.mixer.cacher
                cacher.preload()
            self.audio_driver.start_engine()
            self.start_midi_thread()

    #-----------------------------------------

    def close(self):
        """
        close the app
        from InterfaceApp object
        """

        if self.audio_driver:
            self.stop_midi_thread()
            if self.aud:
                self.aud.close()

    #-----------------------------------------
     
    def gen_channels(self):
        """
        Generate default channels and sounds
        from InterfaceApp object
        """

        fname1 = path.join(_mediadir, "drumloop.wav")
        fname2 = path.join(_mediadir, "funky.wav")
        fname3 = path.join(_mediadir, "latin.wav")
        fname4 = path.join(_mediadir, "wave.wav")
        fname5 = path.join(_mediadir, "singing.wav")
        fname6 = path.join(_mediadir, "a440.wav")
        fname7 = path.join(_mediadir, "guitar_1.wav")
        fname8 = path.join(_mediadir, "piano_1.wav")

        # in memory
        snd1 = self.mixer.create_sample(fname1)
        snd2 = self.mixer.create_sample(fname2)
        snd3 = self.mixer.create_sample(fname3)
        # same wave but in reverse mode
        snd4 = self.mixer.create_sample(fname3)
        
        # in streaming
        snd5 = self.mixer.create_stream(fname4)
        snd6 = self.mixer.create_stream(fname2)
        snd7 = self.mixer.create_stream(fname5)

        # inn memory
        # mono sample
        snd8 = self.mixer.create_sample(fname6)
        snd9 = self.mixer.create_sample(fname7)
        snd10 = self.mixer.create_sample(fname8)

        for i in range(10):
            self.mixer.create_channel(i)
            # chan1.set_volume(16)
            # chan1.set_panning(127, 0)

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

        # print("len chan_lst: ", len(chan_lst), len(snd_lst))
        for (i, item) in enumerate(chan_lst):
            instru = InstruObj()
            instru.id = i+1
            instru.key = key0 +i
            if i < len(snd_lst): instru.snd = snd_lst[i]
            instru.chan = chan_lst[i]
            
            self._instru_lst.append(instru)

        
        for instru in self._instru_lst:
            if instru.key == 37:
                instru.chan_mode =1 # mode continue
            if instru.key == 38:
                # instru.snd.set_loop_count(2)
                instru.snd.set_loop_mode(1)
                instru.chan_mode =1
                instru.loop_mode =1
                instru.loop_count =-1

            if instru.key == 39: # reverse sound
                instru.snd.reverse()


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
        
        # print(f"note_num: {m_note}")
        loop_count =0
        if m_note == 96:
            self.mixer.stop_all()
            return

        if m_note >= 36: m_note -= 36
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
            # instru.chan.play(instru.snd, loop_count)
            self.mixer.play_instru(instru)
        elif m_type == "note_off":
            if instru.chan_mode == 0: 
                # instru.chan.stop()
                self.mixer.stop_instru(instru)

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
if __name__ == "__main__":
    app = InterfaceApp()
    app.init_app()
    input("It's OK...")
    app.close()
    #-------------------------------------------

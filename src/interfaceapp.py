#! /usr/bin/python3
"""
    File: interfaceapp.py:
    See changelog
    Date: Sun, 17/07/2022
    Author: Coolbrother

"""

import os, sys
from os import path
import numpy as np
import audimixer as aumix
import audiplayer as aupl
import midutils as mid
import audiconf as conf
import utils as uti
import logging as log
log.basicConfig(level=log.DEBUG, filename="/tmp/app.log", filemode='w')

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

class InterfaceApp(object):
    """ Interface app manager """
    def __init__(self, parent=None):
        self._parent = parent
        self.audio_driver = None 
        self.player = None
        self.mixer = None
        self.cacher = None
        self._midi_in = None
        self._midi_out = None
        self._instru_lst = []
        self._mode_num =0
        self._mode_lst = [
                "With Mix With Cache",
                "With Mix No Cache",
                "No Mix With Cache",
                "No Mix No Cache By Channel",
                "No Mix No Cache By Sound",
                "With Cache Only",
                ]
        self._key_num =0
        self._key_lst = range(0, 61, 10)


    #-----------------------------------------
    
    def init_app(self, audio_driver=None, input_index=None, output_index=None):
        """
        init app
        from InterfaceApp object
        """

        self.audio_driver = audio_driver # aup.PortAudioDriver()
        if self.audio_driver:
            self.audio_driver.set_input_device_index(input_index)
            self.audio_driver.set_output_device_index(output_index)
            self.audio_driver.parent = self
        self.player = aupl.AudiPlayer(audio_driver=self.audio_driver)
        self.mixer = self.player.mixer
        if self.mixer:
            self.cacher = self.mixer.cacher
        if self.audio_driver:
            self.gen_instru_from_conf()
            self.gen_channels()
            self.gen_instruments()

            """
            if self.cacher:
                self.cacher.preload()
                self.cacher.set_caching(1)
            """

            self.player.init()
            self.audio_driver.start_engine()
            self.start_midi_thread(inport=1, outport=0, func=self._midi_handler)
            self.stop_log()

    #-----------------------------------------

    def close(self):
        """
        close the app
        from InterfaceApp object
        """

        if self.audio_driver:
            self.stop_midi_thread()
            if self.player:
                self.player.close()

    #-----------------------------------------
     
    def get_mode_num(self):
        """
        returns mode number
        from InterfaceApp object
        """

        return self._mode_num
    
    #-----------------------------------------

    def change_mode(self, mode_num, step=0, adding=0):
        """
        Deprecated function
        changing mode list
        """

        changing =0
        val =0
        max_val = len(self._mode_lst) -1
        # mode_num = self._mode_num
        if adding == 0: # no inc or dec value
            if step == -1:
                step = max_val
        else: # adding value
            val = mode_num + step
            changing =1
        if changing:
            step = uti.limit_value(val, 0, max_val)
        if mode_num != step:
            mode_num = step
        else: # no change for mode num
            uti.beep()
        
        item = self._mode_lst[mode_num]
        return (mode_num, item)
    
    #-------------------------------------------

    def select_mode(self, step=0, adding=0):
        """
        select mode item
        from InterfaceApp object
        """
        
        if self.cacher is None or self.mixer is None: 
            return 
        # (mode_num, mode_item) = self.change_mode(self._mode_num, step, adding)
        (mode_num, mode_item) = uti.change_item(self._mode_num, self._mode_lst, step, adding)
        if self._mode_num != mode_num:
            self._mode_num = mode_num
            self.mixer.set_mix_mode(mode_num)
          
        msg = f"Mode {mode_num}: {mode_item}"
        if self._parent:
            self._parent.display(msg)

    #-------------------------------------------

    def play_mode(self, num):
        """
        play belong mode number by channel or sound number
        from InterfaceApp object
        """

        # self._parent.display(f"play channel, sound: {num,num}")
        if not self.player: return
        mode_num = self._mode_num
        if mode_num in (0, 1, 2, 3):
            self.player.play_channel(num, num)
        elif mode_num == 4: # play sound only
            self.player.play_sound(num)
        elif mode_num == 5: # play cache only
            self.player.play_cache(num)

    #-------------------------------------------

    def get_key0(self):
        """
        returns the key0 item
        from InterfaceApp object
        """

        try:
            return self._key_lst[self._key_num]
        except IndexError:
            return 0

    #-------------------------------------------

    def select_key0(self, step=0, adding=0):
        """
        select keyboard key range
        from InterfaceApp object
        """
        
        (key_num, key_item) = uti.change_item(self._key_num, self._key_lst, step, adding)
        if self._key_num != key_num:
            self._key_num = key_num
        else:
            key_item = self._key_lst[self._key_num]
          
        msg = f"Key0 range: {key_item} to {key_item+9}"
        if self._parent:
            self._parent.display(msg)

    #-------------------------------------------

    def change_speed(self, step=0, adding=0):
        """
        change speed item
        from InterfaceApp object
        """
        
        if self.mixer is None: return
        chan = self.mixer.get_last_chan()
        if chan:
            speed_num = chan.get_speed()
            speed_num += step
            chan.set_speed(speed_num)
        
       
        if chan:
            speed_num = chan.get_speed()
            msg = f"speed {speed_num:0.2f}, on channel {chan.id}"
        else:
            msg = f"No speed on No channel"

        if self._parent:
            self._parent.display(msg)

    #-------------------------------------------

    def change_pan(self, step=0, adding=0):
        """
        change panning item
        from InterfaceApp object
        """
        
        if self.mixer is None: return
        chan = self.mixer.get_last_chan()
        if chan:
            pan_num = chan.get_pan()
            pan_num += step
            chan.set_pan(pan_num)
        
       
        if chan:
            pan_num = chan.get_pan()
            msg = f"Pan {pan_num:0.2f}, on channel {chan.id}"
        else:
            msg = f"No panning on No channel"

        if self._parent:
            self._parent.display(msg)

    #-------------------------------------------

    def change_delay(self, step=0, adding=0):
        """
        change simple delay item
        from InterfaceApp object
        """
        
        if self.mixer is None: return
        chan = self.mixer.get_last_chan()
        if chan:
            # TODO putting delay effect in DSP object
            delay = self.mixer.simple_delay
            time_num = delay.get_time()
            time_num += step
            delay.set_time(time_num)
            time_num = delay.get_time()
            msg = f"Delay time {time_num:0.2f}, on channel {chan.id}"
        else:
            msg = f"No Delay on No channel"

        if self._parent:
            self._parent.display(msg)

    #-------------------------------------------




    def gen_channels(self):
        """
        Generate default channels and sounds
        Note: these channels come after Intruments Configuration.
        from InterfaceApp object
        """

        # print("len channels: ", len(self.mixer._chan_lst))
        fname1 = path.join(_mediadir, "drumloop.wav")
        fname2 = path.join(_mediadir, "funky.wav")
        fname3 = path.join(_mediadir, "latin.wav")
        fname4 = path.join(_mediadir, "wave.wav")
        fname5 = path.join(_mediadir, "singing.wav")
        fname6 = path.join(_mediadir, "a440.wav")
        fname7 = path.join(_mediadir, "guitar_1.wav")
        fname8 = path.join(_mediadir, "piano_1.wav")

        # in memory
        # snd0 = self.mixer.beep(freq=880)
        snd1 = self.mixer.create_sample(fname1)
        snd2 = self.mixer.create_sample(fname2)
        snd3 = self.mixer.create_sample(fname3)
        # same wave but in reverse mode
        snd4 = self.mixer.create_sample(fname3)
        
        # in streaming
        snd5 = self.mixer.create_stream(fname4)
        snd6 = self.mixer.create_stream(fname2)
        # snd6 = self.mixer.create_sample(fname2)
        snd7 = self.mixer.create_stream(fname5)

        # inn memory
        # mono sample
        snd8 = self.mixer.create_sample(fname6)
        snd9 = self.mixer.create_sample(fname7)
        snd10 = self.mixer.create_sample(fname8)
        # in stream
        # mono stream
        snd11 = self.mixer.create_stream(fname6)
        # for the click temporary
        # click = self.mixer.create_tone(freq=220, lensec=5)
        
        for i in range(12):
            self.mixer.create_channel()
            # chan1.set_volume(16)
            # chan1.set_panning(127, 0)
            pass


    #-----------------------------------------
    
    def gen_instru_from_conf(self):
        """
        generate instruments from configuration file
        from InterfaceApp object
        """

        self._instru_lst = []
        key0 = 36
        # conf_dir = path.join(_mediadir, "TR808909")
        conf_dir = path.join(_mediadir, "TR808Classic")
        # conf_dir = path.join(_mediadir, "TR808Kit")
        conf_name = path.join(conf_dir, "drumkit.xml")
        auconf = conf.AudiConf()
        auconf.load(conf_name)
        ins_lst = auconf.get_instruments()
        try:
            for (i, item) in enumerate(ins_lst):
                # if i == 3: continue
                instru = InstruObj()
                filename = item["filename"]
                fname = path.join(conf_dir, filename)
                # in memory
                snd = self.mixer.create_sample(fname)
                chan = self.mixer.create_channel()
                instru.id = item["id"]
                instru.key = key0 +i
                instru.snd = snd
                instru.chan = chan
                
                self._instru_lst.append(instru)
        except KeyError as err:
            print("Error: when constructing instrument from conf.", err)



    #-----------------------------------------

    def gen_instruments(self, count=16):
        """
        generate instruments list
        from InterfaceApp object
        """

        last_index = len(self._instru_lst) +1 # +1 for click on channel 0
        id = last_index
        # self._instru_lst = []
        key0 = 36 + last_index
        try:
            chan_lst = self.mixer.get_channels()[last_index:]
            snd_lst = self.mixer.get_sounds()[last_index:]
        except IndexError:
            chan_lst = []
            snd_lst = []

        # print("len chan_lst: ", len(chan_lst), len(snd_lst))
        for (i, item) in enumerate(chan_lst):
            instru = InstruObj()
            instru.id = id + i
            instru.key = key0 +i
            if i < len(snd_lst): instru.snd = snd_lst[i]
            instru.chan = chan_lst[i]
            
            self._instru_lst.append(instru)

        
        # """
        for instru in self._instru_lst:
            if instru.key == key0 +1:
                instru.chan_mode =1 # mode continue
            if instru.key == key0 +2:
                # instru.snd.set_loop_count(2)
                # instru.snd.set_loop_mode(1)
                instru.chan_mode =1
                instru.chan.set_looping(True)
                instru.chan.set_volume(0.3)
                # instru.chan.set_speed(0.5)
                instru.loop_mode =1
                instru.loop_count =-1

            if instru.key == key0 +3: # reverse sound
                instru.snd.reverse()


            if instru.key == key0 +4: # no velocity
                instru.m_vel =-1
                instru.chan.set_vel(-1)
            if instru.key == key0 +5:
                # instru.snd.set_loop_mode(1)
                instru.chan.set_looping(True)
                instru.chan_mode =0
                instru.loop_mode =1
                instru.loop_count =-1
            if instru.key == key0 +7:
                instru.chan.set_looping(True)
                instru.loop_mode =1

         # """

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
            self.player.stop_all()
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
            self.player.play_instru(instru)
        elif m_type == "note_off":
            if instru.chan_mode == 0: 
                # instru.chan.stop()
                self.player.stop_instru(instru)

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

    #-------------------------------------------

    def start_midi_thread(self, inport=0, outport=0, func=None):
        """
        Attach callback function to the Midi port Callback
        from InterfaceApp
        """
        (self._midi_in, self._midi_out) = mid.start_midi_thread(inport, outport, func)

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
        
        (self._midi_in, self._midi_out) = mid.stop_midi_thread()

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
     
    def start_log(self):
        """
        Starting logging
        from InterfaceApp object
        """
        
        log.getLogger().setLevel(log.NOTSET)

        if self._parent:
            msg = "Start logging at level NOTSET"
            self._parent.display(msg)


    #-------------------------------------------

    def stop_log(self):
        """
        Stop logging
        from InterfaceApp object
        """
        
        log.getLogger().setLevel(log.CRITICAL+1)

        if self._parent:
            msg = "Stop logging."
            self._parent.display(msg)


    #-------------------------------------------


    def test(self):
        """
        Testing the app
        from InterfaceApp object
        """

        print("Test from InterfaceApp object")
        chan = self.mixer.get_last_chan()
        if chan:
            chan.set_pan(1) # 100% right channel
        else:
            msg = "No last channel"
            self._parent.display(msg)
        
        # test the cache
        # self.mixer.play_cache(1)
        # self.start_midi_thread()

    #-------------------------------------------

#========================================
if __name__ == "__main__":
    app = InterfaceApp()
    app.init_app()
    input("It's OK...")
    app.close()
    #-------------------------------------------

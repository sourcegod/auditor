#! /usr/bin/python3
"""
    File: portdriver.py:
    Module for PortAudio driver
    Date: Sat, 16/07/2022
    Author: Coolbrother
"""

import time
import wave
import threading
import pyaudio # for portaudio driver
import numpy as np 

#------------------------------------------------------------------------------

### brouillon pour effacer
DEBUG =1 
# float equality
_epsilon = 0.000001

def debug(msg="", title="", bell=True):
    if DEBUG:
        print("%s: %s" %(title, msg))
        if bell:
            print("\a")
    
#------------------------------------------------------------------------------

class PortAudioDriver(object):
    """ portaudio driver manager """
    def __init__(self):
        self._playing =0
        self._audio_data = None
        self._buf_size =512
        self._out = None
        self._nchannels =0
        self._sampwidth =0
        self._rate =0
        self._nframes =0
        self._chan_lst = [] # list for channel object
        self._audio_thread = None # object threading
        self._stream = None
        self._driver_index = None # equiv to host api
        self._input_device_index = None
        self._output_device_index = None
        self._buf_lst = []
        self._max_buf = 32
        self._mixing =0
        self.in_type = np.int16
        self.out_type = np.int16


    #------------------------------------------------------------------------------

   
    def init_audio(self, nchannels=2, rate=44100, format=8):
        """ Open the portaudio device in playback mode through the portaudio driver object 
        """
        
        self._out = pyaudio.PyAudio()

        fname1 = "/home/com/audiotest/loops/f1.wav"
        self.wf = wave.open(fname1, 'rb')

        # self._out.get_format_from_width(self.wf.getsampwidth())
        format = pyaudio.paInt16 
        # self.format = format
        
        # self._audio_thread = CAudioThread(self._write_audio_data)
       
        # with callback
        # """
        self._stream = self._out.open(format=format,
                    channels=nchannels,
                    rate=rate,
                    input=False,
                    output=True,
                    input_device_index = self._input_device_index,
                    output_device_index = self._output_device_index,
                    frames_per_buffer=self._buf_size,
                    start=False,
                    stream_callback=self._audio_callback)
        # """

        # with no callback
        """ 
        self._stream = self._out.open(format=format,
                    channels=nchannels,
                    rate=rate,
                    input=False,
                    output=True,
                    input_device_index = self._input_device_index,
                    output_device_index = self._output_device_index,
                    frames_per_buffer=self._buf_size,
                    start=False)
        """


    #-----------------------------------------

    def close(self):
        """ close audio driver from portaudio driver object        
        """
        
        if self._stream:
            self._stream.close()
            self._out.terminate()
            print("Closing audio driver")

    #-----------------------------------------
     
    def __del__(self):
        if self._audio_thread:
            self._audio_thread.Stop()

    #-----------------------------------------
   
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """ callback calling by portaudio
        """

        flag = pyaudio.paContinue
        # data = self.wf.readframes(frame_count)

        # data =  self._get_mix_data()
        data = self.read_buffers()
        
       
        # debug("je passe ici %d data_count" % len(data))
    
        return (data, flag)

    #-----------------------------------------
   
    def get_version(self):
       """ return  portaudio version
       """
       return pyaudio.get_portaudio_version()

    #-----------------------------------------

    def get_version_text(self):
       """ return  portaudio version string
       """
       return pyaudio.get_portaudio_version_text()

    #-----------------------------------------

    def get_driver_count(self):
        """ count driver host api available 
        """
        
        return self._out.get_host_api_count()

    #-----------------------------------------

    def get_default_driver_info(self):
        """ return the default driver host api available 
        """
        return self._out.get_default_host_api_info()    

    #-----------------------------------------
    
    def get_driver_info_by_index(self, index):
        return self._out.get_host_api_info_by_index(index)

    #-----------------------------------------
    
    def get_device_info_by_driver_device_index(self, driver_index, driver_device_index):
        return self._out.get_device_info_by_host_api_device_index(driver_index, driver_device_index)

    #-----------------------------------------

    def get_driver_list(self):
        """ return list of driver available
        """
        lst = []
        count =0
        count = self.get_driver_count()
        for i in range(count):
            lst.append(self.get_driver_info_by_index(i))
        
        return lst

    #-----------------------------------------

    def get_driver_names(self):
        """ return list of host api names
        """

        lst = []
        count =0
        count = self.get_driver_count()
        for i in range(count):
            dic = self.get_driver_info_by_index(i)
            try:
                    name = dic.get('name')
                    lst.append((i, name))
            except KeyError:
                pass

        return lst

    #-----------------------------------------
       
    def get_device_count(self):
        """ return device count from port audio driver object
        """

        return self._out.get_device_count()

    #-----------------------------------------
    
    def get_default_input_device_info(self):
        """ return dictionary containing info from portaudio driver object
        """

        return self._out.get_default_input_device_info()

    #-----------------------------------------

    def get_default_output_device_info(self):
        """ return dictionary containing info from portaudio driver object
        """

        return self._out.get_default_output_device_info()

    #-----------------------------------------
    
    def get_device_info_by_index(self, index):
        """ return dictionary containing info from portaudio driver object
        """

        return self._out.get_device_info_by_index(index)

    #-----------------------------------------
    
    def get_device_list(self):
        """ return list containing all devices info in a dictionary
        """
        lst = []
        count =0
        count = self.get_device_count()
        for i in range(count):
            lst.append(self.get_device_info_by_index(i))
        
        return lst
    #-----------------------------------------


    def get_device_names(self):
        """ return two lists with inputs and outputs devices name
        """

        input_lst = []
        output_lst = []
        count =0
        count = self.get_device_count()
        for i in range(count):
            dic = self.get_device_info_by_index(i)
            try:
                if dic.get('maxInputChannels') >0:
                    name = dic.get('name')                    
                    input_lst.append((i, name))
                if dic.get('maxOutputChannels') >0:
                    name = dic.get('name')                    
                    output_lst.append((i, name))
            except KeyError:
                pass

        return (input_lst, output_lst)

    #-----------------------------------------

    def get_device_by_driver(self, driver_index):
        """ return inputs and outputs list bellong driver host api index
        """

        input_lst = []
        output_lst = []
        count =0
        count = self.get_device_count()
        for i in range(count):
            dic = self.get_device_info_by_index(i)
            try:
                if dic.get('maxInputChannels') >0 and dic.get('hostApi') == driver_index:
                    name = dic.get('name')                    
                    input_lst.append(("index: %d, input_name: %s, driver_index: %d" %(i, name, driver_index)))
                if dic.get('maxOutputChannels') >0 and dic.get('hostApi') == driver_index:
                    name = dic.get('name')                    
                    output_lst.append(("index: %d, output_name: %s, driver_index: %d" %(i, name, driver_index)))
            except KeyError:
                pass

        return (input_lst, output_lst)

    #-----------------------------------------


    def get_input_device_index(self):
        return self._input_device_index

    #-----------------------------------------

    def set_input_device_index(self, rate, device, channels, format=None):
        """ test if this input device is available
        """

        res =0
        try:
            res = self._out.is_format_supported(rate, 
                    input_device=device, input_channels=channels, 
                    input_format=format)
        except ValueError as e:
            print(e)
        if res:
            self._input_device_index = device
        
        return res

    #-----------------------------------------

    def get_output_device_index(self):
        return self._output_device_index

    #-----------------------------------------


    def set_output_device_index(self, rate, device, channels, format=None):
        """ test if this input device is available
        """

        res =0
        try:
            res = self._out.is_format_supported(rate, 
                    output_device=device, output_channels=channels, 
                    output_format=format)
        except ValueError as e:
            print(e)
        if res:
            self._output_device_index = device
        
        return res

    #-----------------------------------------

    def add_channel(self, chan):
        """ temporary, adding chan to the chan list
        """

        self._chan_lst.append(chan)

    #-----------------------------------------

    def get_channel_list(self):
        """ temporary, get chan list
        """
        
        return self._chan_lst

    #-----------------------------------------

    def _get_mix_data(self): 
        """ mix audio data from Portaudio object
        """
        
        buf_lst = np.zeros((8, 1024), dtype='int32')
        out_buf = np.array([], dtype='int16')
        size =0
        # debug("je pass ici")
        chan_num =0
        chan_count =0

        for (i, chan) in enumerate(self._chan_lst):
            if chan.isactive():
                snd = chan.get_sound()
                curpos = snd.get_position(0) # in frames
                endpos = snd.get_end_position(0) # in frames
                if curpos >= endpos:
                    # debug("curpos >= endpos: %d, %d" %(curpos, endpos))
                    snd.loop_manager()
                    if not snd.is_looping():
                        chan.setactive(0)
                        continue
                   
                # whether buf_size =512 frames, so buf =512*4 = 2048 bytes
                # cause buf in byte, one frame = 4 bytes, 2 signed short, 
                # for 16 bits, 2 channels, 44100 rate,
                
                buf1 = snd.read_data(self._buf_size) 
                if not buf1.size:
                    debug("not buf1")
                    chan.setactive(0)
                    snd.set_play_count(0)
                    continue
                else:
                    """
                    len1 = self._buf_size * 2
                    size = len(buf1)
                    if size < len1:
                        nb_zeros = len1 - size
                        debug("Data too small, adding %d shorts filling with zeros" % nb_zeros)
                        # buf1 = chan.add_zeros(buf1, nb_zeros)
                        zero_lst = [0] * nb_zeros
                        buf1 += zero_lst
                    
                    # if chan.ismuted():
                    #    buf1 = chan.processmute(buf1)
                    #vol = chan.getvolume()
                    # buf1 = chan.processvolume(buf1)
                    # (leftpan, rightpan) = chan.getpanning()
                    # buf1 = chan.processpanning(buf1)
                    # buf1 = chan.seteffect(buf1)
                    """
                    # buf_lst.append(buf1)
                    len1 = buf1.size
                    buf_lst[i] = buf1
                    chan_num = i
                    chan_count +=1
                    # debug("voici i: %d et shape: %s" %(i, buf1.shape))
                    # return
        
        # out of the loop
        if buf_lst.size:
            if chan_count == 1:
                out_buf = buf_lst[chan_num].astype('int16')
                # debug("voici len array %d" % len(out_buf))
            elif chan_count >= 2:
                # passing the type of array result to avoid copy with astype letter
                x = np.sum(buf_lst, axis=0, dtype=self.out_type) # sum by column
                
                # use x.view to avoid copy array,
                # and using np.clip to limit values
                val_lim = 32767
                # limit value in place to avoid copy
                np.clip(x, -val_lim -1, val_lim, out=x)
                out_buf = x # no copy
                # debug("voici %d, %s" %(len(out_buf), out_buf.dtype))

            if out_buf.size:
                # debug("voici: %s" % out_buf)
                self._mixing =1
                return out_buf.tostring()
        
        else: # buf_lst is empty
            self._mixing =0
            # debug("Mixing finished...")
            
            return None

    #-----------------------------------------
        
    def _write_audio_data(self):
        """ write audio data from portaudio object
        """

        self._playing =1
        while self._audio_data and self._playing:
            # self._out.write(self._audio_data)
            self._stream.write(self._audio_data)
            self._audio_data = self._get_mix_data()
            if not self._playing:
                self._audio_thread.Stop()
                self._stream.stop_stream()
                break
            if not self.get_nb_chan_active():
                self._audio_thread.Stop()
                self._stream.stop_stream()
                self._playing =0
                break
            

    #-----------------------------------------

    def read_buffers(self):
        """ read buffer list from portaudio object
        """
        res = None
        if self._mixing:
            data = self._get_mix_data()
            self._buf_lst.append(data)

        if self._buf_lst:
            res = self._buf_lst.pop(0)
        
        return res
    #-----------------------------------------
 
    def set_cache(self):
        """ set caching buffer from portaudio object
        """
        self._buf_lst = []
        for i in range(self._max_buf):
            data = self._get_mix_data()
            if data:
                self._buf_lst.append(data)
            else:
                break
        
        # little pause
        time.sleep(0.1)
        
        return self._buf_lst

    #-----------------------------------------
    
    def get_cache(self): 
        """ return caching buffer from portaudio object
        """
        
        return self._buf_lst

    #-----------------------------------------


    def start_thread(self):
        """ start threading through portaudio driver object
        """

        # debug("voici format : %s" % self.format)
        if not self._stream.is_active() or not self._playing:
            self._stream.stop_stream()
            if self.set_cache():
                # debug("voici len buf_lst: %d" % len(self._buf_lst))
                self._stream.start_stream()
                self._playing =1
            # debug("je starte")

    #-----------------------------------------

    def stop_thread(self):
        """ start threading through portaudio driver object
        """

        if self._playing:
            self._stream.stop_stream()
            debug("je stoppe")
            self._playing =0
   
    #-----------------------------------------
   
   
    def start_thread0(self):
        # start callback calling by audiothread
        self._playing =1
        self._audio_data = self._get_mix_data()
        self._stream.start_stream()
        self._audio_thread.Start()

    #-----------------------------------------

    def stop_thread0(self):
        # stop callback calling by audiothread
        self._playing =0
        self._stream.stop_stream()
        self._audio_thread.Stop()

    #-----------------------------------------

    def get_nb_chan_active(self):
        # return number of active channels
        lst = [chan for chan in self._chan_lst if chan.isactive()]
        
        return len(lst)

    #-----------------------------------------
  
#========================================

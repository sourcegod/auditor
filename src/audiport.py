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

class BaseDriver(object):
    """ Base Audio Driver """
    def __init__(self):
        self._buf_size =512
        self._out = None
        self._nchannels =0
        self._sampwidth =0
        self._rate =0
        self._nframes =0
        self._chan_lst = [] # list for channel object
        self._stream = None
        self._driver_index = None # equiv to host api
        self._input_device_index = None
        self._output_device_index = None
        self._running = False


    #------------------------------------------------------------------------------

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


    def set_output_device_index(self, device):
        """ 
        test whether this input device is available
        from BaseDriver object 
        """

        rate=44100
        channels =2
        format = None
        res =0
        """
        try:
            res = self._out.is_format_supported(rate, 
                    output_device=device, output_channels=channels, 
                    output_format=format)
        except ValueError as e:
            print(e)
        if res:
            self._output_device_index = device
        """

        self._output_device_index = device
        
        return res

    #-----------------------------------------


#========================================

class PortAudioDriver(BaseDriver):
    """ portaudio driver manager """
    def __init__(self):
        super().__init__()
        self.parent = None
        self._audio_thread = None # object threading
        self._playing =0
        self._audio_data = None
        self._max_buf = 32 # for caching
        self._cache_lst = [] # for caching
        self._mixing =0
        self._mixer = None

    #------------------------------------------------------------------------------

   
    def init_audio(self, nchannels=2, rate=44100, format=8):
        """ Open the portaudio device in playback mode through the portaudio driver object 
        """
        
        self._out = pyaudio.PyAudio()


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
   
    def set_mixer(self, mixer):
        """
        set the mixer for mixing data
        from AudiPort object
        """
        
        self._mixer = mixer

    #-----------------------------------------

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """ callback calling by portaudio
        """

        data =None
        flag = pyaudio.paContinue

        # data = self.read_buffers()
        if self._cache_lst:
            data = self._cache_lst[0]
            # debug("Caching here...")
            self._cache_lst = []
        elif self._mixer:
            data =  self._mixer.get_mix_data()
        # debug(f"Data Len") 
        
        return (data, flag)

    #-----------------------------------------
   
    def _write_audio_data(self):
        """ write audio data from portaudio object
        """

        if not self._mixer: return
        self._playing =1
        while self._audio_data and self._playing:
            # self._out.write(self._audio_data)
            self._stream.write(self._audio_data)
            self._audio_data = self._mixer.get_mix_data()
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
        if not self._mixer: return
        if self._mixing:
            data = self._mixer.get_mix_data()
            self._cache_lst.append(data)

        if self._cache_lst:
            res = self._cache_lst.pop(0)
        
        return res
    #-----------------------------------------
 
    def set_cache(self):
        """
        set audio buffer cache
        from portaudio object
        """
        self._cache_lst = []
        data = None
        # for i in range(self._max_buf):
        if 1:
            data = self._mixer.get_mix_data()
            if data: self._cache_lst.append(data)
            # else: break
        
        # little pause
        time.sleep(0.1)
        
        return data

    #-----------------------------------------
    
    def get_cache(self): 
        """ return caching buffer from portaudio object
        """
        
        return self._cache_lst

    #-----------------------------------------


    def start_engine(self):
        """ 
        start the audiocallback through portaudio driver 
        from PortAudioDriver object
        """

        if not self._stream.is_active() or not self._running:
            self._stream.stop_stream()
            if self.set_cache():
                # debug("After Caching...")
                # debug("voici len buf_lst: %d" % len(self._cache_lst))
                self._stream.start_stream()
                self._running = True
                debug("Starting the Stream Callback")

    #-----------------------------------------

    def stop_engine(self):
        """ 
        stop  the audio callback through portaudio driver object
        from PortAudioDriver object
        """

        if self._running:
            self._stream.stop_stream()
            print("\a")
            debug("Stopping the stream callback...")
            self._running = True
   
    #-----------------------------------------
   
#========================================

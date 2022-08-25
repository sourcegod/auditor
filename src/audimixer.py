#! /usr/bin/python3
"""
    File: audimixer.py
    Module mixer for Auditor Engine
    Date: Sun, 17/07/2022
    Author: Coolbrother
"""

import sys, time
import numpy as np
# import audisample as ausam
import audisample2 as ausam
# import audistream as austr
import audistream2 as austr
import audichannel as auchan
# import audiport as aup
import audicache as auc
DEBUG =1 
def debug(msg="", title="", bell=True):
    if DEBUG:
        print("%s: %s" %(title, msg))
        if bell:
            print("\a")
    
#------------------------------------------------------------------------------

class AudiRoll(object):
    """ object for rolling item derived from list """
    def __init__(self, rolling=True):
        self._data = []
        self._cur =0
        self.id =0
        self.type = ""
        self.name = ""
        self.rolling = rolling

    #-----------------------------------------
    
    def get_list(self):
        """
        convenient function for getting the list object
        from CAudiList object
        """

        return self._data

    #-----------------------------------------

    def set_list(self, lst):
        self._data = lst

    #-----------------------------------------

    def add(self, *args):
        self._data.extend(args)

    #-----------------------------------------

    def get(self):
        try:
            return self._data[self._cur]
        except IndexError:
            return
        
    #-----------------------------------------

    def set(self, val):
        if val >= 0 and val < len(self):
            try:
                self._cur = val
                return self._data[self._cur]
            except IndexError:
                return
        
        return
    
#-----------------------------------------
    
    def item_index(self):
        return self._cur

    #-----------------------------------------

    def get_prev(self):
        # get prev item in the list
        cur = self._cur
        if cur == 0 and self.rolling:
            cur = len(self._data) -1
        elif cur > 0:
            cur -= 1
        try:
            return self._data[cur]
        except IndexError:
            return
        
        return

    #-----------------------------------------

    def prev(self):
        # set prev item in the list
        if self._cur ==0 and self.rolling:
            self._cur = len(self._data) -1
        elif self._cur > 0:
            self._cur -= 1
        try:
            return self._data[self._cur]
        except IndexError:
            return

    #-----------------------------------------

    def get_next(self):
        # get next item in the list
        cur = self._cur
        if cur == len(self._data) -1 and self.rolling:
            cur =0
        elif cur < len(self._data) -1:
            cur += 1
        try:
            return self._data[cur]
        except IndexError:
            return
        
    #-----------------------------------------

    def next(self):
        # set next item in the list
        if self._cur == len(self._data) -1 and self.rolling:
            self._cur =0
        elif self._cur < len(self._data) -1:
            self._cur += 1
        try:
            return self._data[self._cur]
        except IndexError:
            return

    #-----------------------------------------

    def get_first(self):
        """ 
        get first item in the list
        from CAudiList object
        """
        if self._data:
            return self._data[0]

        return 

    #-----------------------------------------

    def first(self):
        """ set first item in the list
        """
        if self._data:
            self._cur =0
            return self._data[self._cur]

        return

    #-----------------------------------------

    def get_last(self):
        """ get last item in the list
        """
        if self._data:
            cur = len(self._data) -1
            try:
                return self._data[cur]
            except IndexError:
                return
        
        return

    #-----------------------------------------

    def last(self):
        """ set last item in the list
        """
        if self._data:
            self._cur = len(self._data) -1
            try:
                return self._data[self._cur]
            except IndexError:
                return
        
        return

    #-----------------------------------------

    def is_first(self):
        """ is first item in the list
        """
        
        return self._cur == 0

    #-----------------------------------------

    def is_last(self):
        """ is last item in the list
        """

        return self._cur == len(self._data) -1

    #-----------------------------------------

    def max(self):
        if self._data:
            return max(self._data)

        return

    #-----------------------------------------

    def min(self):
        if self._data:
            return min(self._data)

        return

    #-----------------------------------------

#========================================

class AudiMixer(object):
    """ Singleton object
    Mixer object to manage channels 
    """
    __single_instance = None
    @staticmethod
    def get_instance():
        """ Static access method """
        if AudiMixer.__single_instance is None:
            AudiMixer()
        return AudiMixer.__single_instance

    def __init__(self, audio_driver=None):
        if AudiMixer.__single_instance != None:
            raise exception("This Klass is a singleton klass.")
        else:
            AudiMixer.__single_instance = self
        
        # self._audio_driver = AlsaAudioDriver()
        # self.audio_driver = aup.PortAudioDriver()
        self.audio_driver = audio_driver
        self._playing =0
        self._curpos =0
        self._sound_lst = [] # list for sound object
        self._chan_lst = [] # list for channel object
        self._chan = None
        self._sound = None
        self._snd_num =0
        self._active_chan_dic = {}
        self.last_chan = None
        self._thr_audio = None
        # must be the same as buf_size in PortAudio Driver
        self._buf_size =512
        self._nchannels =1 # TODO: why nchannels not been initialized by init function?
        self._rate = 44100
        self._format =0
        self._in_type = np.float64
        # self._out_type = np.int16
        self._out_type = np.float32
        self._mixing =0
        self._max_int16 = 32767
        self._len_buf =1
        # to maintaining the audio callback alive
        self._ret_buf = None
        self.cacher = None
        self._roll_lst = AudiRoll(rolling=True)
        self._roll_lst.set_list(range(8))
        # print("voici rool: ", self._roll_lst)
        self._vol_ratio =0.5
        self.cur_func = None
        self.simple_delay = auchan.SimpleDelay(time=0.5, decay=0.5, rate=44100)
        self.simple_delay._active =1

    #-----------------------------------------

    def __del__(self):
        self.close()

    #-----------------------------------------

    def init(self, nchannels=2, rate=44100, format=16):
        self._nchannels = nchannels
        self._rate = rate
        self._format = format
        # debug("in the mixer init: nchannels: ", self._nchannels)
        self._len_buf = self._buf_size * self._nchannels
        # self._ret_buf = np.zeros((self._len_buf,), dtype=self._out_type).tobytes()
        # convert to bytes in float32
        self._ret_buf = np.zeros((self._len_buf,), dtype=self._out_type).tobytes()

        if self.audio_driver:
            self.audio_driver.set_callback(self._audio_callback)
            self.audio_driver.init_audio(nchannels, rate, format)
            self.audio_driver.set_mixer(self)
        # create cache data
        self.cacher = auc.AudiCache(self)
        self._mixing =1
        # self.cur_func = self.get_mix_data
        self.cur_func = self.get_buf_data

        # sound musb be created with channel to sync both of them
        # create reserved channel for beep
        # self.chan_beep = self.create_channel(1000)
        self.chan_beep = None
    
    #-----------------------------------------

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """ 
        Audio callback calling by the audio driver
        from AudiMixer object
        """

        # init data
        len_buf = self._len_buf
        data = np.zeros((len_buf, ), dtype=self._out_type)
        # flag = pyaudio.paContinue
        flag_ok = self.audio_driver.flag_ok
        channels = self._active_chan_dic
        simple_delay = self.simple_delay
        simple_delay._active =0
        
        # print(f"frame_count: {frame_count}")
        for chan in list(channels.values()):
            if chan._active:
                chan.write_sound_data(data, len_buf)
        # effect delay
        if simple_delay._active:
            simple_delay.write_sound_data(data, len_buf)

        return (data.tobytes(), flag_ok)

    #-----------------------------------------
      
    def _get_mix_data0(self): 
        """ 
        Deprecated function, savint it for performance test
        mixing audio data 
        from AudiMixer object
        """
        
        # buf_lst = np.zeros((8, self._nchannels * self._buf_size), dtype=np.float32)
        # take less place in memory
        nb_virchan =16
        buf_lst = [None] * nb_virchan
        buf1 = np.array([], dtype=np.float32)
        out_buf = np.array([], dtype=self._out_type)
        # debug("je pass ici")
        chan_num =0
        chan_count =0
        # use of local variable to optimizing lookup attributes and functions
        chan_lst = self._chan_lst
        cacher = self.cacher
        len_cache = cacher.len_cache
        ca_get_data = cacher.get_data
        ca_get_pos = cacher.get_pos
        ca_set_pos = cacher.set_pos
        ca_is_caching = cacher.is_caching
        ca_nb_buf = cacher.nb_buf
        ca_nb_frames = cacher.nb_frames
        cached = False
        len_buf_lst = len(buf_lst)
        num = -1 # for index of buf_lst


        for (i, chan) in enumerate(chan_lst):
            if chan.is_active():
                snd = chan.get_sound()
                curpos = snd.get_position(0) # in frames
                endpos = snd.get_end_position(0) # in frames
                
                if ca_is_caching() and i < len_cache: 
                    cache_pos = ca_get_pos(i)
                    if curpos == 0:
                        # print("\a", file=sys.stderr)
                        ca_set_pos(i, 0)
                        buf1 = np.copy(ca_get_data(i))
                        snd.set_position(cacher.nb_frames)
                        cached = True
                        # print(f"its caching... curpos: {curpos}")
                    
                    elif cache_pos < ca_nb_buf:
                        buf1 = np.copy(ca_get_data(i))
                        # snd.set_position(curpos + self._buf_size)
                        cached = True
                        # print(f"its caching... buf_pos: {cacher.buf_pos}, curpos: {curpos}")
                
                if curpos >= endpos:
                    # debug("curpos >= endpos: %d, %d" %(curpos, endpos))
                    snd.loop_manager()
                    if not snd.is_looping():
                        chan.set_active(0)
                        continue
                   
                # whether buf_size =512 frames, so buf =512*4 = 2048 bytes
                # cause buf in byte, one frame = 4 bytes, 2 signed short, 
                # for 16 bits, 2 channels, 44100 rate,
                
                if not cached:
                    buf1 = snd.read_data(self._buf_size)
                if not buf1.size:
                    debug("not buf1")
                    chan.set_active(0)
                    snd.set_play_count(0)
                    continue
                else:
                    if len(buf1) < self._len_buf:
                        buf1.resize(self._len_buf)
                        chan.set_active(0)
                        # debug(f"Buffer resized: {len(buf1)}, with len_buf: {self._len_buf}")

                    
                    """
                        nb_zeros = len1 - size
                        debug("Data too small, adding %d shorts filling with zeros" % nb_zeros)
                        # buf1 = chan.add_zeros(buf1, nb_zeros)
                        zero_lst = [0] * nb_zeros
                        buf1 += zero_lst
                    
                    # if chan.is_muted():
                    #    buf1 = chan.process_mute(buf1)
                    #vol = chan.get_volume()
                    # buf1 = chan.process_volume(buf1)
                    # (leftpan, rightpan) = chan.getpanning()
                    # buf1 = chan.process_panning(buf1)
                    # buf1 = chan.set_effect(buf1)
                    """
                    
                    # avoid saturation
                    buf1 *= self._vol_ratio
                    if chan.is_vel():
                        chan.process_vel(buf1)
                    
                    # FIX: we cannot modify array that is in readonly, so we copy
                    # to avoid saturation when summing, we divide the amplitude
                    # buf1 = buf1 / 2
                    
                    # verify whether there is a free place
                    num = (num + 1) % len_buf_lst
                    buf_lst[num] = buf1
                    chan_num = num
                    if chan_count < len_buf_lst:
                        chan_count +=1
                        # debug("voici i: %d et shape: %s" %(i, buf1.shape))
        
        # out of the loop
        if chan_count == 0: # no more audio data
            # maintaining the audio callback alive
            return self._ret_buf
        elif chan_count == 1: # no copy data
            out_buf = buf_lst[chan_num] # (buf_lst[chan_num] * 32767).astype('int16')
            # no copy, but very bad sound
            # out_buf = buf_lst[chan_num].view(self._out_type)
            # debug("Yes mannn")
        elif chan_count >= 2:
            # passing the type of array result to avoid copy with astype letter
            # avoid saturation, but no copy
            # max_amp = np.max(np.abs(buf_lst))
            # print(f"voici max: {val_max}")
            # TODO: find better solution for readjust level after mixing
            line = np.sum(buf_lst[0:chan_count], axis=0, dtype=np.float32) # sum each column per line
            # line = sum(buf_lst) # sum each column per line
            # readjust the volume
            # TODO: normalize it
            # max_amp = np.max(line)
            # line += (1.0 - max_amp)
            # line += 0.2 # FIXIT
            # print(f"voici max_amp: {max_amp}, et max_line: {1.0 - max_amp}")
            
            """
            # No more necessary
            # use line.view to avoid copy array,
            # and using np.clip to limit values
            val_lim = 32767
            # limit value in place to avoid copy
            np.clip(line, -val_lim -1, val_lim, out=line)
            """
            
            out_buf = line # no copy
            # debug("voici %d, %s" %(len(out_buf), out_buf.dtype))

        if out_buf.size:
            # debug("voici: %s" % out_buf)
            
            # avoid copy
            return out_buf.tobytes()
            # return (out_buf * self._max_int16).astype(np.int16).tostring()
    
        else: # out_buf  is empty
            # debug("Mixing finished...")
            
            return self._ret_buf

    #-----------------------------------------

    def get_buf_data_0(self): 
        """ 
        Deprecated function, keeping for benchmark
        Only read audio data 
        from AudiMixer object
        """
        
        # take less place in memory
        nb_virchan =16
        buf_lst = [None] * nb_virchan
        buf1 = np.array([], dtype=np.float32)
        out_buf = np.array([], dtype=self._out_type)
        # debug("je pass ici")
        chan_num =0
        chan_count =0
        # use of local variable to optimizing lookup attributes and functions
        chan_lst = self._chan_lst
        cacher = self.cacher
        len_cache = cacher.len_cache
        ca_get_data = cacher.get_data
        ca_get_pos = cacher.get_pos
        ca_set_pos = cacher.set_pos
        ca_is_caching = cacher.is_caching
        ca_nb_buf = cacher.nb_buf
        ca_nb_frames = cacher.nb_frames
        cached = False
        len_buf_lst = len(buf_lst)
        num = -1 # for index of buf_lst
        mixing = self._mixing


        for (i, chan) in enumerate(chan_lst):
            print("\a")
            if chan.is_active():
                snd = chan.get_sound()
                if not snd: 
                    chan.set_active(0)
                    continue
                curpos = snd.get_position(0) # in frames
                endpos = snd.get_end_position(0) # in frames
                
                if ca_is_caching() and i < len_cache: 
                    cache_pos = ca_get_pos(i)
                    if curpos == 0:
                        # print("\a", file=sys.stderr)
                        ca_set_pos(i, 0)
                        buf1 = np.copy(ca_get_data(i))
                        snd.set_position(cacher.nb_frames)
                        cached = True
                        # print(f"its caching... curpos: {curpos}")
                    
                    elif cache_pos < ca_nb_buf:
                        buf1 = np.copy(ca_get_data(i))
                        # snd.set_position(curpos + self._buf_size)
                        cached = True
                        # print(f"its caching... buf_pos: {cacher.buf_pos}, curpos: {curpos}")
                
                # curpos+1 for flac format where last curpos is = endpos -1
                if curpos+1 >= endpos:
                    # debug("curpos >= endpos: %d, %d" %(curpos, endpos))
                    snd.loop_manager()
                    if not snd.is_looping():
                        chan.set_active(0)
                        continue
                   
                # whether buf_size =512 frames, so buf =512*4 = 2048 bytes
                # cause buf in byte, one frame = 4 bytes, 2 signed short, 
                # for 16 bits, 2 channels, 44100 rate,
                
                if not cached:
                    buf1 = snd.read_data(self._buf_size)
                if not buf1.size:
                    debug("not buf1")
                    chan.set_active(0)
                    snd.set_play_count(0)
                    continue
                else: # whether buf1 have size
                    if len(buf1) < self._len_buf:
                        buf1.resize(self._len_buf)
                        chan.set_active(0)

                    # avoid saturation
                    if mixing:
                        buf1 *= self._vol_ratio
                        if chan.is_vel():
                            chan.process_vel(buf1)
                       
                        # verify whether there is a free place
                        num = (num + 1) % len_buf_lst
                        buf_lst[num] = buf1
                        chan_num = num
                        if chan_count < len_buf_lst:
                            chan_count +=1
                            # debug("voici i: %d et shape: %s" %(i, buf1.shape))
            
        # out of the loop
        if buf1.size and not mixing:
            return buf1.tobytes()
        if chan_count == 0: # no more audio data
            # maintaining the audio callback alive
            return self._ret_buf
        elif chan_count == 1: # no copy data
            out_buf = buf_lst[chan_num] 
            return out_buf.tobytes()
        elif chan_count >= 2:
            out_buf = self._mix_buf_data(chan_count, buf_lst)

        if out_buf.size:
            # avoid copy
            
            """
            time.sleep(1)
            print("\a")
            """
            return out_buf.tobytes()
        else: # out_buf  is empty
            return self._ret_buf

    #-----------------------------------------

    def get_buf_data(self): 
        """ 
        2nd version for benchmark
        Only read audio data 
        from AudiMixer object
        """
        
        # take less place in memory
        nb_virchan =16
        buf_lst = [None] * nb_virchan
        buf1 = np.array([], dtype=np.float32)
        out_buf = np.array([], dtype=self._out_type)
        # debug("je pass ici")
        chan_num =0
        chan_count =0
        # use of local variable to optimizing lookup attributes and functions
        chan_lst = self._chan_lst
        active_chan_dic = self._active_chan_dic
        cacher = self.cacher
        len_cache = cacher.len_cache
        ca_get_data = cacher.get_data
        ca_get_pos = cacher.get_pos
        ca_set_pos = cacher.set_pos
        ca_is_caching = cacher.is_caching
        ca_nb_buf = cacher.nb_buf
        ca_nb_frames = cacher.nb_frames
        cached = False
        len_buf_lst = len(buf_lst)
        num = -1 # for index of buf_lst
        mixing = self._mixing


        # Whether not mixing, keeping the last active channel
        if not mixing and len(active_chan_dic) >= 2:
            active_chan_dic.clear()
            active_chan_dic[self.last_chan.id] = self.last_chan
        
        # efficient way to delete item in dictionnary while iterating
        for key in list(active_chan_dic.keys()):
        # for (i, chan) in enumerate(chan_lst):
            # print("\a")
            chan = active_chan_dic[key]
            i = chan.id
            if chan.is_active():
                snd = chan.get_sound()
                if not snd: 
                    chan.set_active(0)
                    del active_chan_dic[chan.id]
                    continue
                curpos = snd.get_position(0) # in frames
                endpos = snd.get_end_position(0) # in frames
                
                if ca_is_caching() and i < len_cache: 
                    cache_pos = ca_get_pos(i)
                    if curpos == 0:
                        # print("\a", file=sys.stderr)
                        ca_set_pos(i, 0)
                        buf1 = np.copy(ca_get_data(i))
                        snd.set_position(cacher.nb_frames)
                        cached = True
                        # print(f"its caching... curpos: {curpos}")
                    
                    elif cache_pos < ca_nb_buf:
                        buf1 = np.copy(ca_get_data(i))
                        # snd.set_position(curpos + self._buf_size)
                        cached = True
                        # print(f"its caching... buf_pos: {cacher.buf_pos}, curpos: {curpos}")
                
                # curpos+1 for flac format where last curpos is = endpos -1
                if curpos+1 >= endpos:
                    # debug("curpos >= endpos: %d, %d" %(curpos, endpos))
                    snd.loop_manager()
                    if not snd.is_looping():
                        chan.set_active(0)
                        del active_chan_dic[chan.id]
                        continue
                   
                # whether buf_size =512 frames, so buf =512*4 = 2048 bytes
                # cause buf in byte, one frame = 4 bytes, 2 signed short, 
                # for 16 bits, 2 channels, 44100 rate,
                
                if not cached:
                    buf1 = snd.read_data(self._buf_size)
                if not buf1.size:
                    debug("not buf1")
                    chan.set_active(0)
                    snd.set_play_count(0)
                    del active_chan_dic[chan.id]
                    continue
                else: # whether buf1 have size
                    if len(buf1) < self._len_buf:
                        buf1.resize(self._len_buf)
                        chan.set_active(0)
                        del active_chan_dic[chan.id]

                    # avoid saturation
                    if mixing:
                        buf1 *= self._vol_ratio
                        if chan.is_vel():
                            chan.process_vel(buf1)
                       
                        # verify whether there is a free place
                        num = (num + 1) % len_buf_lst
                        buf_lst[num] = buf1
                        chan_num = num
                        if chan_count < len_buf_lst:
                            chan_count +=1
                            # debug("voici i: %d et shape: %s" %(i, buf1.shape))
            
        # out of the loop
        if buf1.size and not mixing:
            return buf1.tobytes()
        if chan_count == 0: # no more audio data
            # maintaining the audio callback alive
            return self._ret_buf
        elif chan_count == 1: # no copy data
            out_buf = buf_lst[chan_num] 
            return out_buf.tobytes()
        elif chan_count >= 2:
            out_buf = self._mix_buf_data(chan_count, buf_lst)

        if out_buf.size:
            # avoid copy
            
            """
            time.sleep(1)
            print("\a")
            """
            return out_buf.tobytes()
        else: # out_buf  is empty
            return self._ret_buf

    #-----------------------------------------
                          
    def _mix_buf_data(self, chan_count, buf_lst):
        """
        mixing audio data list
        from AudiMixer object
        """

        line = np.sum(buf_lst[0:chan_count], axis=0, dtype=np.float32) # sum each column per line
        return line

    #-----------------------------------------

    def set_mixing(self, mixing):
        """
        set the mix state
        from AudiMixer object
        """

        self._mixing = mixing

    #-----------------------------------------

    def set_cache_data(self, snd_num=0, loops=0, playing=0):
        """
        prepare cache data for playing
        from AudiMixer object
        """
        
        # self.cacher.buf_pos =0
        self.cacher.set_pos(snd_num, 0)
        self._snd_num = snd_num
        self._playing = playing
        # self.cur_func = self.get_cache_data
        
        return True

    #-----------------------------------------

    def get_cache_data(self):
        """
        returns raw data from the cache without Sound object
        from AudiMixer object
        """

        if self._playing:
            data = self.cacher.get_data(self._snd_num)
            if data is not None:
                # convert to byte in float32
                return data.tobytes()
        
        self._playing =0
        # restore previous Audio Callback function
        # self.cur_func = self.get_mix_data
        return self._ret_buf
    
    #-----------------------------------------

    def set_sound_data(self, snd_num=0, loops=0, playing=0):
        """
        prepare sound data for playing
        from AudiMixer object
        """
        
        try:
            snd = self._sound_lst[snd_num]
            chan0 = self._chan_lst[0]
        except IndexError as err:
            print("Error: no sound found.", err)
            return False
        
        snd.set_position(0)
        self._snd_num = snd_num
        self._sound = snd
        chan0.set_active(1)
        self._chan = chan0
        self._playing = playing
        # self.cur_func = self.get_sound_data
        
        return True

    #-----------------------------------------

    def get_sound_data(self):
        """
        returns raw data from the Sound object
        from AudiMixer object
        """

        chan = self._chan
        snd = self._sound
        if snd and chan and chan.is_active():
            # print("\a")
            curpos = snd.get_position(0)
            endpos = snd.get_end_position(0)
            # print(f"curpos: {curpos}, endpos: {endpos}")
            # curpos+1 for flac format where last curpos is = endpos -1
            if curpos+1 >= endpos:
                # snd.set_position(0)
                print("\a")
                chan.set_active(0)
            else:
                data = snd.read_data(self._buf_size)
                if not data.size:
                    chan.set_active(0)
                    return self._ret_buf
                if len(data) < self._len_buf:
                    data.resize(self._len_buf)
                # convert to byte in float32
                return data.tobytes()
            
        self._playing =0
        # restore previous Audio Callback function
        # self.cur_func = self.get_mix_data
        
        # print("\a")
        return self._ret_buf
    
    #-----------------------------------------

    def set_mix_mode(self, mode_num):
        """
        assign to the audio callback the right function to call
        from AudiMixer object
        """

        if mode_num == 0: # with mix with cache 
            self.cacher.set_caching(1)
            self.set_mixing(1)
            self.cur_func = self.get_buf_data
        elif mode_num == 1:  # with mix no cache
            self.cacher.set_caching(0)
            self.set_mixing(1)
            self.cur_func = self.get_buf_data
        elif mode_num == 2:  # no mix with cache
            self.cacher.set_caching(1)
            self.set_mixing(0)
            self.cur_func = self.get_buf_data
        elif mode_num == 3:  # no mix no cache by channel
            self.cacher.set_caching(0)
            self.set_mixing(0)
            self.cur_func = self.get_buf_data
        elif mode_num == 4:  # no mix no cache by Sound
            self.cacher.set_caching(0)
            self.set_mixing(0)
            self.cur_func = self.get_sound_data
        elif mode_num == 5:  # only cache
            self.cacher.set_caching(1)
            self.set_mixing(0)
            self.cur_func = self.get_cache_data

    #-----------------------------------------

    def beep(self, freq=440, lensec=1, loops=-2):
        """ beep square wave through mixer object
        freq: in hertz
        lensec: in second

        loopss: 
        -1: loop the sound infinitly
        0: no looping mode
        """
        
        snd = ausam.AudiSample(mode=1) # empty sample
        rate = 44100
        nbsamp = int(lensec * rate)
        snd = snd.tone(1, freq, nbsamp)
        
        # play the beep on the reserved channel
        self.chan_beep.play(snd, loops)

    #-----------------------------------------

    def create_sample(self, fname):
        """
        create new sound
        from AudiMixer object
        """

        snd = ausam.AudiSample(mode=0)
        snd = snd.load(fname)
        if snd is not None: 
            self._sound_lst.append(snd)

        return snd
    
    #-----------------------------------------

    def create_stream(self, filename):
        # create new stream
        snd = austr.AudiStream()
        snd = snd.load(filename)
        if snd is not None: 
            self._sound_lst.append(snd)

        return snd
    
    #-----------------------------------------

    def create_channel(self, id=-1):
        """
        create channel object
        from AudiMixer object
        """

        # print("je pass par la id: ", id)
        chan = auchan.AudiChannel(id)
        if self.audio_driver:
            chan.set_mix_callback(self.audio_driver)
            self._chan_lst.append(chan)
        
        return chan

    #-----------------------------------------
    
    def close(self):
        print("Closing the mixer...")
        for chan in self._chan_lst:
            chan.stop(closing=True)
        for snd in self._sound_lst:
            snd.close()
        if self.audio_driver:
            self.audio_driver.stop_engine()
            self.audio_driver.close()


    #-----------------------------------------

    def get_sounds(self):
        """
        returns sound list 
        from AudiMixer object
        """

        return self._sound_lst

    #-----------------------------------------

    def  get_channels(self):
        """
        returns channel list 
        from AudiMixer object
        """

        return self._chan_lst

    #-----------------------------------------

    def  get_active_channels(self):
        """
        returns actives channels dic
        from AudiMixer object
        """

        return self._active_chan_dic

    #-----------------------------------------

    def get_last_chan(self):
        """
        returns last channel
        from AudiMixer object
        """

        return self.last_chan

    #-----------------------------------------

    def get_sound_by_id(self, index):
        """
        returns sound from sound list
        from AudiMixer object
        """
        
        try:
            return self._sound_lst[index]
        except IndexError:
            return

    #-----------------------------------------

    def get_chan_by_id(self, index):
        """
        returns channel from chan list
        from AudiMixer object
        """
        
        try:
            return self._chan_lst[index]
        except IndexError:
            return

    #-----------------------------------------

    def get_chan_sound(self, chan_id, snd_id):
        """
        returns channel and sound
        from AudiMixer object
        """

        chan = None
        snd = None
        
        try:
            chan = self._chan_lst[chan_id]
            snd = self._sound_lst[snd_id]
        except IndexError:
            pass
        return (chan, snd)

    #-----------------------------------------


#========================================

if __name__ == "__main__":
    lst = AudiRoll()
    lst.set_list([1,2,3])
    val = lst.last()
    print(f"voici last val: {val}") 
    for i in range(6):
        print(f"voici next val: {lst.next()}") 

    app = AudiMixer()
    app.init()
    input("It's OK...")

#-----------------------------------------

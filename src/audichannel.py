#! /usr/bin/python3
"""
File: audichannel.py:
    Module Audichannel, for Channel and DSP managing
    Date: Sun, 17/07/2022
    Author: Coolbrother
"""
import numpy as np
import audimixer as aumix

class DspEffect(object):
    """ effect manager """
    def __init__(self):
        self._volume =1
        self._panning =1
        self._dsp_lst = []
        # self._dsp_lst = ['dsp_010']

    #-----------------------------------------

    def dsp_volume(self, wavebuf, leftvol, rightvol):
        """ 
        set dsp volume
        # change in place wavebuf
        from DspEffect object
        """

        for i in range(0, len(wavebuf), 2):
            wavebuf[i] *= leftvol
            wavebuf[i+1] * rightvol

    #-----------------------------------------

    def dsp_vel(self, wavebuf, val):
        """ 
        set dsp velocity
        change in place numpy wavebuf 
        from DspEffect object
        """

        
        # must be same type for multipliy in place, so verify wavebuf type at the beginning
        wavebuf *= val
        # print("wavebuf type: ",wavebuf.dtype)

    #-----------------------------------------


    def dsp_pitch(self, wavebuf, val=32):
        # set pitch shifting
        max_val =32
        lst = []
        try:
            for i in range(0, len(wavebuf), max_val):
                lst0 = wavebuf[i:i+val]
                lst.extend(lst0)
        except IndexError:
            # lst = []
            pass

        return lst

    #-----------------------------------------

    def dsp_test(self, wavebuf):
        # set dsp test
        
        lst = []
        """
        # make a pitch
        try:
            for i in range(0, len(wavebuf), 16):
                lst0 = wavebuf[i:i+8]
                lst.extend(lst0)
        except IndexError:
            # lst = []
            pass
        """

        return lst

    #-----------------------------------------


#========================================


class AudiChannel(DspEffect):
    """ channel manager """
    _id =0
    def __init__(self, id=-1):
        DspEffect.__init__(self)
        if id >= 0:
            self.id = id
        else:
            self.id = AudiChannel._id
        AudiChannel._id +=1
        self._sound = None
        self._playing =0
        self._paused =0
        self._active =0
        self._mix_callback = None
        self._mixer = aumix.AudiMixer.get_instance()
        self._maxvol =128.0
        self._maxvel = 128.0 # velocity
        self._volume =1 # self._maxvol / self._maxvol
        self._maxpan =127 # max panoramique volume
        self._leftpan =1 # left channel volume of sample
        self._rightpan =1 # right channel volume of sample
        self._muted =0
        self._leftmute =1 # for left channel mute
        self._rightmute =1 # for right channel mute
        self._vel =1
        self._active_chan_dic = self._mixer._active_chan_dic
        self._curpos =0
        self._vol_ratio = 0.5


    #-----------------------------------------

    def set_mix_callback(self, mix_callback):
        # init the mix callback function for channel
        self._mix_callback = mix_callback

    #-----------------------------------------

    def set_sound(self, sound):
        # set sound to the channel
        self._sound = sound

    #-----------------------------------------

    def get_sound(self):
        """ return the sound from channel object
        """

        return self._sound

    #-----------------------------------------

    def play(self, snd, loops=0):
        """
        play for channel
        from AudiChannel object
        """

        # loops -1: infinitly
        # 0: no looping mode
        if snd is None: return
        
        if self._playing:
            self.stop() # stop previous sound

        self._sound = snd
        
        """
        self._sound.set_loop_count(loops)
        # self._sound.set_loop_mode(1)
        self._sound.loop_manager()
        start_pos = self._sound.get_start_position(0) # in frames
        self._sound.set_position(start_pos)
        # self._sound.active =1
        """
        
        self._active =1
        self._active_chan_dic[self.id] = self
        self._mixer.last_chan = self
        self._playing =1
        self._paused =0
        if self._mix_callback:
            # debug("je suis ici pour voir mixcallback")
            self._mix_callback.start_engine()

    #-----------------------------------------

    def stop(self, closing=False):
        """
        stop channel
        from AudiChannel object
        """

        if self._sound:
            if not closing:
                self._sound.set_position(0)
        self._active =0
        try:
            del self._active_chan_dic[self.id]
        except KeyError:
            pass
        self._sound = None
        self._curpos =0
        self._playing =0
        self._paused =0

    #-----------------------------------------

    def pause(self):
        # pause channel
        if self._sound:
            self._active =0
            self._playing =0
            self._paused =1

    #-----------------------------------------

    def unpause(self):
        # unpause channel
        if self._sound:
            self._active =1
            self._playing =1
            self._paused =0
        if self._mix_callback:
            self._mix_callback.start_engine()

    #-----------------------------------------

    def get_length(self, unit=0):
        # channel length
        val =0
        if self._sound:
            val = self._sound.get_length(unit)

        return val
    #-----------------------------------------
    
    def get_position(self, unit=0):
        # channel position in frames samples, second, or bytes
        val =0
        if self._sound:
            val = self._sound.get_position(unit)
    
        return val
    #-----------------------------------------

    def set_position(self, pos, unit=0):
        # channel position
        # set_position function take frames samples number
        # frames samples, seconds or bytes
        # unit=0: for frames samples
        # unit=1: for seconds
        # unit=2: for bytes
        if self._sound:
            self._sound.set_position(pos, unit)

    #-----------------------------------------

    def rewind(self, step=1):
        # rewind channel, step in sec
        curpos = int(self.get_position(1)) # in sec
        self.set_position(curpos - step, 1) # in sec

    #-----------------------------------------

    def forward(self, step=1):
        # forward channel, step in sec
        curpos = int(self.get_position(1)) # in sec
        curpos += step
        # print("voici curpos: ", curpos)
        self.set_position(curpos, 1) # in sec

    #-----------------------------------------

    def set_start(self):
        self.set_position(0)

    #-----------------------------------------

    def set_end(self):
        len1 = self.get_length()
        self.set_position(len1)
    
    #-----------------------------------------
    
    def is_playing(self):
        # play state for this channel
        return self._playing

    #-----------------------------------------

    def is_paused(self):
        # pause state for this channel
        return self._paused

    #-----------------------------------------

    def is_active(self):
        # active state for this channel
        return self._active

    #-----------------------------------------

    def set_active(self, active):
        # set active state for this channel
        self._active = active

    #-----------------------------------------

    def limit_value(self, lim_left, lim_right, val):
        """ 
        returns value beetwen lim_left, lim_right
        from AudiChannel object
        """
        if val < lim_left: val = lim_left
        elif val > lim_right: val = lim_right

        return val

    #-----------------------------------------
    
    def add_zeros(self, wave_buf, nb_zeros, type=16):
        """ add nb_zero to the wave buffer
        type =: 16, 24  or 32 bits
        """
        # wave_buf is a tuple containing signed short values
        lst = [0] * nb_zeros
        return wave_buf + lst

    #-----------------------------------------

    def get_volume(self):
        # return channel volume
        """
        mute =0 # for both channel side
        if self._muted:
            return mute
        else:
            return self._volume
        """
        
        return self._volume

    #-----------------------------------------

    def set_volume(self, vol):
        """
        set the channel volume
        from AudiChannel object
        """

        self._volume = self.limitvalue(-1, self._maxvol, vol)
        if self._volume >=0:
            self._volume /= self._maxvol
        # self._dsp_lst.append('dsp_001') # volume effect id

    #-----------------------------------------

    def process_volume(self, wavebuf):
        # process channel volume
        self.dsp_volume(wavebuf, self._volume, self._volume)

    #-----------------------------------------

    def is_volume(self):
        """
        returns whether channel volume is activate
        from AudiChannel object
        """

        if self._volume <0: return False
       
        return True

    #-----------------------------------------

    def get_panning(self):
        # return left and right channel for a sample
        return (self._leftpan, self._rightpan)

    #-----------------------------------------

    def set_panning(self, leftpan=127, rightpan=127):
        # set the channel panoramique
        self._leftpan = self.limitvalue(0, self._maxpan, leftpan)
        self._rightpan = self.limitvalue(0, self._maxpan, rightpan)
        self._leftpan /= self._maxpan 
        self._rightpan /= self._maxpan 

    #-----------------------------------------

    def process_panning(self, wavebuf):
        # process channel panning
        return self.dsp_volume(wavebuf, self._leftpan, self._rightpan)

    #-----------------------------------------

    def get_vel(self):
        """
        returns channel velocity
        from AudiChannel object
        """
       
        return self._vel

    #-----------------------------------------

    def set_vel(self, vel):
        """
        set the channel velocity
        from AudiChannel object 
        """
        
        self._vel = self.limit_value(-1, self._maxvel, vel)
        if self._vel >=0:
            self._vel /= float(self._maxvel)

    #-----------------------------------------

    def process_vel(self, wavebuf):
        """
        process channel velocity
        from AudiChannel object
        """

        self.dsp_vel(wavebuf, self._vel)

    #-----------------------------------------

    def is_vel(self):
        """
        returns whether velocity is activate
        from AudiChannel object
        """
       
        if self._vel <0: return False

        return True

    #-----------------------------------------


    def get_mute(self):
        return (self._leftmute, self._rightmute)
    
    #-----------------------------------------

    def set_mute(self, muted=0, chanside=2):
        # set channel mute
        val=0 if muted else 1 # ternary operator
        if chanside == 0: # left channel side
            self._leftmute = val
        elif chanside == 1: # right channel side
            self._rightmute = val
        elif chanside == 2: # both channel side
            self._leftmute = val
            self._rightmute = val

        self._muted = muted


    #-----------------------------------------
        
    def is_muted(self):
        return self._muted
    
    #-----------------------------------------

    def process_mute(self, wavebuf):
        # process channel panning
        return self.dsp_volume(wavebuf, self._leftmute, self._rightmute)

    #-----------------------------------------

    
    def add_effect(self, id_dsp):
        self._dsp_lst.append(id_dsp) # panning effect id

    #-----------------------------------------
        
    def set_effect(self, wavebuf):
        for item in self._dsp_lst:
            if item == 'dsp_001': # volume
                wavebuf = self.dsp_volume(wavebuf, self._volume)
            elif item == 'dsp_002':
                wavebuf = self.dsp_panning(wavebuf, self._leftpan, self._rightpan)
            elif item == 'dsp_010': # test effect
                wavebuf = self.dsp_test(wavebuf)
         
        return wavebuf
    
    #-----------------------------------------

    def write_sound_data(self, data, count):
        """
        write buffer sound in data
        from AudiChannel object
        """

        sound = self._sound
        if sound is None: return
        sound_data = sound.get_data()
        len_sound = sound.get_length() # in frames
        pos = self._curpos
        vol_ratio = self._vol_ratio
        # print(f"curpos: {self._curpos}, len_sound: {len_sound}")
        if pos >= len_sound: 
            self.stop()
            return
        if sound._nchannels == 1:
            for i in range (count):
                if pos >= len_sound: break
                data[2*i] += sound_data[pos] # * vol_ratio
                data[2*i+1] += sound_data[pos] # * vol_ratio
                pos += 1
        elif sound._nchannels == 2:
            for i in range (count):
                if pos >= len_sound: 
                    break
                data[2*i] +=  sound_data[2*pos] # * vol_ratio
                data[2*i+1] += sound_data[2*pos+1] # * vol_ratio
                pos += 1
        else:
            return
        data *= vol_ratio     
        self._curpos = pos
        # print("\a")

    #-----------------------------------------


#========================================




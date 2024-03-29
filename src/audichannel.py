#! /usr/bin/python3
"""
File: audichannel.py:
    Module Audichannel, for Channel and DSP managing
    Date: Sun, 17/07/2022
    Author: Coolbrother
"""
import numpy as np
import audimixer as aumix
import utils as uti
import logging as log
# log.basicConfig(level=log.DEBUG, filename="/tmp/app.log", filemode='w')

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


    def dsp_speed(self, wavebuf, val=32):
        # set speed shifting
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
        # make a speed
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

class SimpleDelay(object):
    """ Simple delay effect manager """
    def __init__(self, time: float, decay: float, rate: int=44100):
        """ 
        Init the Delay object 
        from SimpleDelay object
        """
        
        self._time = time # in seconds
        self._decay = decay # in gain
        self._rate = rate
        self._pos =0
        self._buf_size = int(self._time * self._rate)
        # Init the buffer with zeros
        self._buffer = np.zeros((self._buf_size), dtype=np.float32)
        self._active =0 # deactivate the delay by default

    #-----------------------------------------

    def get_time(self):
        """
        returns delay time
        from SimpleDelay object
        """

        return self._time

    #-----------------------------------------

    def set_time(self, time):
        """
        set the delay time and reinit the data buffer
        from SimpleDelay object
        """
        
        self._time = uti.limit_value(time, 0.1, 5.0)
        self._pos =0
        self._buf_size = int(self._time * self._rate)
        # Init the buffer with zeros
        self._buffer = np.zeros((self._buf_size), dtype=np.float32)

    #-----------------------------------------

    def get_decay(self):
        """
        returns delay decay
        from SimpleDelay object
        """

        return self._decay

    #-----------------------------------------

    def set_decay(self, decay):
        """
        set delay decay
        from SimpleDelay object
        """

        self._decay = uti.limit_value(decay, 0.0, 1.0)

    #-----------------------------------------
    
    def write_sound_data(self, data, count):
        """ 
        mix buffer data with original data
        from SimpleDelay object 
        """
        pos = self._pos
        buffer = self._buffer
        decay = self._decay
        buf_size = self._buf_size
        
        for i in range(count):
            # Mix sample with the one in the buffer at position pos
            data[i] += buffer[pos] * decay
            # Record the sample in the buffer at position pos
            buffer[pos] = data[i]
            
            pos = (pos +1)  % buf_size

        self._pos = pos

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
        self._left_gain =0.5 # left channel volume of sample
        self._right_gain =0.5 # right channel volume of sample
        self._muted =0
        self._leftmute =1 # for left channel mute
        self._rightmute =1 # for right channel mute
        self._vel =1
        self._active_chan_dic = self._mixer._active_chan_dic
        self._curpos =0
        self._looping = False
        self._vol_mix = 0.5 # mix saturation volume
        self._speed = 1.0
        self._pan =0
        self._buf_len =0
        self._buf_pos =0
        self._wav_pos =0
        self._count =0

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
            # uti.beep()
            # print(f"Error: KeyError when deleting channel: {self.id}")
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
        Deprecated function.
        Use the one in utils module instead
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

    def get_volume0(self):
        """
        returns channel volume
        from AudiChannel
        """

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

        self._volume = uti.limit_value(vol, 0.0, 1.0)

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

    def get_pan(self):
        """
        returns pan value for both channels side
        from AudiChannel object
        """

        return self._pan

    #-----------------------------------------

    def set_pan(self, pan):
        """
        set the pan for both channels side
        from AudiChannel object
        """
        # pan varie from -1.0 to 1.0
        self._pan = uti.limit_value(pan, -1.0, 1.0)
        self.update_pan()

    #-----------------------------------------

    def update_pan(self):
        """
        Linear Panning
        updating both channels side
        from AudiChannel object
        """

        # pan varie from -1.0 to 1.0
        # left_gain and right_gain varie from 0 to 1.0
        pos = self._pan * 0.5
        self._left_gain = 0.5 - pos
        self._right_gain = pos + 0.5

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
                wavebuf = self.dsp_panning(wavebuf, self._left_gain, self._right_gain)
            elif item == 'dsp_010': # test effect
                wavebuf = self.dsp_test(wavebuf)
         
        return wavebuf
    
    #-----------------------------------------

    def is_looping(self):
        """
        returns looping mode
        from AudiChannel object
        """

        return self._looping

    #-----------------------------------------

    def set_looping(self, looping):
        """
        set looping mode
        from AudiChannel object
        """

        self._looping = looping

    #-----------------------------------------

    def get_speed(self):
        """
        returns channel speed
        from AudiChannel
        """
       
        return self._speed

    #-----------------------------------------

    def set_speed(self, speed):
        """
        set the channel speed
        from AudiChannel object
        """

        self._speed = uti.limit_value(speed, 0.25, 4.0)

    #-----------------------------------------

    def linear_interpolation(self, val_a, val_b, val):
        """
        Linear Interpolation formula, for speed modulation
        """
        
        # Notes:
        # return val_a * (1 - val) + val * val_b
        # return val_a + ((val_b - val_a) * val)
        return val_a + (val * (val_b - val_a))

    #-----------------------------------------
    
    def write_sound_data(self, data, count):
        """
        write buffer sound in data
        from AudiChannel object
        """

        # print(f"voici count: {count}, len_data: {len(data)}")
        sound = self._sound
        if sound is None: return
        sound_len = sound.get_length() # in frames
        if not sound_len: return
        nb_channels = sound._nchannels
       
        if sound.sound_type == 0: # Sample type
            self.mix_sample_data(data, count, sound, sound_len, nb_channels)
        elif sound.sound_type == 1: # Stream type
            self.mix_stream_data(data, count, sound, sound_len, nb_channels)

    #-----------------------------------------

    def mix_sample_data(self, data, count, sound, sound_len, nb_channels):
        """
        Mix Sound Sample data
        from AudiChannel object
        """

        curpos = self._curpos
        vol = self._volume * self._vol_mix
        speed = self._speed
        left_gain = self._left_gain
        right_gain = self._right_gain
        buf_data = sound.get_data()

        if nb_channels == 1:
            for i in range (0, count, 2):
                # uti.beep()
                if curpos +1 >= sound_len:
                # Loop manager
                    if self._looping:
                        curpos =0
                    else: # No looping
                        self.stop()
                        return

                pos = int(curpos)
                frac_pos = curpos - pos
                if speed == 1.0: # no speeding
                    val = buf_data[pos] * vol
                    data[i] += val * left_gain
                    data[i+1] += val * right_gain
                else: # speeding
                    # Linear Interpolation
                    val = (buf_data[pos] + frac_pos * (buf_data[pos+1] - buf_data[pos])) * vol
                    data[i] += val * left_gain
                    data[i+1] += val * right_gain

                curpos += speed

        elif nb_channels == 2:
            for i in range (0, count, 2):
                if curpos +1 >= sound_len:
                    # Loop manager
                    if self._looping:
                        curpos =0
                    else: # No looping
                        self.stop()
                        return

                pos = int(curpos * 2)
                if speed == 1.0: # no speed
                    if curpos + 1 >= sound_len: break
                    val = buf_data[pos] * vol
                    data[i] += val * left_gain
                    val = buf_data[pos+1] * vol
                    data[i+1] += val * right_gain

                else: # speeding
                    if curpos + 2 >= sound_len: break
                    # Linear Interpolation
                    val = (buf_data[pos] + frac_pos * (buf_data[pos+1] - buf_data[pos])) * vol
                    data[i] += val * left_gain
                    val = (buf_data[pos+1] + frac_pos * (buf_data[pos+2] - buf_data[pos+1])) * vol
                    data[i+1] +=  val * right_gain
            
                curpos += speed

        else: # 0 or more than 2 channels
            return


        self._curpos = curpos

    #-----------------------------------------

    def mix_stream_data(self, data, count, sound, sound_len, nb_channels):
        """
        Mix Stream Sound data
        from AudiChannel object
        """

        vol = self._volume * self._vol_mix
        # Speed Not Implemented YET
        speed = 1.0 # self._speed
        left_gain = self._left_gain
        right_gain = self._right_gain
        curpos = self._curpos
        wav_pos  =0 
        buf_pos = sound.buf_pos
        buf_len = sound.buf_len
        nb_samples = buf_pos * nb_channels
        nb_frames = count * 4 # 4
        
        """
        if not hasattr(self, "_count"):
            self._count =0
        # uti.beep()i
        """
        
        if curpos == 0:
            sound.set_position(0)
            sound.buf_pos =0
            buf_pos =0
            self._buf_len =0

        sound_pos = sound.get_position(0) # in frames
        endpos = sound.get_end_position(0) # in frames
        # TODO: Unable to call sound.get_data function, no way to know why???
        # buf_data = sound.get_data() # in samples
        buf_data = sound.get_raw_data() # in samples
        
        # print(f"curpos: {curpos}, sound_len: {sound_len}")
        if sound_pos >= sound_len and nb_samples >= buf_len:
            # print(f"Revoici curpos: {curpos}, _buf_len: {self._buf_len}\nsound_len: {sound_len}")
            
            msg = f"Finishing with count: {self._count}:\n"\
                + f"    sound_pos: {sound_pos}, buf_pos: {buf_pos}, nb_samples: {nb_samples},\n"\
            + f"    buf_len: {buf_len}, self._buf_len: {self._buf_len}, self._curpos: {self._curpos}\n"\
            + "###----------------------------------------"
            log.info(msg)
            # log.disable(log.CRITICAL+1)
            # self.stop()
            # return
            if self._looping:
                self._curpos =0
                sound.buf_pos =0
                self._buf_len =0
                sound.set_position(0)
            else: # No looping
                self.stop()
            # print("Not buf_data.size")
            self._buf_len =0
            sound.buf_pos =0
            self._count =0
            return

        # print(f"voici curpos: {curpos}, buf_len: {buf_len}, wav_pos: {wav_pos}")

        if curpos == 0:
            msg_head = f"With Count: {self._count}, sound_len: {sound_len}, nb_frames: {nb_frames}, nb_channels: {nb_channels}, speed: {speed}\n"
            log.info(msg_head)
        
        msg0 = f"    sound_pos: {sound_pos}, buf_pos: {buf_pos}, nb_samples: {nb_samples},\n"\
            + f"    buf_len: {buf_len}, self._buf_len: {self._buf_len}, self._curpos: {self._curpos}"
        
        msg = f"Voici count: {self._count}\n"\
            + msg0
        log.info(msg)
        # return

        if curpos == 0 or nb_samples >= buf_len:
            # reading nb_frames frames
            # and updates: sound.buf_len, sound.buf_pos variables
            buf_data = sound.read_frames(nb_frames)
            sound_pos = sound.get_position()
            # uti.beep()
            if not buf_data.size:
                self.stop()
                # print(f"voici curpos: {curpos}, _len_buf: {self._buf_len},\nSound_len: {sound_len}")
                self._buf_len =0
                sound.buf_pos =0
                return
            else: # data is valid
                buf_len = sound.buf_len
                self._buf_len += buf_len
                sound.buf_pos =0
                buf_pos =0
                nb_samples =0

                msg = f"After Reading data with Count: {self._count}\n"\
                    + f"    sound_pos: {sound_pos}, buf_pos: {buf_pos}, nb_samples: {nb_samples},\n"\
                    + f"    buf_len: {buf_len}, self._buf_len: {self._buf_len}, self._curpos: {self._curpos}"
                log.info(msg)
                # print(f"voici curpos: {curpos}, buf_len: {buf_len}, wav_pos: {wav_pos}")

                # print(f"curpos: {curpos}, buf_len: {buf_len}, _buf_len: {self._buf_len}, sound_len: {sound_len}")
                if buf_len < count:
                    count = buf_len
                # print(f"voici buf_len: {buf_len}")

        
        if nb_channels == 1:
            for i in range(0, count, 2):
                index = nb_samples + wav_pos
                pos = int(index)
                # frac_pos = index - pos
                if pos >= buf_len: break
                val = buf_data[pos] * vol
                data[i] += val * left_gain
                data[i+1] += val * right_gain
                
                """
                # Speed Not Implemented
                if speed == 1.0: # no speeding
                    if pos >= buf_len: break
                    val = buf_data[pos] * vol
                    data[i] += val * left_gain
                    data[i+1] += val * right_gain
                else: # speeding
                    # Linear Interpolation
                    if pos +1 >= buf_len: 
                        # print(f"In the Loop, _count: {self._count}, buf_pos: {buf_pos:0.3f}, buf_len: {buf_len}, curpos: {curpos:0.3f}")
                        break
                    
                    val = (buf_data[pos] + frac_pos * (buf_data[pos+1] - buf_data[pos])) * vol
                    # print(f"Voici pos: {pos}, buf_len: {buf_len}")
                    data[i] += val * left_gain
                    data[i+1] += val * right_gain
                """

                wav_pos += speed
        
        elif nb_channels == 2:
            for i in range(0, count, 2):
                index = nb_samples + (wav_pos * 2) # nb_channels
                pos = int(index)
                # frac_pos = index - pos
                if pos + 1 >= buf_len: break
                val = buf_data[pos] * vol
                data[i] += val * left_gain
                val = buf_data[pos+1] * vol
                data[i+1] += val * right_gain

                """
                # Speed Not Implemented
                if speed == 1.0: # No speeding
                    if pos + 1 >= buf_len: break
                    val = buf_data[pos] * vol
                    data[i] += val * left_gain
                    val = buf_data[pos+1] * vol
                    data[i+1] += val * right_gain

                else: # speeding
                    if pos + 2 >= buf_len: break
                    # Linear Interpolation
                    val = (buf_data[pos] + frac_pos * (buf_data[pos+1] - buf_data[pos])) * vol
                    data[i] += val * left_gain
                    val = (buf_data[pos+1] + frac_pos * (buf_data[pos+2] - buf_data[pos+1])) * vol
                    data[i+1] +=  val * right_gain
                """


                wav_pos += speed
            
        else:  # No channel or more than 2
            return


        # """

        # print(f"self._curpos: {self._curpos}, wav_pos: {wav_pos}")
        self._curpos += wav_pos
        sound.buf_pos += wav_pos
        self._count +=1

        return

    #-----------------------------------------

#========================================


if __name__ == "__main__":
    chan = AudiChannel()
    print(f"Channel id: {chan.id}")
    input("It's OK...")

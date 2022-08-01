#python3
"""
    File: audibase.py
    Module for common variables audios.
    Date: Sun, 17/07/2022
    Author: Coolbrother
"""

class AudiSoundBase(object):
    """ common object for sample and stream
    """
    def __init__(self):
        """
        """
        super(AudiSoundBase, self).__init__()
        self._filename = ""
        self._id = id
        self._wavfile = None
        self._wavbuf_lst = []
        self._nchannels =1
        self._sampwidth =1
        self._rate =1
        self._nframes =0
        self._bits =1
        self._maxamp = pow(2, 15) -1 # max amplitude, short 32767
        self._curpos =0
        self._length =0
        self._looping =0
        self._loop_mode =0
        self._loop_count =0
        self._loop_start =0
        self._loop_end =0
        self._play_count =0
        self._buf_arr = None # for numpy array
        self._soundbuf = None # for SoundBuffer object
 
    #------------------------------------------------------------------------------
    
    def load(self, filename):
        """ generic method from soundbase object
        """

    #-----------------------------------------

    def close(self):
        """ generic method from soundbase object
        """

    #-----------------------------------------

    def get_params(self):
        """  return sound params from soundbase object
        """
        
        return (self._nchannels, self._sampwidth, self._rate, self._nframes)
    
    #-----------------------------------------

    def set_params(self, nchannels, sampwidth, rate, nframes):
        """  set sound params from soundbase object
        """

        self._nchannels = nchannels
        self._sampwidth = sampwidth
        self._rate = rate
        self._nframes = nframes

        self._length = self._nframes
        
    #-----------------------------------------

    def read_data(self, nb_frames):
        """ generic method from soundbase object
        """

    #-----------------------------------------

    def unit_to_frames(self, val, unit):
        """ convert any value to frames from soundbase object
        keywords arguments
        val :
        value to convert
        unit :
        the unit's value , must be
        0 -- value in frames
        1 -- value in seconds
        2 -- value in samples
        3 -- value in bytes
        """

        res =0
        if unit == 0: # frames to frames
            res = int(val)
        elif unit == 1: # secs to frames
            res = int(val * self._rate)
        elif unit == 2: # samples to frames
            res = int(val / self._nchannels)
        elif unit == 3: # bytes to frames
            res = int(val / (self._nchannels * self._sampwidth))
        
        return res
    
    #------------------------------------------------------------------------------

    def frames_to_unit(self, val, unit):
        """ convert any frames values to unit from soundbase object
        keywords arguments
        val :
        frames value to convert
        unit :
        the unit's value , must be
        0 -- value in frames
        1 -- value in seconds
        2 -- value in samples
        3 -- value in bytes
        """

        res =0
        if unit == 0: # frames to frames
            res = int(val)
        elif unit == 1: # frames to sec
            res = val / float(self._rate)
        elif unit == 2: # frames to samples
            res = int(val * self._nchannels)
        elif unit == 3: # frames to  bytes
            res = int(val * self._nchannels * self._sampwitdh)
        
        return res
    
    #------------------------------------------------------------------------------

    def get_position(self, unit=0):
        """ generic method from soundbase object
        """

    #-----------------------------------------

    def set_position(self, pos, unit=0):
        """ generic method from soundbase object
        """

    #-----------------------------------------

    def get_start_position(self, unit=0):
        """ return start sound  position from soundbase object
        """
       # loopstart in frames 
        start_pos =0
        if self._looping:
            start_pos = self._loop_start
        
        # convert start_pos to unit
        start_pos = self.frames_to_unit(start_pos, unit)
        
        return start_pos

    #-----------------------------------------
 
    def get_end_position(self, unit=0):
        """ return end sample position from soundbase object
        """
        # loopend in frames
        end_pos =0
        if self._looping:
            end_pos = self._loop_end
        else:
           end_pos = self._length # in frames by default

        # convert end_pos to unit
        end_pos = self.frames_to_unit(end_pos, unit)
 
        return end_pos

    #-----------------------------------------
    
    def get_length(self, unit=0):
        """ get wave length from soundbase object
        unit =0: in frames
        1: in second
        2: in samples
        3: in bytes
        """
        # self._length in frames
        # convert length to unit
        val = self.frames_to_unit(self._length, unit)
       
        return val

    
    #-----------------------------------------

    def set_length(self):
        """ set wave length in frames from soundbase object
        """
        self._length = len(self._wavbuf_lst) / self._nchannels
   
        return self._length

    #-----------------------------------------
            
    def get_num_frames(self):
        """ return total frames from soundbase object
        """

        return self._nframes

    #-----------------------------------------

    def get_num_channels(self):
        """ return number of channels from soundbase object
        """

        return self._nchannels

    #-----------------------------------------

    def reverse(self):
        """
        reverse sound
        from AudiSoundBase object
        """
        
       
    #-----------------------------------------
 
    def is_mono(self):
        """
        returns whether the audio file is mono
        from AudiBase object
        """

        return self._nchannels == 1

    #-----------------------------------------

    def get_raw_list(self):
        """ return the sound raw data from soundbase object
        """

        return self._wavbuf_lst

    #-----------------------------------------

    def is_looping(self):
        """ whether is looping or not from soundbase object
        """
        
        return self._looping

    #-----------------------------------------
    
    def loop_manager(self):
        """ manage the loopback mode from soundbase object
        """

        play_count = self._play_count
        if self._loop_mode and self._loop_count:
            if play_count < self._loop_count:
                if self._loop_start < self._loop_end:
                    self.set_position(self._loop_start, 0) # in frames
                else: # loopstart >= loopend
                    self.set_position(0, 0) # in frames
                play_count +=1
                self.set_play_count(play_count)
                self._looping =1
            else: # playcount >= loopcount
                self.set_play_count(0)
                self._looping =0
        else:
            self._looping =0
        
        return self._looping
    
    #-----------------------------------------

    def get_loop_mode(self):
        """ return loop mode from soundbase object
            1 for looping, 0 for not
        """        
        
        return self._loop_mode

    #-----------------------------------------

    def set_loop_mode(self, mode):
        """ set the loop mode from soundbase object
            mode =1 -- for looping, 0 for not
        """
        
        if mode == 1:
            if self._loop_start == 0 and self._loop_end == 0:
                self.set_loop_points(0, self._length, 0) # in frames
        
        self._loop_mode = mode
        self.loop_manager()

    #-----------------------------------------

    def get_loop_count(self):
        """ return loop count from soundbase object
        """

        return self._loop_count

    #-----------------------------------------

    def set_loop_count(self, loopcount=0):
        """ set loop count from sample obase object
        loops=-1: --  looping infinitly
        """
        
        inf = 65535
        if loopcount == -1:
            self._loop_count = inf
        elif loopcount >= 0:
            self._loop_count = loopcount

    #-----------------------------------------

    def get_loop_points(self, unit=0):
        """ return loop points from soundbase object
        """
        loop_start = self.frames_to_unit(self._loop_start, unit)
        loop_end = self.frames_to_unit(self._loop_end, unit)

        return (loop_start, loop_end)

    #-----------------------------------------

    def set_loop_points(self, start=0, end=-1, unit=0):
        """ set loop points from soundbase object
        unit: -- frames, seconds, samples or bytes
        unit=0: for frames
        unit=1: for seconds
        unit=2: for samples
        unit=3: for bytes
        """
        
        """
        if unit == 1: # in seconds
            start *= self._rate
            end *= self._rate
        elif unit == 2: # in bytes
            # belong the framesize or samplesize
            start /= (self._nchannels  * self._sampwidth)
            end /= (self._nchannels  * self._sampwidth)
        """
            
        if end == -1:
            end = self._length # in frames
        self._loop_start = self.unit_to_frames(start, unit)
        self._loop_end = self.unit_to_frames(end, unit)

    #-----------------------------------------

    def get_play_count(self):
        """ return play count from soundbase object
        """
        return self._play_count

    #-----------------------------------------

    def set_play_count(self, count):
        """ set play count from soundbase object
        """

        self._play_count = count

    #-----------------------------------------
    
    def add_zeros(self, wave_buf, nb_zeros, type=16):
        """ add nb_zero to the wave buffer from soundbase object
        type =: 16, 24  or 32 bits
        # wave_buf: list containing signed short values
        """
        lst = [0] * nb_zeros
        
        return wave_buf + lst

    #-----------------------------------------

    
#========================================


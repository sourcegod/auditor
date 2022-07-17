#! /usr/bin/python3
"""
    File: audisound.py
    Module for Sample and Stream manager
    Date: Sun, 17/07/2022
    Author: Coolbrother
"""

import struct
import wave
import numpy as np

class CWave16BitsStereo(object):
    """ wave manager """
    def __init__(self):
        self.rate =44100
        self.bitspersample =16
        self.nbchannels =2
        self.leftchannel = None
        self.rightchannel = None
        self.len =0

    #------------------------------------------------------------------------------
                
#========================================

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
        self._nchannels =0
        self._sampwidth =0
        self._rate =0
        self._nframes =0
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

class AudiSample(AudiSoundBase): # object is necessary for property function
    """ sample manager """
    def __init__(self, mode=0, filename="", bits=16, rate=44100, channels=2, nbsamples=1):
        super(AudiSample, self).__init__()
        if mode == 0 and filename: # load sample from file
            self.load(filename)
        elif mode == 1: # create empty sample
            self.init_sample(bits, rate, channels, nbsamples)

    #-----------------------------------------
    
    def __str__(self):
        # sound string
        return str(self.__dict__)

    #-----------------------------------------

    def __eq__(self, other):
        # sound compare with == operator
        return self.__dict__ == other.__dict__

    #-----------------------------------------

    def load(self, filename):
        """ load entire sound into memory from audisample object
        """

        self._filename = filename
        wave_data = None        

        try:
            self._wavfile = wave.open(self._filename, 'rb')
        except IOError:
            print("Error: unable to open file: %s" % self._filename)
            return
        
        # sampwidth: number of byte per samples: in bytes
        # nchannels: number of channels
        # rate: sampling rate per second
        # nframes: total number of samples for audio data in bytes
        # framesize = nchannels * sampwidth = 4 bytes (2*2)
        # for 2 channels, 16 bits
        self._nchannels = self._wavfile.getnchannels()
        self._sampwidth = self._wavfile.getsampwidth()
        self._rate = self._wavfile.getframerate()
        self._nframes = self._wavfile.getnframes()

        # duration = nframes / rate in second
        # length in second
        # length = (self._nchannels * self._sampwidth * self.nframes) / 
        # (self._nchannels * self._sampwidth * self._rate)
        # equiv': self._length = self._nframes / float(self._rate)
        try:
            wave_data = self._wavfile.readframes(self._nframes)
            self._wavfile.close()
        except IOError:
            print("Error: unable to load in memory wave file: %s" % self._filename)
            self._wavfile.close()
            return
            
        
        size = self._nframes * self._nchannels # size is in short, not in byte
        # struct.unpack return a tuple, must be converted in list
        self._wavbuf_lst = list(struct.unpack('<'+size*'h', wave_data))
        # self._length = len(self._wavbuf_lst)
        self._length = self._nframes # in frames
        
   
        return self._wavbuf_lst
    
    #-----------------------------------------

    def close(self):
        """ close sample from audisample object
        """
        pass

    #-----------------------------------------

    def init_sample(self, bits=16, rate=44100, channels=2, nbsamples=44100):
        # create new sound
        # sampwidth: number of byte per samples: in bytes
        # nchannels: number of channels
        # rate: sampling rate per second
        # nframes: total number of samples for audio data in bytes
        # framesize = nchannels * sampwidth = 4 bytes (2*2)
        # for 2 channels, 16 bits
        
        self._nchannels = channels
        self._rate = rate
        self._sampwidth = bits * channels / 8 
        self._nframes = nbsamples 

        # duration = nframes / rate in second
        # length in second
        # length = (self._nchannels * self._sampwidth * self.nframes) / 
        # (self._nchannels * self._sampwidth * self._rate)
        # equiv':
        self._length = self._nframes * self._nchannels
        self._wavbuf_lst = [0] * nbsamples * channels
        
        return self
    #-----------------------------------------

    def read_data(self, nb_frames):
        """ read nb_frames frames in file in memory from audisample object
        """
        # frames = 4 bytes, 2 signed short
        # for 2 channels, 16 bits, 44100 rate
        buf_lst = []
        nb_samples = nb_frames * self._nchannels # in samples
        pos = int(self._curpos * self._nchannels)
        start_pos = self.get_start_position(2) # * self._nchannels # in samples
        end_pos = self.get_end_position(2) # in samples
        # debug("voici end_pos %d" % end_pos)
        # return
        if pos < end_pos:
            if pos + nb_samples < end_pos:
                step = pos + nb_samples
                try:
                    buf_lst = self._wavbuf_lst[pos:step]
                except IndexError:
                    # debug("Error in read_data from sample object, voici step: %d" % step)
                    print("index_rror: unable to index in read_data from sample object")
                
                self._buf_arr = np.array(buf_lst, dtype='int16')
                self._curpos = step / self._nchannels
            else: # nb_frames is too large
                if self.is_looping():
                    # debug("voici loopmode: %d, loopcount: %d" %(self._loop_mode, self._loop_count))
                    len1 = len(self._wavbuf_lst[pos:end_pos])
                    len2 = nb_samples - len1
                    buf_lst = self._wavbuf_lst[pos:end_pos] + self._wavbuf_lst[start_pos:start_pos+len2]
                    self._buf_arr = np.array(buf_lst, dtype='int16')
                    self._curpos = start_pos
                else: # no looping
                    # add zeros at the end to adjust length sample
                    len1 = len(self._wavbuf_lst[pos:end_pos])
                    # nb_zeros = nb_samples - len1
                    buf_lst = self._wavbuf_lst[pos:end_pos]
                    # buf_lst = self.add_zeros(buf_lst, nb_zeros)
                    # arr = np.zeros(1024, dtype='int16')
                    self._buf_arr = np.array(buf_lst, dtype='int16')
                    self._buf_arr.resize(nb_samples)
                    self._curpos = end_pos -1
                    # debug("voici pos: %d, end_pos: %d, len1 %d, nb_zeros %d, et len_buf %d" %(pos, end_pos, len1, nb_zeros, len(buf_lst)))
        else: # whether pos > to sample length
            # debug("je passe dans read_data de sample : %d bytes" % len(buf_lst)) 
            pass

       
        # return buf_lst
        return self._buf_arr
    
    #-----------------------------------------
    
    def get_position(self, unit=0):
        """ get position for audisample object
        """
        # position in frames, second, samples, or bytes
        val =0 # curpos is in frames
        # unit=0: in frames
        # convert curpos to unit
        val = self.frames_to_unit(self._curpos, unit)
       
        # debug("voila dans sample object, get_position, val : %f " % val)
        return val

    #-----------------------------------------


    def set_position(self, pos, unit=0):
        """ set sound position from audisample object
        """
        # set_position function take frames samples number
        # frames, seconds, samples or bytes
        # unit=0: for frames samples
        # unit=1: for seconds
        # unit=2: for bytes
        # convert pos to frames bellong unit
        pos = self.unit_to_frames(pos, unit)
        if pos <0:
            pos =0
        elif pos >= self._length: # length in frames
            pos = self._length -1
        
        self._curpos = pos
        # debug("coucou %d" % pos)

    #-----------------------------------------

   
    def reverse(self):
        # reverse sound
        if self._wavbuf_lst:
            self._wavbuf_lst.reverse()
        # print self._wavbuf_lst

    #-----------------------------------------
    
    def get_raw_list(self):
        # return the sound raw data
        return self._wavbuf_lst

    #-----------------------------------------

    def set_raw_list(self, lst):
        # change raw list
        self._wavbuf_lst = lst

    #-----------------------------------------

    def set_raw_list(self, start, nbsamples):
        # set the sound raw data
        # wavbuf_lst is in short one channel per value
        start *= self._nchannels
        nbsamples *= self._nchannels
        length = start + nbsamples 
        try:
            self._wavbuf_lst = self._wavbuf_lst[start:length]
        except IndexError:
            return None
        
        return self._wavbuf_lst
    
    #-----------------------------------------

    def set_raw_range(self, start, end):
        # set the range raw data without calculate length of data to set
        # wavbuf_lst is in short one channel per value
        start *= self._nchannels
        end *= self._nchannels
        try:
            self._wavbuf_lst = self._wavbuf_lst[start:end]
        except IndexError:
            return None
        
        return self._wavbuf_lst
    
    #-----------------------------------------

    def mix_raw_list(self, start1, len1, lst1, mixstart=0):
        # merge list1 to the current sound list
        # lst1 must be <= lwavbuf_lst
        # wavbuf_lst is in short one channel per value
        start1 *= self._nchannels
        len1 *= self._nchannels
        mixstart *= self._nchannels
        try:
            for i in range(start1, len1):
                # avoid sound clipping
                sm = self._wavbuf_lst[i+mixstart] + lst1[i]
                data = min(max(sm, -32767), 32767)
                self._wavbuf_lst[i+mixstart] = data
        except IndexError:
            pass
        
        return self._wavbuf_lst
    
    #-----------------------------------------

    def change_raw_list(self, start1, len1, val=0):
        # change the current sound list
        # wavbuf_lst is in short one channel per value
        start1 *= self._nchannels
        len1 *= self._nchannels
        try:
            for i in range(start1, len1):
                self._wavbuf_lst[i] = val
        except IndexError:
            pass
        
        return self._wavbuf_lst
    
    #-----------------------------------------


    def new_sample(self, bits=16, rate=44100, channels=2, nbsamples=44100):
        # create new sample
        mode =1
        samp = AudiSample(mode, "", bits, rate, channels, nbsamples)

        return samp

    #-----------------------------------------

    def copy_sample(self, start, nbsamples):
        # copy sample
        snd = copy.deepcopy(self)
        snd.set_raw_list(start, nbsamples)

        return snd
    
    #-----------------------------------------

    def cut_sample(self, from1=0, nbsamples=0):
        # cut sample, 
        # from1=0: from begining
        # from1=1: from end
        start=0
        if from1 == 0:
            start = nbsamples
            len1 = self.get_length()
        else:
            start=0
            len1 = self.get_length() - nbsamples
        snd = self.copy_sample(start, len1)

        return snd
    
    #-----------------------------------------

    def crop_sample(self, start, nbsamples):
        # cut each part outside the selection
        len1 = self.get_length()
        if start <0:
            start =0
        if nbsamples <= 0 or nbsamples > len1:
            nbsamples = len1
        
        snd = copy.deepcopy(self)
        snd.set_raw_list(start, nbsamples)

        return snd
    
    #-----------------------------------------

    def insert_sample(self, samp, start, nbsamples, ins_start):
        """ insert a new sample to the old sample
        ins_start: the point to insert the new sample
        """
        len1 = self.get_length()
        samp = samp.copy_sample(start, nbsamples)
        if ins_start <0:
            ins_start =0
        if ins_start > len1:
            ins_start = len1
       
        snd = copy.deepcopy(self)
        snd_raw = snd.get_raw_list()
        try:
            part1 = snd_raw[0, ins_start]
            part2 = samp.get_raw_list()
            if ins_start < len1:
                part3 = snd_raw[ins_start:]
            else:
                part3 = []
        except IndexError:
            return snd
        
        lst = part1 + part2 + part3
        snd.set_raw_list(lst)

        return snd
    
    #-----------------------------------------

    def erase_sample(self, start=0, len1=-1):
        # erase sample, not delete
        if len1 == -1:
            len1 = self.get_length() 

        snd = self.copy_sample(0, self.get_length())
        # fill val to the rawlist
        snd.change_raw_list(start, len1, val=0)

        return snd
    
    #-----------------------------------------
        
    def mix_sample(self, samp2, start2, len2, mixstart=0):
        # mix two samples
        # mix samp2 to samp1 with start2 and len2 of samp2, at mixstart of samp1
        lst1 = self.get_raw_list()
        len1 = self.get_length()
        lst2 = samp2.get_raw_list()
        len3 =0
        start3 = start2 + mixstart
        if start3 == 0:
            if len2 <= len1:
                len3 = len1
            else:
                len3 = len2
        
        elif start3 >0 and start3 < len1:
            if len2 <= len1:
                len3 = len1
            else:
                len3 = len1 + (len2 - len1)
        
        elif start3 >= len1:
                len3 = len1 + len2
        
        # create new sample
        samp3 = self.new_sample(nbsamples=len3)
        samp3.mix_raw_list(0, len1, lst1, 0)
        samp3.mix_raw_list(start2, len2, lst2, mixstart)

        return samp3
    #-----------------------------------------

    def concat_sample(self, samp2):
        # concat samp1 to samp2
        # it's a mix for samp2 at the end of samp1
        return self.mix_sample(samp2, 0, samp2.get_length(), self.get_length())

    #-----------------------------------------
        
    def delete_sample(self):
        self.set_raw_list([])
        self.active =0
    
    #-----------------------------------------

    
    def tone(self, type=0, freq=440, nbsamp=44100):
        # create tone wave with nbsamp samples
        # type=0: sine wave
        # type=1: square wave
        # type=2: sawtooth wave
        # type=3: triangle wave
        # type=4: whitenoise wave
        # type=5: silence wave
        
        samp = self.new_sample(nbsamples=1)
        samp._gen_wave(type, freq, nbsamp)

        return samp

    #-----------------------------------------

    
    def _triangle_sine(self, n):
        # return triangular sine of n
        x = n % 1
        if x <= .25:
            return x
        if x <= .75:
            return .5 - x

        return x -1
    
    #-----------------------------------------

    def _gen_wave(self, type=0, freq=440, nbsamples=44100):
        # generate nbsamples sine raw data
        # create tone wave with nbsamp samples
        # type=0: sine wave
        # type=1: square wave
        # type=2: sawtooth wave
        # type=3: triangle wave
        # type=4: whitenoise wave
        # type=5: silence wave
        
        nbsamples *= self._nchannels
        nbsamples = int(nbsamples)
        vol =1
        lst = []
        # period for the sinus function
        t = 2*pi*freq/(self._rate*self._nchannels)
        # len1 =0.001 # length of samples in miliseconds
        # nbsamples = int(self._rate*self._nchannels*len1)
        # sine wave
        if type == 0:
            for i in range(nbsamples):
                y = int(vol*self._maxamp*sin(t*i))
                lst.append(y)
        # square wave
        elif type == 1:
            # get the sign of the angle for square wave with cmp function
            for i in range(nbsamples):
                y = int(self._maxamp*vol * cmp(sin(t*i), 0))
                lst.append(y)
        # sawtooth wave
        elif type == 2:
            for i in range(nbsamples):
                y = int(self._maxamp*(t*i % 1))
                # second way
                # y = int(self._maxamp*(t* - math.floor(t*i)))
                lst.append(y)
        # triangle wave
        elif type == 3:
            for i in range(nbsamples):
                y = int(self._maxamp * self._triangle_sine(t*i))
                lst.append(y)
        # whitenoise wave
        elif type == 4:
            for i in range(nbsamples):
                # choose start at 10000 to best amplitude
                y = int(vol*random.randrange(10000, self._maxamp)) 
                lst.append(y)
        # silence wave
        elif type == 5:
            lst = [0] * nbsamples
        else:
            lst = [00]
    
        self._wavbuf_lst = lst
    
        return self._wavbuf_lst

    #-----------------------------------------


                       
#========================================

class AudiStream(AudiSoundBase):
    """ stream manager """
    def __init__(self, filename=""):
        super(AudiStream, self).__init__()
        if filename:
            self.load(filename)
    
    #-----------------------------------------

    def load(self, filename):
        # load stream
        self._filename = filename

        try:
            self._wavfile = wave.open(filename, 'rb')
        except IOError:
            print("Error: unable to load file in memory")
            return
        
        # sampwidth: number of byte per samples: in bytes
        # nchannels: number of channels
        # rate: sampling rate per second
        # nframes: total number of samples for audio data in bytes
        # framesize = nchannels * sampwidth = 4 bytes (2*2)
        # for 2 channels, 16 bits
        
        self._nchannels = self._wavfile.getnchannels()
        self._sampwidth = self._wavfile.getsampwidth()
        self._rate = self._wavfile.getframerate()
        self._nframes = self._wavfile.getnframes()

        # duration = nframes / rate in second
        # length in second
        # length = (self._nchannels * self._sampwidth * self.nframes) / 
        # (self._nchannels * self._sampwidth * self._rate)
        # equiv': 
        self._length = self._nframes # in frames


        return self._wavfile
    
    #-----------------------------------------

    def close(self):
        # close stream file
        if self._wavfile:
            try:
                self._wavfile.close()
            except IOError:
                print("Error: unable to close file: %s" % self._filename)
            
    #-----------------------------------------


    def read_data(self, nb_frames):
        """ read nb_frames frames for audistream object
        """
        # frames = 4 bytes, so 2 signed short
        # for 2 channels, 16 bits, 44100 rate
        # we want to get a list of short to manage samples not frames
        wav_data = None
        wav_data1 = None
        nb_samples = nb_frames * self._nchannels
        # so nb_samples is in samples for 2 channels
        # struct.unpack return a tuple, must be converted in list
        start_pos = self.get_start_position(0) # in frames
        end_pos = self.get_end_position(0) # in frames
        if self._curpos + nb_frames <= end_pos: # its normal, nb_frames not too large
            try:
                wav_data = self._wavfile.readframes(nb_frames)
            except wave.error:
                print("Wave_error: unable to read wave file: %s" % self._filename)
                return
            
            """
            try:
                self._wavbuf_lst = list(struct.unpack('<'+nb_samples*'h', wav_data))
            except struct.error:
                print("Struct_error: unable to unpack data from wave file %s" % self._filename)
                debug("struct_error: voici curpos: %d" % self._wavfile.tell())
                self._wavbuf_lst = []
            """
            
            # self._buf_arr = np.array([], dtype='int16')
            self._buf_arr = np.fromstring(wav_data, dtype='int16')
            # debug("je passe ici: %s" % self._buf_arr.dtype)
            # return
            
            self._curpos += nb_frames
        else: # whether nb_frames is too large
            try:
                wav_data = self._wavfile.readframes(nb_frames)
            except wave.error:
                print("Wave_error: unable to read wave file: %s" % self._filename)
                return
            nb_bytes1 = len(wav_data)
            # convert bytes to frames
            nb_frames1 = self.unit_to_frames(nb_bytes1, 3)
            # calculate the rest in frames
            nb_frames2 = nb_frames - nb_frames1
            # debug("voici len_frames1 in frames %d" % len_frames1)
            # nb_samples1 is in samples for struct.unpack
            nb_samples1 = nb_frames1 * self._nchannels
            if self.is_looping(): # is looping
                # todo: test with loop_manager function

                # debug("is looping")
                # self._wavbuf_lst = buf_lst1 + buf_lst2
                self.set_position(start_pos)
                wav_data1 = self._wavfile.readframes(nb_frames2)
                wav_data += wav_data1
                self._buf_arr = np.fromstring(wav_data, dtype='int16')
                self._curpos += nb_frames2
            else: # not looping
                # add zeros at end to complete samples length
                """
                try:
                    buf_lst = list(struct.unpack('<'+nb_samples1*'h', wav_data))
                except struct.error:
                    print("Struct_error: unable to unpack data from wave file %s" % self._filename)
                    return
                """
                # self._buf_arr = np.zeros(1024, dtype='int16')
                self._buf_arr = np.fromstring(wav_data, dtype='int16')
                # fill the rest of the array with zeros 
                self._buf_arr.resize(nb_samples)
                # debug("voici len_buf %d, nb_zeros: %d, et total buf: %d" %(len(buf_lst), nb_zeros, len(self._wavbuf_lst)))
                self._curpos += nb_frames1

        # return self._wavbuf_lst
        return self._buf_arr

    #-----------------------------------------

    def get_position(self, unit=0):
        """ return stream position  from audistream object
        position is in frames, seconds, samples or bytes
        """
        # the tell function return value in frames
        # self._curpos  = self._wavfile.tell() # in frames
        # val = self._curpos
        # convert curpos to unit
        val = self.frames_to_unit(self._curpos, unit)
       
        # debug("je suis dans AudiStream, get_position : %f" % val)
        
        return val

    #-----------------------------------------


    def set_position(self, pos, unit=0):
        """ set stream position from audistream object
        """
        # set_position function take frames number

        # unit=0: for frames samples
        # unit=1: for seconds
        # unit=2: for bytes
        pos = self.unit_to_frames(pos, unit)
        if pos <0:
            pos =0
        elif pos >= self._length: # length in frames
            pos = self._length
        try:
            self._wavfile.setpos(pos)
        except wave.Error:
            print("Error: unable to set position in wave file: %s" % self._filename)
            return 
        
        self._curpos = pos
    
    #-----------------------------------------


#========================================


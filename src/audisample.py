#! /usr/bin/python3
"""
    File: audisample.py
    Module for Sample mananment
    Date: Sun, 17/07/2022
    Author: Coolbrother
"""

import struct
import wave
import numpy as np
from audibase import AudiSoundBase

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



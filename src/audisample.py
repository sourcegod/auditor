#! /usr/bin/python3
"""
    File: audisample.py
    Module for Sample mananment
    Date: Sun, 17/07/2022
    Author: Coolbrother
"""
import copy
import numpy as np
from audibase import AudiSoundBase
import soundfile as sf

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

class SoundBuffer(object):
    """ wave data manager """
    def __init__(self, data=None):
        """
        init function
        from SoundBuffer object
        """
        # data is a numpy array
        self._data = data
        self._len =0
        if self._data.size:
            self._len = len(self._data)
        self._curpos =0
        self._channels =1
        self._rate = 44100
        self._bits = 16
        self._sampwidth =1
        self.frames = self._len

    #------------------------------------------------------------------------------
    
    def get_data(self):
        """
        returns numpy data
        from SoundBuffer object
        """

        return self._data

    #------------------------------------------------------------------------------

    def set_data(self, data):
        """
        init data
        from SoundBuffer object
        """

        # data is an nmpy array, with one dimension per channel
        self._data = data
        self._len = len(self._data)
        self.frames = self._len


    #------------------------------------------------------------------------------

    def set_params(self, channels=1, rate=44100, bits=16):
        """
        set params for data buffer
        from SoundBuffer object
        """

        self._channels = channels
        self._rate = rate
        self._bits = bits
        self._sampwidth = (self._bits * self._channels) / 8

    #------------------------------------------------------------------------------


    def read(self, frames=-1, start=-1, stop=0):
        """
        reading numpy array in frames
        returns nb_frames from data buffer
        from SoundBuffer object
        """

        data = None
        if start <0: start = self._curpos
        if frames >= 0: stop = start + frames
        
        try:
            data = self._data[start:stop]
        except IndexError:
            return 
        self._curpos = stop

        return data

    #------------------------------------------------------------------------------

    def tell(self):
        """
        returns curpos in frames
        from SoundBuffer object
        """

        return self._curpos

    #------------------------------------------------------------------------------

    def seek(self, pos):
        """
        search pos in frames
        from SoundBuffer object
        """

        # _len is data len
        if not self._len: return -1
        if pos <0: pos =0
        elif pos >= self._len: pos = self._len -1
        self._curpos = pos
        
        return pos

    #------------------------------------------------------------------------------


#========================================


class AudiSample(AudiSoundBase): # object is necessary for property function
    """ sample manager """
    def __init__(self, mode=0, filename="", bits=16, rate=44100, channels=2, nbsamples=1):
        super(AudiSample, self).__init__()
        self.sound_type =0 # type sample
        self._wav_data = None
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
        """ 
        load entire sound into memory with pysoundfile module 
        from audisample object
        """

        wav_data = None
        sf_info = None

        try: 
            sf_info = sf.info(filename)
        except RuntimeError as err:
            print("Error info, unable to open file: ", err)
            return

        # sampwidth: number of byte per samples: in bytes
        # nchannels: number of channels
        # rate: sampling rate per second
        # nframes: total number of samples for audio data in bytes
        # framesize = nchannels * sampwidth = 4 bytes (2*2)
        # for 2 channels, 16 bits
        
        if sf_info:
            self._filename = filename
            self._nchannels = sf_info.channels
            # subtype is a string like: "PCM_16"
            # so we need to extract the number
            try:
                bits = int(sf_info.subtype.split('_')[1])
            except ValueError:
                bits =0
            self._bits = bits
            self._sampwidth = (bits * self._nchannels) / 8
            self._rate = sf_info.samplerate
            self._nframes = sf_info.frames
            self._length = self._nframes # in frames


        # duration = nframes / rate in second
        # length in second
        # length = (self._nchannels * self._sampwidth * self.nframes) / 
        # (self._nchannels * self._sampwidth * self._rate)
        # equiv': self._length = self._nframes / float(self._rate)
        try:
            (wav_data, rate) = sf.read(filename, dtype='float32')
        except RuntimeError as err:
            print(f"Error: unable to load in memory wave file: {filename}")
            return
  
        self._wav_data = wav_data.flatten()

        return self
    
    #-----------------------------------------


    def close(self):
        """ 
        close sample 
        from audisample object
        """
        pass

    #-----------------------------------------

    def init_sample(self, bits=16, rate=44100, channels=2, nbsamples=44100):
        """
        create new sound sample in memory
        sampwidth: number of byte per samples: in bytes
        nchannels: number of channels
        rate: sampling rate per second
        nframes: total number of samples for audio data in bytes
        from AudiSample object
        """

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
        # all in frames
        if nbsamples == 0:
            self._wav_data = np.array([], dtype='float32')
        else:
            nb_zeros = nbsamples * channels
            self._wav_data = np.zeros(nb_zeros, dtype='float32')
        self._length = self._nframes # * self._nchannels
        
        return self

    #-----------------------------------------
    
    def update_sample(self):
        """
        update sample parameters
        from AudiSample object
        """
        
        # Todo: more parameters
        if self._wav_data is None: 
            self._nframes =0
        else:
            self._nframes = int(len(self._wav_data) / self._nchannels)
        
        self._length = self._nframes

    #-----------------------------------------

    def read_data(self, nb_frames):
        """
        Temporary function, just to backup old version based on samples instead frames
        from AudiSample object
        """
        buf_arr = None

        nb_samples = nb_frames * self._nchannels # convert nb_frames in samples
        # curpos in frames
        pos = int(self._curpos * self._nchannels) # in samples
        start_pos = self.get_start_position(2) # * self._nchannels # in samples
        end_pos = self.get_end_position(2) # in samples
        # debug("voici pos: %d, start_pos %d, end_pos %d" %(pos, start_pos, end_pos))
        # return
        if pos < end_pos:
            if pos + nb_samples < end_pos:
                step = pos + nb_samples # in samples
                try:
                    buf_arr = self._wav_data[pos:step]
                except IndexError:
                    # debug("Error in read_data from sample object, voici step: %d" % step)
                    print("indexError: unable to index in read_data from sample object")
                
                self._curpos = int(step / self._nchannels) # in frames

            else: # nb_frames is too large
                if self.is_looping():
                    # debug("voici loopmode: %d, loopcount: %d" %(self._loop_mode, self._loop_count))
                    len1 = len(self._wav_data[pos:end_pos])
                    len2 = nb_samples - len1
                    buf_arr = np.append(self._wav_data[pos:end_pos], 
                            self._wav_data[start_pos:start_pos+len2])
                    self._curpos = start_pos # in frames
                else: # no looping
                    # add zeros at the end to adjust length sample
                    
                    """
                    # now, no need to be resized because its managing by the mixer for performance reason
                    len1 = len(self._wav_data[pos:end_pos])
                    # must be copied before resizing
                    buf_arr = np.copy(self._wav_data[pos:end_pos])
                    buf_arr.resize(nb_samples)
                    """

                    buf_arr = np.copy(self._wav_data[pos:end_pos])
                    self._curpos = end_pos -1 # in frames
                    # debug("voici pos: %d, end_pos: %d, len1 %d, et len_buf %d" %(pos, end_pos, len1, len(buf_lst)))
        else: # whether pos > to sample length
            # debug("je passe dans read_data de sample : %d bytes" % len(buf_lst)) 
            pass
        if self.is_mono():
            # repeat each value to convert mono to stereo
            return np.repeat(buf_arr, 2)
        
        # explicit copy, to not modify the original data 
        return np.copy(buf_arr)

    #-----------------------------------------

    def read_frames(self, nb_frames):
        """ 
        read nb_frames frames in file in memory 
        like read_data function but not resize the array that will be returned
        from audisample object
        """
        # frames = 4 bytes, 2 signed short
        # for 2 channels, 16 bits, 44100 rate
        buf_lst = []
        buf_arr = np.arr([], dtype='int16')
        nb_samples = nb_frames * self._nchannels # convert nb_frames in samples
        # curpos in frames
        pos = int(self._curpos * self._nchannels) # in samples
        start_pos = self.get_start_position(2) # * self._nchannels # in samples
        end_pos = self.get_end_position(2) # in samples
        # debug("voici pos: %d, start_pos %d, end_pos %d" %(pos, start_pos, end_pos))
        # return
        if pos < end_pos:
            if pos + nb_samples < end_pos:
                step = pos + nb_samples # in samples
                try:
                    # buf_lst = self._wavbuf_lst[pos:step]
                    buf_arr = self._wav_data[pos:step]
                except IndexError:
                    # debug("Error in read_data from sample object, voici step: %d" % step)
                    print("index_rror: unable to index in read_data from sample object")
                
                self._curpos = int(step / self._nchannels) # in frames
            else: # nb_frames is too large
                if self.is_looping():
                    # debug("voici loopmode: %d, loopcount: %d" %(self._loop_mode, self._loop_count))
                    len1 = len(self._wav_data[pos:end_pos])
                    len2 = nb_samples - len1
                    buf_arr = np.append(self._wav_data[pos:end_pos], 
                            self._wav_data[start_pos:start_pos+len2])
                    self._curpos = start_pos # in frames
                else: # no looping
                    # add zeros at the end to adjust length sample
                    len1 = len(self._wav_data[pos:end_pos])
                    buf_arr = self._wav_data[pos:end_pos]
                    # no resizing if nb_frames is too large
                    self._curpos = end_pos -1 # in frames
                    # debug("voici pos: %d, end_pos: %d, len1 %d, et len_buf %d" %(pos, end_pos, len1, len(buf_lst)))
        else: # whether pos > to sample length
            # debug("je passe dans read_data de sample : %d bytes" % len(buf_lst)) 
            pass

       
        # debug("voici buf_arr: %s" %(self._buf_arr))
        return buf_arr
    
    #-----------------------------------------
    
    def get_position(self, unit=0):
        """ 
        returns position 
        from audisample object
        """

        # position in frames, second, samples, or bytes
        # unit=0: in frames
        # convert curpos to unit
        # curpos in frames
        # debug("voici curpos in frames : %d" %(self._curpos))
        # not necessary
        # no convert float to int to be precise in position
           
        return self._curpos

    #-----------------------------------------

    def set_position(self, pos, unit=0):
        """ 
        set sound position 
        from audisample object
        """
        
        # set_position function take frames samples number
        # frames, seconds, samples or bytes
        # unit=0: for frames samples
        # unit=1: for seconds
        # unit=2: for bytes
        # convert pos to frames bellong unit
        # debug("dans sample set_pos: pos: %.2f" %(pos))
        # not necessary and prenvent to convert float to int
        # pos = self.unit_to_frames(pos, unit)
        if pos <0:
            pos =0
        elif pos >= self._length: # length in frames
            pos = self._length
            # debug("pos is greater than length: %d" %(self._length))
        
        self._curpos = pos # in frames

    #-----------------------------------------
   
    def reverse(self):
        """
        reverse sound
        from AudiSample object
        """
        
        if self._nframes:
            # change the strides of numpy array
            # reverse numpy data
            self._wav_data = self._wav_data[::-1]
        
    #-----------------------------------------
    def get_data(self, nb_frames=0):
        """
        returns numpy data
        from AudiSample object
        """

        return self._wav_data

    #------------------------------------------------------------------------------

 
    def get_raw_list(self):
        """
        returns the sound raw data
        from AudiSample object
        """

        return self._wav_data

    #-----------------------------------------

    def init_raw_list(self, arr):
        """
        init raw list
        from AudiSample object
        """

        # self._wavbuf_lst = lst
        self._wav_data = arr
        self.update_sample()

    #-----------------------------------------

    def set_raw_list(self, start, nbsamples):
        """
        set the sound raw data
        from AudiSample object
        """

        # wavbuf_lst is in short one channel per value
        start *= self._nchannels
        nbsamples *= self._nchannels
        length = start + nbsamples 
        if self._wav_data is None: return
        try:
            self._wav_data = self._wav_data[start:length]
        except IndexError:
            return self._wav_data
        
        self.update_sample()        
        
        return self._wav_data
    
    #-----------------------------------------

    def set_raw_range(self, start, end):
        """
        set the range raw data without calculate length of data to set
        from AudiSample object
        """

        # wavbuf_lst is in short one channel per value
        start *= self._nchannels
        end *= self._nchannels
        try:
            self._wav_data = self._wav_data[start:end]
        except IndexError:
            return None
        self.update_sample()
        
        return self._wav_data
    
    #-----------------------------------------

    def mix_raw_list(self, start1, len1, lst1, mixstart=0):
        """
        merge list1 to the current sound list
        from AudiSample object
        """

        # Todo: convert it in numpy array
        # lst1 must be <= lwavbuf_lst
        # wavbuf_lst is in short one channel per value
        start1 *= self._nchannels
        len1 *= self._nchannels
        mixstart *= self._nchannels
        try:
            for i in range(start1, len1):
                # avoid sound clipping
                sm = self.wavbuf_lst[i+mixstart] + lst1[i]
                data = min(max(sm, -32767), 32767)
                self._wavbuf_lst[i+mixstart] = data
        except IndexError:
            pass
        self.update_sample()        
        
        return self._wav_data
    
    #-----------------------------------------

    def change_raw_list(self, start1, len1, val=0):
        """
        change the current sound list
        from AudiSample object
        """

        # wavbuf_lst is in short one channel per value
        # numpy slice assign the value to all the range
        start1 *= self._nchannels
        len1 *= self._nchannels
        try:
            self._wav_data[start1:len1] = val
        except IndexError:
            pass
        self.update_sample()        
        
        return self._wav_data
    
    #-----------------------------------------

    def new_sample(self, bits=16, rate=44100, channels=2, nbsamples=44100):
        """
        create new sample
        from AudiSample object
        """

        mode =1
        if self.sound_type == 0:
            samp = AudiSample(mode, "", bits, rate, channels, nbsamples)
        elif self.sound_type == 3:
            samp = AudiLoopSample(mode, "", bits, rate, channels, nbsamples)

        return samp

    #-----------------------------------------

    def copy_sample(self, start=0, nbsamples=0):
        """
        deep copy sample
        from AudiSample object
        """
        
        snd = copy.deepcopy(self)
        if nbsamples >0:
            snd.set_raw_list(start, nbsamples)
        
        snd.update_sample()
        
        return snd
    
    #-----------------------------------------

    def cut_sample(self, from1=0, nbsamples=0):
        """
        cut sample, 
        returns the rest of sample after cutting
        from AudiSample object
        """

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
        """
        cut each part outside the selection
        returns the rest of sample
        from AudiSample object
        """

        len1 = self.get_length()
        if start <0:
            start =0
        if nbsamples <= 0 or nbsamples > len1:
            nbsamples = len1
        
        """
        snd = copy.deepcopy(self)
        snd.set_raw_list(start, nbsamples)
        """
        
        snd = self.copy_sample(start, nbsamples)

        return snd
    
    #-----------------------------------------

    def insert_sample(self, samp, start, nbsamples, ins_start):
        """ 
        insert a new sample to the old sample
        ins_start: the point to insert the new sample
        from AudiSample object
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
            part1 = snd_raw[0:ins_start]
            part2 = samp.get_raw_list()
            if ins_start < len1:
                part3 = snd_raw[ins_start:]
            else:
                part3 = np.array([], dtype='int16')
        except IndexError:
            return snd
        
        arr = np.concatenate(part1, part2, part3)
        snd.init_raw_list(arr)
        
        return snd
    
    #-----------------------------------------

    def erase_sample(self, start=0, len1=-1):
        """
        erase sample, not delete
        from AudiSample object
        """

        if len1 == -1:
            len1 = self.get_length() 

        snd = self.copy_sample(0, self.get_length())
        # fill the rawlist with val
        snd.change_raw_list(start, len1, val=0)
        
        return snd
    
    #-----------------------------------------
        
    def merge_sample(self, samp2, start2, len2, mixstart=0):
        """
        mix two samples
        from AudiSample object
        """

        # Todo: pass to the numpy array
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
        
        samp3.update_sample()
        return samp3
    
    #-----------------------------------------

    def mix_sample(self, *samp_lst):
        """
        mix sample list
        from AudiSample object
        """
        
        # all sounds must have same length
        acc =0
        sum_lst = []
        snd = self.copy_sample()
        
        """
        samp_len = samp_lst[0].get_length() # in frames
        for i in range(samp_len):
            acc =0
            for samp in samp_lst:
                lst = samp.get_raw_list()
                acc += lst[i]
            sum_lst.append(acc)
       """
       
        arr = np.sum(samp_lst, axis=0)
        # Todo: limit sum_lst values against saturation
        snd.init_raw_list(sum_lst)
        
        return snd
    
    #-----------------------------------------

    def concat_sample(self, *samp_lst):
        """
        concat samp1 to samp2 or more samples
        from AudiSample object
        """

        # it's a adding for samp2 at the end of samp1
        new_snd = None
        
        if samp_lst:
            new_snd = self.copy_sample(nbsamples=1)
            new_lst = new_snd.get_raw_list()
            for snd in samp_lst:
                data_lst = snd.get_raw_list()
                new_lst = np.append(new_lst, data_lst)
            

        new_snd.init_raw_list(new_lst)
        # update sample parameters
        # new_snd.update_sample()

        return new_snd

    #-----------------------------------------
        
    def delete_sample(self):
        """
        delete sample
        from AudiSample object
        """

        arr = np.array([], dtype='int16')
        self.init_raw_list(arr)
        # self.active =0
        # self.update_sample()
    
    #-----------------------------------------

    def tone(self, type=0, freq=440, nbsamp=44100):
        """
        create tone wave with nbsamp samples
        type=0: sine wave
        type=1: square wave
        type=2: sawtooth wave
        type=3: triangle wave
        type=4: whitenoise wave
        type=5: silence wave
        from AudiSample object
        """

        self._gen_wave(type, freq, nbsamp)

        return self

    #-----------------------------------------

    def _triangle_sine(self, n):
        """
        return triangular sine of n
        from AudiSample object
        """

        x = n % 1
        if x <= .25:
            return x
        if x <= .75:
            return .5 - x

        return x -1
    
    #-----------------------------------------

    def _gen_wave(self, type=0, freq=440, nbsamples=44100):
        """
        generate nbsamples sine raw data
        create tone wave with nbsamp samples
        type=0: sine wave
        type=1: square wave
        type=2: sawtooth wave
        type=3: triangle wave
        type=4: whitenoise wave
        type=5: silence wave
        from AudiSample object
        """

        # print(f"freq: {freq}, channels: {self._nchannels}")
        nbsamples *= self._nchannels
        nbsamples = int(nbsamples)
        vol =1
        lst = []
        # period for the sinus function
        t = 2 * np.pi*freq/(self._rate*self._nchannels)
        # len1 =0.001 # length of samples in miliseconds
        # nbsamples = int(self._rate*self._nchannels*len1)
        # sine wave
        incr = (2 * np.pi * freq) / (self._rate * self._nchannels)
        if type == 0:
            for i in range(nbsamples):
                y = vol*self._maxamp*np.sin(t*i)
                lst.append(y)
            
            """
            # TODO: refactorize it in numpy array way
            arr = np.arange(nbsamples)
            self._wav_data = np.sin(incr * arr)
            """

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
    
        # self._wavbuf_lst = lst
        self._wav_data = np.array(lst, dtype='float32')
        
        # update sound params
        # like nframes, and length sound
        nb_frames = int(nbsamples / self._nchannels)
        self.set_params(self._nchannels, self._sampwidth, self._rate, nb_frames)
    
        return self._wav_data

    #-----------------------------------------

#========================================

if __name__ == "__main__":
    fname = ""
    snd = AudiSample(mode=0)
    snd = snd.load(fname)
    if not snd: print("Sound not found")
    else: print(f"File is loaded: {fname}")
    input("It's OK...")


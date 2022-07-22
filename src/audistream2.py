#! /usr/bin/python3
"""
    File: audistream2.py
    Module for audio stream managment
    Date: Fri, 22/07/2022
    Author: Coolbrother
"""
import soundfile as sf
import numpy as np
from audibase import AudiSoundBase



class AudiStream(AudiSoundBase):
    """ stream manager """
    def __init__(self, filename=""):
        super(AudiStream, self).__init__()
        if filename:
            self.load(filename)
    
    #-----------------------------------------

    def load(self, filename):
        """
        load stream with pysoundfile
        # load stream
        from AudiStream object
        """

        """
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
        """

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
            self._sampwidth =1
            self._rate = sf_info.samplerate
            self._nframes = sf_info.frames
            self._length = self._nframes # in frames


        # duration = nframes / rate in second
        # length in second
        # length = (self._nchannels * self._sampwidth * self.nframes) / 
        # (self._nchannels * self._sampwidth * self._rate)
        # equiv': self._length = self._nframes / float(self._rate)
        try:
            self._wavfile = sf.SoundFile(filename)
        except RuntimeError as err:
            print(f"Error: unable to create stream object with filename: {filename}")
            return
  
        return self
 
    
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
        """ 
        read nb_frames frames with pysoundfile
        from audistream object
        """

        # frames = 4 bytes, so 2 signed short
        # for 2 channels, 16 bits, 44100 rate
        # we want to get a list of short to manage samples not frames
        wav_data = None
        wav_data1 = None
        nb_samples = nb_frames * self._nchannels # convert nb_frames in samples
        start_pos = self.get_start_position(0) # in frames
        end_pos = self.get_end_position(0) # in frames
        try:
            wav_data = self._wavfile.read(frames=nb_frames)
        except RuntimeError as err:
            print(f"Error: unable to read stream file: {self._filename}")
            return

        if self._curpos + nb_frames <= end_pos: # its normal, nb_frames not too large
            # debug("je passe ici: %s" % self._buf_arr.dtype)
            self._curpos += nb_frames
        else: # whether nb_frames is too large
            nb_frames1 = len(wav_data)
            # calculate the rest in frames
            nb_frames2 = nb_frames - nb_frames1
            # debug("voici len_frames1 in frames %d" % len_frames1)
            if self.is_looping(): # is looping
                # todo: test with loop_manager function
                # debug("is looping")
                self.set_position(start_pos)
                try:
                    wav_data1 = self._wavfile.read(frames=nb_frames2)
                except RuntimeError as err:
                    print(f"Error: unable to read stream file in looping mode: {self._filename}")
                    return

                wav_data = np.append(wav_data, wav_data1)
                self._curpos += nb_frames2
            else: # not looping
                # fill the rest of the array with zeros 
                # we can resize in place cause stream is renewed each time
                wav_data.resize(nb_samples)
                # self._buf_arr.resize(nb_samples)
                # debug("voici len_buf %d, nb_zeros: %d, et total buf: %d" %(len(buf_lst), nb_zeros, len(self._wavbuf_lst)))
                self._curpos += nb_frames1

        # convert buf_arr in one dimensional array
        self._buf_arr = wav_data.flatten()
        return self._buf_arr

    #-----------------------------------------

    def get_position(self, unit=0):
        """ 
        returns stream position for pysoundfile
        from audistream object
        """

        # position is in frames, seconds, samples or bytes
        # the tell function return value in frames
        # self._curpos  = self._wavfile.tell() # in frames
        # val = self._curpos
        # convert curpos to unit
        val = self.frames_to_unit(self._curpos, unit)
       
        # debug("je suis dans AudiStream, get_position : %f" % val)
        
        return val

    #-----------------------------------------


    def set_position(self, pos, unit=0):
        """ 
        set stream position for pysoundfile
        from audistream object
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
            self._wavfile.seek(pos)
        except RuntimeError as err:
            print(f"Error: unable to set position in stream file: {self._filename}")
            return 
        
        self._curpos = pos
    
    #-----------------------------------------


#========================================

if __name__ == "__main__":
    fname = ""
    snd = AudiStream()
    snd = snd.load(fname)
    if not snd: print("Sound not found")
    else: print(f"File is loaded: {fname}")
    input("It's OK...")


#! /usr/bin/python3
"""
    File: audistream.py
    Module for audio stream managment
    Date: Sun, 17/07/2022
    Author: Coolbrother
"""
import wave
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

        # convert in float for more manip
        self._buf_arr = self._buf_arr.astype(np.float32, order='C') / 32768.0
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


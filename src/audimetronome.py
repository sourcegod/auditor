#! /usr/bin/python3
"""
   File audimetronome.py
   Test on Metronome with fill buffer 
    Author: Coolbrother
"""

import numpy as np
import audisample as ausam


class TableObj(object):
    """ 
    Generic object containing data, 
    can be useful for a metronome or rolling data object
    """
    def __init__(self, arr, start=0, _len=1):
        self._arr = arr # arr initial array
        self._start = start
        self._len = _len
        self._pos = self._start
        self._count =3
    
    #----------------------------------------

    def __iter__(self):
        return self

    #----------------------------------------

    def __next__(self):
        return self.get_data(self._count)

    #----------------------------------------

    def get_data(self, count):
        step = self._pos + count
        curpos = self._pos
        print(f"Voici step {step}, and _len: {self._len}")
        if self._pos >= self._len: return None
        elif step >= self._len:
            count = self._len - self._pos
            step = self._pos + count
            self._pos = self._len
        elif step < self._len:
            self._pos += count
        # if len(self._arr[self._pos:step]) == 0: return None
            
        print(f"Returns curpos: {curpos}, step {step}, count: {count}, and _len: {self._len}")
        return self._arr[curpos:step]
        
    #----------------------------------------

    def reset(self):
        self._pos = self._start

    #----------------------------------------

#========================================

class AudiMetronome(ausam.AudiSample):
    """ Generating click with static numpy array and using fill buffer function """
    def __init__(self):
        super(AudiMetronome, self).__init__()
        self._buf = []
        self._curpos =0
        self._index =0
        _len = 7 # len of block size
        # can use get_sine_table function for generating array
        arr1 = np.arange(_len) # tone 1
        arr2 = np.zeros((_len, ), dtype='int16') # silence
        arr3 = np.arange(_len) # tone 2
        part1 = TableObj(arr1, 0, _len)
        # blank length can be different from tone 1 or 2
        part2 = TableObj(arr2, 0, _len)
        part3 = TableObj(arr3, 0, _len)
        # part4 = TableObj(arr2.copy(), 0, _len)
        part4 = part2

        part5 = part3
        part6 = part2
        part7 = part3
        part8 = part2
        
        self._objlist = [part1, part2, part3,
                part4, part5, part6,

                part7, part8
                ]
        self._lenobj = len(self._objlist)

    #----------------------------------------

    def gen_click(self, bpm=100):
        """
        create new tone sound in memory
        from AudiMetronome object
        """

        """
        snd = ausam.AudiSample(mode=1) # empty sample
        rate = 44100
        nbsamp = int(lensec * rate)
        snd = snd.tone(0, freq, nbsamp)
        """

        track_click = None
        count_time =0
        samp_rate =44100
        tempo_time = 60 / float(bpm)  # in seconds
        tick_time =0.060 # in second
        sil_time = tempo_time - tick_time # bad idea: to substract 0.001 # to be precise
        nbsamp_tick = int(samp_rate * tick_time)
        nbsamp_sil = int(samp_rate * sil_time)

        samp = ausam.AudiSample(mode=1) # empty sample with nbsamples=1
        samp.sound_type =0
        
        samp1 = samp.new_sample(nbsamples=1)
        samp1 = samp1.tone(0, 880, nbsamp_tick) # generate sine wave with 880 Hz

        samp2 = samp.new_sample(nbsamples=nbsamp_sil)
        
        samp3 = samp.new_sample(nbsamples=1)
        samp3 = samp3.tone(0, 440, nbsamp_tick) # generate sine wave with 440 Hz
       
        samp_lst = [samp1, samp2, samp3, samp2,\
                samp3, samp2, samp3, samp2
                ]
        snd = samp.concat_sample(*samp_lst)

            

        return snd

    #-----------------------------------------


        return snd
    
    #-----------------------------------------

    def get_sine_table(self, freq, rate, _len):
        """ returns array of sine wave """
        incr = (2 * np.pi * freq) / rate
        arr = np.arange(_len)
        return np.sin(incr * arr)
        

    #-------------------------------------------
     
    def _next_obj(self):
        
        self._index = self._index +1 % self._lenobj
        
    #----------------------------------------

    def fill_buffer(self, count):
        self._buf = []
        rest_count = count
        print(f"In fill_buffer, count: {count}, rest_count: {rest_count}")
        while 1:
            print("Top loop")
            print(f"index: {self._index}, rest_count: {rest_count}, lenbuf: {len(self._buf)}")
            cur_obj = self._objlist[self._index]
            data = cur_obj.get_data(rest_count)
            if data is None and len(self._buf) == 0 and self._index == self._lenobj -1:
                break
            if data is None:
                print(f"data is None at index: {self._index}")
                cur_obj.reset()
                self._next_obj()
                continue
            else: 
                print(f"Before extend\n index: {self._index}, rest_count: {rest_count}, lendata: {len(data)}, lenbuf: {len(self._buf)}")
                self._buf.extend(data)
                rest_count = rest_count - len(data)
                print(f"After extend\n index: {self._index}, rest_count: {rest_count}, lendata: {len(data)}, lenbuf: {len(self._buf)}")
            
            if len(self._buf) >= count:
                break
            else:
                continue
    
        print(f"Len final buffer: {len(self._buf)}")
        return self._buf

    #----------------------------------------

#========================================



def main():
    obj = AudiMetronome()
    
    for i in range(4):
    # if 1:
        buf = obj.fill_buffer(5)
        print("In Main")
        print(f"len buffer: {len(buf)}")
        print(f"{i}: {buf}")
        print()


#----------------------------------------

if __name__ == "__main__":
    main()
    input("Press Enter Key...")

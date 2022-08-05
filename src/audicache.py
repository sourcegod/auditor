#! /usr/bin/env python
"""
    File: audicache.py
    Audio Cache Manager
    Date: Sun, 31/07/2022
    Author: Coolbrother
"""
import numpy as np

class BufferObj(object):
    """ container for cache buffer """
    def __init__(self):
        self.pos =0
        self.buf = None

    #-----------------------------------------

#========================================


class AudiCache(object):
    """ Audio Cache Manager """
    def __init__(self, mixer=None):
        self._mixer = mixer
        self._nchannels =1
        self._buf_size =1
        self.cache_data = None
        self._in_type = np.float32
        self._len_buf =0
        self.is_caching = False
        self.len_cache =0
        self.cache_data = []
        self.nb_buf =0 # number of buffer by each sound
        self.buf_pos =0
        self.row =0
        self.nb_frames =0

    #-----------------------------------------
    
    def init_cache(self, nb_chan=1):
        """
        initialize the data cache
        from AudiCache object
        """

        if not self._mixer: return
        self._nchannels = self._mixer._nchannels
        self._buf_size = self._mixer._buf_size
        self._in_type = self._mixer._in_type
        self._len_buf = self._mixer._len_buf
        # take too place in memory
        # self.cache_data = np.zeros((nb_chan, self._len_buf), dtype=self._in_type)
        self.cache_data = [] # [0] * nb_chan
        # self.len_cache = len(self.cache_data)

    #-----------------------------------------
    
    def preload(self, nb_chan=16):
        """
        preload data
        from AudiCache object
        """
        
        if not self._mixer: return False
        chan_lst = self._mixer.get_channels()
        nb_chan  = len(chan_lst)
        self.nb_buf =4 # number of buffer for each sound to preload
        nb_cache = nb_chan
        self.init_cache(nb_cache)
        self.nb_frames = self.nb_buf * self._buf_size
        # if not self.cache_data: return False
        self._view_data = []
        if not chan_lst:
            print("No data is caching...")
            return False
        try:
            for (i, chan) in enumerate(chan_lst):
                if i < nb_cache:
                    snd = self._mixer.get_sound_by_id(i)
                    if not snd: continue
                    else:
                        buf1 = snd.read_data(self.nb_frames)
                        nb_samples = self.nb_buf * self._len_buf
                        if len(buf1) < nb_samples:
                            buf1.resize(nb_samples)
                        self.cache_data.append(buf1)
                        buf = self.cache_data[-1]
                        bufobj = BufferObj()
                        bufobj.buf = buf.reshape(-1, self._len_buf)
                        self._view_data.append(bufobj)

                        self.is_caching = True
                        # print(f"find caching sound on channel {i}")
                else: break
            self.len_cache = len(self.cache_data)
            # print(f"voici shape view_data: {self._view_data[0].shape}")
            # print("view0 is cache_data 0? ", np.shares_memory(self._view_data[0], self.cache_data[0]))
        except IndexError:
            self.is_caching = False
            return False
        
        if self.is_caching:
            print("Preloading cache...")
        
        return True

    #-----------------------------------------

    def get_data(self, num=0):
        """
        returns simple raw data without Sound object
        from AudiCache object
        """

        data = None
        try:
            # print(f"voici curpos {self._curpos}, et len_data: {len(self._raw_data)}")
            bufobj = self._view_data[num]
            # print(f"voici num: {num}, pos: {bufobj.pos}")
            data = bufobj.buf[bufobj.pos]
            bufobj.pos +=1 # (bufobj.pos +1) % self.nb_buf
        except IndexError:
            return
            
        return data
    
    #-----------------------------------------

    def get_pos(self, num):
        """ 
        returns the buffer position in the cache
        from AudiCache object
        """
        
        try:
            return self._view_data[num].pos
        except IndexError:
            preturn -1

    #-----------------------------------------

    def set_pos(self, num, pos):
        """ 
        set the buffer position in the cache
        from AudiCache object
        """
        
        try:
            self._view_data[num].pos = pos
        except IndexError:
            pass

    #-----------------------------------------

#========================================

if __name__ == "__main__":
    app = AudiCache()
    app.init_cache()
    input("It's OK...")

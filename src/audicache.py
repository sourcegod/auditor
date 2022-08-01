#! /usr/bin/env python
"""
    File: audicache.py
    Audio Cache Manager
    Date: Sun, 31/07/2022
    Author: Coolbrother
"""
import numpy as np

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

    #-----------------------------------------
    
    def init_cache(self):
        """
        initialize the data cache
        from AudiCache object
        """
        if not self._mixer: return

        self._nchannels = self._mixer._nchannels
        self._buf_size = self._mixer._buf_size
        self._in_type = self._mixer._in_type
        self._len_buf = self._mixer._len_buf
        self.cache_data = np.zeros((16, self._len_buf), dtype=self._in_type)

    #-----------------------------------------
    
    def preload(self):
        """
        preload data
        from AudiCache object
        """
        
        if not self._mixer: False
        if not self.cache_data.size: return False
        chan_lst = self._mixer._chan_lst
        if not chan_lst:
            print("No data is caching...")
            return False
        try:
            for (i, chan) in enumerate(chan_lst):
                if i < len(self.cache_data):
                    snd = self._mixer.get_sound_by_id(i)
                    if not snd: continue
                    else:
                        self.cache_data[i] = snd.read_data(self._buf_size)
                        self.is_caching = True
                        # print(f"find caching sound on channel {i}")
                else: break
        except IndexError:
            self.is_caching = False
            return False
        
        if self.is_caching:
            print("Preloading cache...")
        
        return True

    #-----------------------------------------

#========================================

if __name__ == "__main__":
    app = AudiCache()
    app.init_cache()
    input("It's OK...")

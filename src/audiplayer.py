#! /usr/bin/env python
"""
    File: audiplayer.py
    player module for auditor
    Date: Fri, 05/08/2022
    Author: Coolbrother
"""
import audimixer as aumix

class AudiPlayer(object):
    """ 
    Auditor manager
    from AudiPlayer object
    """
    def __init__(self, audio_driver=None):
        self.audio_driver = audio_driver
        self.mixer = aumix.AudiMixer(audio_driver)
        self.mixer.init()
        self._chan_lst = []
        self._snd_lst = []

    #-----------------------------------------

    def init(self):
        """ 
        init all things for auditor
        from AudiPlayer object
        """

        if self.mixer:
            self._chan_lst = self.mixer.get_channels()
            self._snd_lst = self.mixer.get_sounds()
        
        """
        if self.mixer:
            self.mixer.init()
            # self._audio_driver.init_audio()
        """
    
    #--------------------------------------
     
    def __del__(self):
        self.close()

    #-----------------------------------------

    def close(self):
        """ 
        close the mixer
        from AudiPlayer object
        """
        
        if self.mixer:
            self.mixer.close()
            self.mixer = None

    #-----------------------------------------
               
    def play_all(self):
        """
        play all channels
        from AudiPlayer object
        """
        
        for i, chan in enumerate(self._chan_lst):
            snd = self._snd_lst[i]
            chan.play(snd)

    #-----------------------------------------

    def pause(self):
        self._playing =0

    #-----------------------------------------
        
    def stop_all(self):
        """
        stop all channels
        from AudiPlayer object
        """

        self._playing =0
        for chan in self._chan_lst:
            chan.stop()

    #-----------------------------------------
 
    def play_channel(self, chan_num, snd_num=0, loops=0):
        """
        play channel with associated sound
        from AudiPlayer object
        """
        
        try:
            chan = self._chan_lst[chan_num]
            snd = self._snd_lst[snd_num]
        except IndexError:
            print("Index Error...")
            return
        chan.play(snd, loops)

        return True

    #-----------------------------------------

    def stop_channel(self, chan_num):
        """
        channel with associated sound
        from AudiPlayer object
        """
        
        try:
            self._chan_lst[chan_num].stop()
        except IndexError:
            return

        return True

    #-----------------------------------------

    def play_instru(self, instru=None):
        """
        temporary function to play instrument
        from AudiPlayer object
        """

        if instru is None: return
        instru.chan.play(instru.snd, instru.loop_count)

    #-----------------------------------------

    def stop_instru(self, instru=None):
        """
        temporary function to stop instrument
        from AudiPlayer object
        """

        if instru is None: return
        instru.chan.stop()

    #-----------------------------------------

    def play_cache(self, snd_num=0, loops=0):
        """
        play raw data from the Cache
        from AudiPlayer object
        """

        if not self.mixer.cacher.is_caching: return False
        self._playing =1
        self.mixer.set_cache_data(snd_num, loops, playing=self._playing)

        
        return True
        
    #-----------------------------------------

#========================================


if __name__ == "__main__":
    app = AudiPlayer()
    app.init()
    input("It's Ok")

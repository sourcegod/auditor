#! /usr/bin/python3
"""
    File: audimixer.py
    Module mixer for Auditor Engine
    Date: Sun, 17/07/2022
    Author: Coolbrother
"""
import audisound as ausnd
import audichannel as auchan
import audiport as aup

class CAudiList(list):
    """ object derived from list """
    def __init__(self):
        self._cur =0
        self.id =0
        self.type = ""
        self.name = ""

    #-----------------------------------------
    
    def get_list(self):
        # convenient function for getting the list object
        return self

    #-----------------------------------------

    def add(self, *args):
        self.extend(args)

    #-----------------------------------------

    def get_cur(self):
        res = None
        try:
            res = self[self._cur]
        except IndexError:
            pass

        
        return res

    #-----------------------------------------

    def set_cur(self, val):
        res = None
        if val >= 0 and val < len(self):
            try:
                self._cur = val
                res = self[self._cur]
            except IndexError:
                pass

        return res

    #-----------------------------------------
    
    def item_index(self):
        return self._cur

    #-----------------------------------------

    def get_prev(self):
        # get prev item in the list
        res = None
        cur = self._cur
        if cur > 0:
            try:
                cur -= 1
                res = self[cur]
            except IndexError:
                pass

        return res

    #-----------------------------------------


    def set_prev(self):
        # set prev item in the list
        res = None
        if self._cur > 0:
            try:
                self._cur -= 1
                res = self[self._cur]
            except IndexError:
                pass

        return res

    #-----------------------------------------

    def get_next(self):
        # get next item in the list
        res = None
        cur = self._cur
        if cur < len(self) -1:
            try:
                cur += 1
                res = self[cur]
            except IndexError:
                pass

        return res

    #-----------------------------------------


    def set_next(self):
        # set next item in the list
        res = None
        if self._cur < len(self) -1:
            try:
                self._cur += 1
                res = self[self._cur]
            except IndexError:
                pass

        return res

    #-----------------------------------------

    def get_first(self):
        """ get first item in the list
        """
        res = None
        if self:
            cur =0
            res = self[cur]

        return res

    #-----------------------------------------

    def set_first(self):
        """ set first item in the list
        """
        res = None
        if self:
            self._cur =0
            res = self[self._cur]

        return res

    #-----------------------------------------

    def get_last(self):
        """ get last item in the list
        """
        res = None
        if self:
            cur = len(self) -1
            res = self[cur]

        return res

    #-----------------------------------------

    def set_last(self):
        """ set last item in the list
        """
        res = None
        if self:
            self._cur = len(self) -1
            res = self[self._cur]

        return res

    #-----------------------------------------

    def is_first(self):
        """ is first item in the list
        """
        res =0
        if self:
            if self._cur == 0:
                res =1

        return res

    #-----------------------------------------


    def is_last(self):
        """ is last item in the list
        """
        res =0
        if self:
            if self._cur == len(self) -1:
                res =1

        return res

    #-----------------------------------------

    def get_max(self):
        pass

    #-----------------------------------------

    def get_min(self):
        pass
    
    #-----------------------------------------

#========================================


class AudiMixer(CAudiList):
    """ Mixer object to manage channel 
    """
    def __init__(self):
        self._playing =0
        self._sound_lst = [] # list for sound object
        self._chan_lst = self # list for channel object
        self._thr_audio = None
        # self._audio_driver = AlsaAudioDriver()
        self.audio_driver = aup.PortAudioDriver()

    #-----------------------------------------

    def init(self, nchannels=2, rate=44100, format=16):
        if self.audio_driver:
            self.audio_driver.init_audio(nchannels, rate, format)

        # create reserved channel for beep
        self.chan_beep = self.create_channel(1000)
    
    #-----------------------------------------
     
    def __del__(self):
        # self.close()
        pass

    #-----------------------------------------


         
    def beep(self, freq=440, lensec=1, loops=-2):
        """ beep square wave through mixer object
        freq: in hertz
        lensec: in second

        loopss: 
        -1: loop the sound infinitly
        0: no looping mode
        """
        
        snd = ausnd.AudiSample(mode=1) # empty sample
        rate = 44100
        nbsamp = int(lensec * rate)
        snd = snd.tone(1, freq, nbsamp)
        
        # play the beep on the reserved channel
        self.chan_beep.play(snd, loops)

    #-----------------------------------------


       
    def create_sample(self, fname):
        # create new sound
        snd = ausnd.AudiSample(mode=0, filename=fname)
        self._sound_lst.append(snd)

        return snd
    
    #-----------------------------------------

    def create_stream(self, fname):
        # create new stream
        snd = ausnd.AudiStream(filename=fname)
        self._sound_lst.append(snd)

        return snd
    
    #-----------------------------------------

    def create_channel(self, id):
        # create channel object
        chan = auchan.AudiChannel(id)
        self.audio_driver.add_channel(chan)
        chan.setmixcallback(self.audio_driver)
        self._chan_lst.append(chan)
        
        return chan

    #-----------------------------------------
                   
    def play(self):
        # play all channels
        """
        self._data = self._getmixdata()
        self._startthread(self._writedata)
        """
        for i, chan in enumerate(self._chan_lst):
            snd = self._sound_lst[i]
            chan.play(snd)


    #-----------------------------------------


    def pause(self):
        self._playing =0

    #-----------------------------------------
        
    def stop(self):
        # stop all channels
        self._playing =0
        for chan in self._chan_lst:
            chan.stop()

    #-----------------------------------------
    
    def close(self):
        if self.audio_driver:
            self.audio_driver.stop_thread()
            self.audio_driver.close()
        for chan in self._chan_lst:
            chan.stop()
        for snd in self._sound_lst:
            snd.close()


    #-----------------------------------------

   
#========================================

if __name__ == "__main__":
    app = AudiMixer()
    app.init()
    input("It's OK...")

#-----------------------------------------

#! /usr/bin/python3
"""
    File: audimixer.py
    Module mixer for Auditor Engine
    Date: Sun, 17/07/2022
    Author: Coolbrother
"""
import audisample as ausam
import audistream as austr
import audichannel as auchan
import audiport as aup

class AudiMixer(object):
    """ Mixer object to manage channel 
    """
    def __init__(self):
        self._playing =0
        self._sound_lst = [] # list for sound object
        self._chan_lst = [] # list for channel object
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
        self.close()
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
        
        snd = ausam.AudiSample(mode=1) # empty sample
        rate = 44100
        nbsamp = int(lensec * rate)
        snd = snd.tone(1, freq, nbsamp)
        
        # play the beep on the reserved channel
        self.chan_beep.play(snd, loops)

    #-----------------------------------------


       
    def create_sample(self, fname):
        # create new sound
        snd = ausam.AudiSample(mode=0, filename=fname)
        self._sound_lst.append(snd)

        return snd
    
    #-----------------------------------------

    def create_stream(self, fname):
        # create new stream
        snd = austr.AudiStream(filename=fname)
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

#! /usr/bin/python3
"""
    File: audimixer.py
    Module mixer for Auditor Engine
    Date: Sun, 17/07/2022
    Author: Coolbrother
"""
import numpy as np
# import audisample as ausam
import audisample2 as ausam
# import audistream as austr
import audistream2 as austr
import audichannel as auchan
# import audiport as aup
DEBUG =1 
def debug(msg="", title="", bell=True):
    if DEBUG:
        print("%s: %s" %(title, msg))
        if bell:
            print("\a")
    
#------------------------------------------------------------------------------


class AudiMixer(object):
    """ Mixer object to manage channels """
    def __init__(self, audio_driver=None):
        # self._audio_driver = AlsaAudioDriver()
        # self.audio_driver = aup.PortAudioDriver()
        self.audio_driver = audio_driver
        self._playing =0
        self._sound_lst = [] # list for sound object
        self._chan_lst = [] # list for channel object
        self._thr_audio = None
        # must be the same as buf_size in PortAudio Driver
        self._buf_size =512
        self._nchannels =2 # TODO: why nchannels not been initialized by init function?
        self._rate = 44100
        self._format =0
        self._in_type = np.int16
        self._out_type = np.int16
        self._mixing =0
        self._max_int16 = 32767
        self._len_buf = self._buf_size * self._nchannels
        # to maintaining the audio callback alive
        self._ret_buf = np.zeros((self._len_buf,), dtype=self._out_type).tobytes()


    #-----------------------------------------

    def init(self, nchannels=2, rate=44100, format=16):
        self._nchannels = nchannels
        self._rate = rate
        self._format = format
        debug("in the mixer init: nchannels: ", self._nchannels)
        if self.audio_driver:
            self.audio_driver.init_audio(nchannels, rate, format)
            self.audio_driver.set_mixer(self)


        # create reserved channel for beep
        self.chan_beep = self.create_channel(1000)
    
    #-----------------------------------------
     
    def __del__(self):
        self.close()
        pass

    #-----------------------------------------

    def get_mix_data(self): 
        """ 
        mixing audio data 
        from AudiMixer object
        """
        
        buf_lst = np.zeros((8, self._nchannels * self._buf_size), dtype=np.float32)
        buf1 = np.array([], dtype=np.float32)
        out_buf = np.array([], dtype=self._out_type)
        # debug("je pass ici")
        chan_num =0
        chan_count =0
        self._mixing =0

        for (i, chan) in enumerate(self._chan_lst):
            if chan.is_active():
                snd = chan.get_sound()
                curpos = snd.get_position(0) # in frames
                endpos = snd.get_end_position(0) # in frames
                if curpos >= endpos:
                    # debug("curpos >= endpos: %d, %d" %(curpos, endpos))
                    snd.loop_manager()
                    if not snd.is_looping():
                        chan.set_active(0)
                        continue
                   
                # whether buf_size =512 frames, so buf =512*4 = 2048 bytes
                # cause buf in byte, one frame = 4 bytes, 2 signed short, 
                # for 16 bits, 2 channels, 44100 rate,
                
                buf1 = snd.read_data(self._buf_size) 
                if not buf1.size:
                    debug("not buf1")
                    chan.set_active(0)
                    snd.set_play_count(0)
                    continue
                else:
                    if len(buf1) < self._len_buf:
                        buf1.resize(self._len_buf)
                        chan.set_active(0)
                        # debug(f"Buffer resized: {len(buf1)}, with len_buf: {self._len_buf}")

                    
                    """
                        nb_zeros = len1 - size
                        debug("Data too small, adding %d shorts filling with zeros" % nb_zeros)
                        # buf1 = chan.add_zeros(buf1, nb_zeros)
                        zero_lst = [0] * nb_zeros
                        buf1 += zero_lst
                    
                    # if chan.is_muted():
                    #    buf1 = chan.process_mute(buf1)
                    #vol = chan.get_volume()
                    # buf1 = chan.process_volume(buf1)
                    # (leftpan, rightpan) = chan.getpanning()
                    # buf1 = chan.process_panning(buf1)
                    # buf1 = chan.set_effect(buf1)
                    """
                    
                    # buf_lst.append(buf1)
                    # len1 = buf1.size
                    if chan.is_vel():
                        chan.process_vel(buf1)
                    
                    # FIX: we cannot modify array that is in readonly, so we copy
                    # to avoid saturation when summing, we divide the amplitude
                    # buf1 = buf1 / 2
                    buf_lst[i] = buf1
                    chan_num = i
                    chan_count +=1
                    # debug("voici i: %d et shape: %s" %(i, buf1.shape))
        
        # out of the loop
        if buf_lst.size:
            if chan_count == 0: # no more audio data
                self._mixing =0
                # maintaining the audio callback alive
                return self._ret_buf
            elif chan_count == 1: # no copy data
                out_buf = buf_lst[chan_num] # (buf_lst[chan_num] * 32767).astype('int16')
                # no copy, but very bad sound
                # out_buf = buf_lst[chan_num].view(self._out_type)
                # debug("Yes mannn")
            elif chan_count >= 2:
                # passing the type of array result to avoid copy with astype letter
               
                # avoid saturation, but no copy
                max_amp = np.max(np.abs(buf_lst))
                # print(f"voici max: {val_max}")
                # TODO: find better solution for readjust level after mixing
                coef = 1/np.sqrt(2)
                for buf in buf_lst: buf *= coef # temporary
                line = np.sum(buf_lst, axis=0, dtype=np.float32) # sum each column per line
                # readjust the volume
                # TODO: normalize it
                max_amp = np.max(line)
                # line += (1.0 - max_amp)
                # line += 0.2 # FIXIT
                # print(f"voici max_amp: {max_amp}, et max_line: {1.0 - max_amp}")
                
                """
                # No more necessary
                # use line.view to avoid copy array,
                # and using np.clip to limit values
                val_lim = 32767
                # limit value in place to avoid copy
                np.clip(line, -val_lim -1, val_lim, out=line)
                """
                
                out_buf = line # no copy
                # debug("voici %d, %s" %(len(out_buf), out_buf.dtype))

            if out_buf.size:
                # debug("voici: %s" % out_buf)
                self._mixing =1
                
                # avoid copy
                return (out_buf * self._max_int16).astype(np.int16).tostring()
                # return out_buf.tostring()
        
        else: # buf_lst is empty
            self._mixing =0
            # debug("Mixing finished...")
            
            return None

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
        """
        create new sound
        from AudiMixer object
        """

        snd = ausam.AudiSample(mode=0)
        snd = snd.load(fname)
        if snd is not None: 
            self._sound_lst.append(snd)

        return snd
    
    #-----------------------------------------

    def create_stream(self, filename):
        # create new stream
        snd = austr.AudiStream()
        snd = snd.load(filename)
        if snd is not None: 
            self._sound_lst.append(snd)

        return snd
    
    #-----------------------------------------

    def create_channel(self, id):
        # create channel object
        chan = auchan.AudiChannel(id)
        if self.audio_driver:
            chan.set_mix_callback(self.audio_driver)
            self._chan_lst.append(chan)
        
        return chan

    #-----------------------------------------
                   
    def play(self):
        """
        play all channels
        from AudiMixer object
        """
        
        for i, chan in enumerate(self._chan_lst):
            snd = self._sound_lst[i]
            chan.play(snd)

    #-----------------------------------------

    def play_channel(self, chan_num, snd_num=0):
        """
        play channel with associated sound
        from AudiMixer object
        """
        
        try:
            chan = self._chan_lst[chan_num]
            snd = self._sound_lst[snd_num]
        except IndexError:
            return
        chan.play(snd)

        return True

    #-----------------------------------------

    def stop_channel(self, chan_num):
        """
        channel with associated sound
        from AudiMixer object
        """
        
        try:
            self._chan_lst[chan_num].stop()
        except IndexError:
            return

        return True

    #-----------------------------------------

    def pause(self):
        self._playing =0

    #-----------------------------------------
        
    def stop(self):
        """
        stop all channels
        from AudiMixer object
        """

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

    def get_sounds(self):
        """
        returns sound list 
        from AudiMixer object
        """

        return self._sound_lst

    #-----------------------------------------

    def  get_channels(self):
        """
        returns channel list 
        from AudiMixer object
        """

        return self._chan_lst

    #-----------------------------------------

   
#========================================

if __name__ == "__main__":
    app = AudiMixer()
    app.init()
    input("It's OK...")

#-----------------------------------------

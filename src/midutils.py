#! /usr/bin/python3
"""
    Utils functions for midi notes number, notes names, and frequencies.
    and play midi messages through external midi device like fluidsynth or timidity server.
    Last update: Mon, 25/07/2022

    Date: Tue, 14/09/2021
    Author: Coolbrother
"""
import mido

# Midi notes numbers: from 0 to 127
# Midi notes names: from C-1 to G9

_note_names = [
            'C', 'C#', 'D', 'D#',
            'E', 'F', 'F#', 
            'G', 'G#', 'A', 'A#', 'B'
            ]

_note_lst = []
_freq_lst = []
_input_names = []
_output_names = []
_midi_in = _midi_out = None
_midi_running = False

def limit_value(val, min_val=0, max_val=127):
    if val < min_val: return min_val
    if val > max_val: return max_val
    return val

#-----------------------------------------

def _init_noteList():
    """ initializing notes list """
    global _note_lst
    _note_lst = [name + str(i) for i in range(-1, 10) for (j, name) in enumerate(_note_names) if (i+1)*12+j <= 127]
    return _note_lst

#-----------------------------------------

def _init_noteFreq():
    """ initializing notes and freqs list """
    global _note_lst, _freq_lst
    _note_lst = []; _freq_lst = []
    count =0
    for i in range(-1, 10):
        for name in _note_names:
            _note_lst.append(name + str(i))
            _freq_lst.append(mid2freq(count))
            count += 1
            if count > 127:
                return

#-----------------------------------------

def mid2freq(val):
    """ returns freq from midi note number """
    ref = 440.0/32 # 13.75 Hz, note A-1
    # we substract -9 for getting C-1 note name
    return ref * pow(2, (int(val) - 9) * 1/12.0)

#-----------------------------------------

def mid2note(val):
    """ convert midi number to note name """
    try:
        val = limit_value(val, 0, 127)
        return _note_lst[val]
    except IndexError:
        return ""

#-----------------------------------------

def note2mid(name):
    """ convert note name to midi note number """
    try:
        return _note_lst.index(name.upper())
    except IndexError:
        return 0

#-----------------------------------------

def note2freq(name):
    """ convert note name to freq """
    try:
        val = _note_lst.index(name.upper())
        return _freq_lst[val]
    except IndexError:
        return 0

#-----------------------------------------

def init():
    """ dumy function """
    pass

#-----------------------------------------

def close():
    """ dumy function """
    pass

#-----------------------------------------

def open_input(port=0):
    """
    like receive_from function, but more coherent
    Get incoming messages - nonblocking interface
    with cb_func as callback
    """

    portname = ""
    midi_in = None
    input_names = mido.get_input_names()
    try:
        portname = input_names[port]
    except IndexError:
        print("Error: Midi Port {} is not available".format(port))
    
    if portname:
        print("Found Midi Input name: ",portname)
        midi_in = mido.open_input(portname)
        
    return midi_in

#-----------------------------------------

def open_output(port=0):
    """
    open midi output port
    from MidiManager object
    """

    midi_out = None

    output_names = mido.get_output_names()
    try:
        port_name = output_names[port]
        print("Found Midi Output name: ",port_name)
        midi_out = mido.open_output(port_name)
    except IndexError:
        print("Error opening midi output Port {}".format(port))
    
    return midi_out

#-----------------------------------------

def get_input_names():
    return mido.get_input_names()

#-----------------------------------------

def get_output_names():
    return mido.get_output_names()

#-----------------------------------------


def get_input_count():
    return len(mido.get_input_names())

#-----------------------------------------

def get_output_count():
    return len(mido.get_output_names())

#-----------------------------------------

def play_midi(inport=0, outport=0, printing=False):
    """ display midi in messages """
    midi_in = open_input(inport)
    midi_out = open_output(outport)

    print("Press a keyboard's key...")
    print("---------------------")
    
    try:
        while True:
            msg = midi_in.poll()
            if msg:
                m_type = msg.type
                if m_type in ['note_on', 'note_off']:
                    m_note = msg.note
                    m_vel = msg.velocity
                    if m_type == "note_on" and m_vel == 0:
                        if printing:
                            print("Midi_in Message: ")
                            print(f"Note_off, Midi Number: {m_note}, Name: {mid2note(m_note)}")
                            print(f"Details: {msg}")
                    elif m_type == "note_on" and m_vel >0:
                        if printing:
                            print(f"Note_on, Midi Number: {m_note}, Name: {mid2note(m_note)}")
                            freq = mid2freq(m_note)
                            print(f"Freq: {freq:.2f}")
                            print(f"Details: {msg}")
                else:# others messages
                    if printing:
                        print("Unknown message")
                        print(f"Details: {msg}")
                if  midi_out:
                    midi_out.send(msg)
                    if printing: 
                        print("Midi_out message.")
                # beep
                if printing: 
                    print("\a") 
    
    except KeyboardInterrupt as err:
        print("Stoping...")

#-------------------------------------------

def print_input_names():
    input_names = get_input_names()
    print("Midi Input Names")
    for (i, name) in enumerate(input_names):
        print(f"{i}: {name}")
    print("---------------------")

#-------------------------------------------

def print_output_names():
    output_names = get_output_names()
    print("Midi Output Names")
    for (i, name) in enumerate(output_names):
        print(f"{i}: {name}")
    print("---------------------")

#-------------------------------------------
def _midi_handler(msg, inport=0, outport=0, printing=False):
    """ 
    Handling midi messages 
    """
    

    if msg:
        # print("\a") # beep
        m_type = msg.type
        if m_type in ['note_on', 'note_off']:
            m_note = msg.note
            m_vel = msg.velocity
            # Note off
            if m_type == "note_on" and m_vel == 0:
                m_type = "note_off"
                # play_notes(m_type, m_note, m_vel)
                if printing:
                    print("Midi_in Message: ")
                    print(f"Note_off, Midi Number: {m_note}, Name: {mid2note(m_note)}")
                    print(f"Details: {msg}")
            # Note on
            elif m_type == "note_on" and m_vel >0:
                # play_notes(m_type, m_note, m_vel)
                pass
                if printing:
                    print(f"Note_on, Midi Number: {m_note}, Name: {mid2note(m_note)}")
                    freq = mid2freq(m_note)
                    print(f"Freq: {freq:.2f}")
                    print(f"Details: {msg}")
        else:# others messages
            if printing:
                print("Unknown message")
                print(f"Details: {msg}")
        if  _midi_out:
            _midi_out.send(msg)
            if printing: 
                print("Midi_out message.")
        # beep
        if printing: 
            print("\a")
    # time.sleep(0.1)

#-------------------------------------------

def start_midi_thread(inport=0, outport=0, func=None):
    """
    Attach callback function to the Midi port Callback
    """
    global _midi_in, _midi_out, _midi_running
    _midi_in = open_input(inport)
    # func = _midi_handler
    _midi_in.callback = func
    _midi_out = open_output(outport)
    _midi_running = True
    
    return (_midi_in, _midi_out)
#-------------------------------------------

def stop_midi_thread():
    """
    Stopping Midi callback
    """
    global _midi_in, _midi_out, _midi_running

    if _midi_running:
        if _midi_in:
            _midi_in.callback = None
            _midi_in.close()
        if _midi_out:
            _midi_out.close()
        _midi_running = False

    return (_midi_in, _midi_out)

#-------------------------------------------

# initializing lists
# _init_noteList()
# initializing note freq dic
_init_noteFreq()
receive_from = open_input
def test():
    hz = note2freq
    print("---------------------")
    print("Test on midutils\n")
    print("Note names list:")
    for (i, item) in enumerate(_note_lst):
        print(f"{i}: {item}", end=", ")
        print()
    for (name, freq) in zip(_note_lst, _freq_lst):
        print(f"{name}: {freq}")

    print(f"Note to Mid A4: {note2mid('a4')}")
    print(f"Note to Freq A3: {hz('a3')}")
    print("Midi Input count: ", get_input_count())
    print("Midi Output count: ", get_output_count())
    print("---------------------")

#-----------------------------------------

if __name__ == "__main__":
    inport=1
    outport =4
    printing = False
    test()
    print_input_names()
    print_output_names()
    play_midi(inport, outport, printing)
    input("Pres Enter...")

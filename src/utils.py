#python3
"""
    File: utils.py
    Module for miscellaneous functions.
    Date: Mon, 04/07/2022
    Author: Coolbrother
"""

DEBUG=1
_logfile = None

def debug(msg="", title="", bell=True, write_file=False, stdout=True, endline=False):
    if DEBUG:
        if stdout:
            txt = ""
            if title and not msg:
                txt = "{}".format(title)
            elif msg and not title:
                txt = "{}".format(msg)
            elif msg and title:
                txt = "{}: {}".format(title, msg)
            print(txt)

        if bell:
            # curses.beep()
            print("\a")
        if write_file:
            with open('/tmp/zikdrum.log', 'a') as fh:
                # _logfile.write("{}:\ {}\n".format(title, msg))
                txt = ""
                if title and not msg:
                    txt = "{}:".format(title)
                elif msg and not title:
                    txt = "{}".format(msg)
                elif title and msg:
                    txt = "{}:\n{}".format(title, msg)

                print(txt, file=fh) 

                if endline:
                    print("", file=fh)

#------------------------------------------------------------------------------

def beep():
    # curses.beep()
    print("\a")

#-------------------------------------------

def limit_value(val, min_val=0, max_val=127):
    """ limit value """
    
    if val < min_val: val = min_val
    elif val > max_val: val = max_val
    
    return val

#-------------------------------------------

def change_item(item_num, item_lst, step=0, adding=0):
    """
    generic change item
    """

    changing =0
    val =0
    new_item = None
    if not item_lst:
        return (item_num, new_item)

    max_val = len(item_lst) -1
    if adding == 0:
        if step == -1:
            step = max_val
    else: # adding value
        val = item_num + step
        changing =1
    if changing:
        step = limit_value(val, 0, max_val)
    if item_num != step:
        item_num = step
        new_item = item_lst[item_num]
    else: # no change for menu num
        beep()
    
    return (item_num, new_item)

#-------------------------------------------



#!user/bin/python3

'''
A light-weight music player.
'''

import sys
import threading

import audio
import input_listener
import ui

# -----------------------------------------
# Global constants / variables
# -----------------------------------------

___HELP__ = "This is some help text"

app_started = False

# -----------------------------------------
# Methods
# -----------------------------------------

def start_app():
    '''Starts the main application'''
    ui.init()

    global app_started
    app_started = True

    if "-nosplash" not in sys.argv:
        ui.display_splash()

    ui.refresh()

    #threading._start_new_thread(ui.refresh_thread, ())

    # Start listening for user input
    input_listener.listen()


def main():
    '''Start terminal screen and set up'''

    if "-h" in sys.argv or "-help" in sys.argv:
        print (___HELP__);

    else:
        start_app()


# -----------------------------------------
# Entry point
# -----------------------------------------

failure = False
failure_msg = ''

try:
    main()
except BaseException as e:
    failure = True
    failure_msg = str(e)
finally:
    if app_started:
        ui.deinit()
    audio.stop()

    if failure:
        print("Unexpected failure! Safely handled.\nException:{}".format(failure_msg))

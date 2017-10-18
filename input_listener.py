import os

import audio
import ui

import pyglet
# -----------------------------------------
# Global
# -----------------------------------------

__INPUT_TRIGGER__ = ':'

__PLAY_PAUSE__ = [' ', 'p', '\n']
__STOP__ = ['s']
__SEL_NEXT__ = ['n']
__PLAY_NEXT__ = ['N']
__SEL_PREV__ = ['b']
__PLAY_PREV__ = ['B']


# -----------------------------------------
# Methods
# -----------------------------------------

def listen():
    '''Listens for input, delegating input to the processing when recieved.'''

    #ui.write_cmd_line('Type \'' + __INPUT_TRIGGER__ + '\' to begin command input.')
    #audio.add_to_playlist(['test.mp3'])
    #audio.add_to_playlist(['test2.mp3'])
    #audio.add_to_playlist(['test.flac'])
    #audio.add_to_playlist(['test.m4a'])
    #audio.play_playlist_no(1)
    
    # Enter infinite (blocking) loop waiting for input.
    # We refresh to clear previous input / output, then await input trigger, at which point we capture input (terminated with ENTER) and process it.
    # NOTE: Resizing the terminal window is processed as input. This causes the loop to execute and refreshes the UI to match the new window size.
    quit_app = False
    while not quit_app:
        update()
        key = ui.__stdscr.getkey()

        if key in __PLAY_PAUSE__:
            audio.play_pause()
        elif key in __STOP__:
            audio.stop()
        elif key in __SEL_NEXT__:
            audio.sel_next_track()
        elif key in __PLAY_NEXT__:
            audio.sel_next_track()
            audio.play_current()
        elif key in __SEL_PREV__:
            audio.sel_prev_track()
        elif key in __PLAY_PREV__:
            audio.sel_prev_track()
            audio.play_current()

        elif key == __INPUT_TRIGGER__:
            cmd = ui.read_cmd_line()

            try:
                quit_app = process_input(cmd)
            except:
                update("Invalid input")


def update(message = None):
    '''Refreshes the screen to display the latest action and then writes the message to screen'''
    ui.refresh()
    if message is not None:
        ui.write_cmd_line(message)


def process_input(cmd):
    '''Processes the provided input command, executing appropriate logic.'''

    cmd_list = cmd.split()


    def is_command(expected_cmds):
        '''Helper method to check if the first element of the command args matches any provided element of a list
           If true is returned, the app should be terminated.'''
        for cmd_i in expected_cmds:
            if cmd_list[0] == cmd_i:
                return True
        return False

    def has_arg(expected_args):
        '''Helper method to check if the command contains any of the provided expected_args'''
        for arg_i in expected_args:
            if arg_i in cmd_list:
                return True
        return False



    # If we have one or more args, attempt to process
    if len(cmd_list) > 0:

        # Basic commands without args
        if is_command(['help', 'h']):
            show_help()
        elif is_command(['refresh', 'rf']):
            ui.refresh()
        elif is_command(['quit', 'q']):
            return True



        # Commands with optional/mandatory args

        # Play the specified file.
        elif is_command(['play', 'p']):
            if len(cmd_list) > 1:
                if audio.get_playback_state() is not audio.PlaybackState.STOPPED:
                        audio.stop()         
                if has_arg(['-file', '-f']):                                            # play filename
                    audio.play(cmd_list[2])
                    update('Playing file {}'.format(cmd_list[2]))
                else:                                                                   # play playlist index
                    audio.play_playlist_no( int(cmd_list[1]) )
                    update('Playing playlist item {}'.format(cmd_list[1]))
            else:
                audio.play_pause()
                update('Playing/pausing current track')



        # Stops playback
        elif is_command(['stop', 's']):
            audio.stop()
            update('Stopped current track')



        # Add all files listed to the playlist
        elif is_command(['add', 'a']):
            if has_arg(["-dir"]):
                count = 0
                directory = os.fsencode(os.getcwd())
                for filename in os.listdir(directory):
                    filen = os.fsdecode(filename)
                    count = count + audio.add_to_playlist([filen])
                update('Added {} file(s) from directory: {}'.format(count, os.getcwd()))
            else:
                count = audio.add_to_playlist(cmd_list[1:len(cmd_list)])
                update('Added {} file(s) to playlist: {}'.format(count, cmd_list[1:len(cmd_list)]))



        # Remove all listed playlists indices
        elif is_command(['remove', 'r']):
            if has_arg(['-all', '-a']):
                audio.clear_playlist()
                update('Playlist cleared')
            else:
                audio.rem_from_playlist(cmd_list[1:len(cmd_list)])
                update('Removed from playlist: {}'.format(cmd_list[1:len(cmd_list)]))



        # Change main panel mode
        elif is_command(['mode', 'm']):
            if has_arg(['help']):
                ui.set_mode(ui.MainPanelMode.HELP)
            if has_arg(['details']):
                ui.set_mode(ui.MainPanelMode.DETAILS)
            update('Changed mode to {}'.format(cmd_list[1]))


        # Unrecognized command
        else:
           update('Unrecognized command.')

    return False


def show_help():
    '''Shows help text to the user'''
    ui.write_cmd_line('For detailed help, type \':\' to enter input mode and type \'mode help\'')


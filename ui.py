import curses, curses.panel
import time

from enum import Enum

import audio

# -----------------------------------------
# Types
# -----------------------------------------

class MainPanelMode(Enum):
    HELP = 1
    DETAILS = 2


# -----------------------------------------
# Global constants
# -----------------------------------------

__SPLASH_TEXT__ = "Welcome to Argon Music Player!"
__PLAYLIST_HEADER__ = " PLAYLIST"
__MAIN_HEADER__ = "{}"
__INPUT_PROMPT_CHAR__ = ": "
__OUTPUT_FORMAT__ = "< {} >"
__PLAYBACK_BAR_HEIGHT__ = 5
__PLAYBACK_BAR_HEADER__ = " NOW PLAYING: {}"
__PLAYBACK_BAR_INFO__ = "{}"

__UNKNOWN_TRACK_DATA__ = "Unknown"

# -----------------------------------------
# Global variables
# -----------------------------------------

__stdscr = None

__playback_panel = None
__playback_width = None
__playbacK_title = __PLAYBACK_BAR_HEADER__

__main_panel = None
__main_width = None
__main_state = MainPanelMode.DETAILS

__playlist = None
__playlist_width = None


# -----------------------------------------
# General
# -----------------------------------------

def init():
    '''Initializes the terminal-based GUI'''
    global __stdscr
    __stdscr = curses.initscr()
    __stdscr.keypad(True)
    curses.noecho()         # do not echo input
    curses.cbreak()         # do not wait for Enter after input


def deinit():
    '''Deinitializes the terminal-based GUI'''
    global __stdscr
    __stdscr.keypad(False)
    curses.echo()
    curses.nocbreak()
    curses.endwin()


def refresh_thread():
    while(True):
        time.sleep(1)
        refresh()


def refresh():
    '''Redraws the UI at the current terminal window size'''
    curses.update_lines_cols()
    __stdscr.clear()

    global __playback_width, __main_width, __playlist_width
    __playback_width = __main_width = (int)((curses.COLS / 4) * 3)
    __playlist_width = (int)(curses.COLS / 4)

    draw_playback()
    draw_main()
    draw_playlist()

    update_playback()
    update_main()
    update_playlist()
    
    curses.panel.update_panels()
    __stdscr.refresh()


def display_splash():
    '''Plays an introductory splash screen'''
    __stdscr.border(0)
    __stdscr.refresh()
    time.sleep(0.5)

    centreY = (int)(curses.LINES / 2);  centreX = (int)(curses.COLS / 2);
    halfSplashLen = (int)(len(__SPLASH_TEXT__) / 2)

    win = curses.newwin(5, len(__SPLASH_TEXT__) + 6, centreY - 2, centreX - halfSplashLen - 3)
    win.border(0)
    win.refresh()

    complete = False
    counter = 0
    while (not complete):
        time.sleep(0.03)
        __stdscr.addstr(centreY, centreX - halfSplashLen, __SPLASH_TEXT__[:counter], curses.A_BOLD)
        counter += 1
        __stdscr.refresh()

        if (counter >= len(__SPLASH_TEXT__)):
            complete = True
    
    time.sleep(1)
    curses.beep()


# -----------------------------------------
# Create UI elements
# -----------------------------------------

def draw_playback():
    '''Draws the seekbar element of the GUI'''

    # Create window attached to left side of screen, 3/4 width of screen and equal to screens height.
    win = curses.newwin(__PLAYBACK_BAR_HEIGHT__, __playback_width, 0, 0)
    win.erase()
    win.box()

    global __playback_panel
    __playback_panel = curses.panel.new_panel(win)


def draw_main():
    '''Draws the main element of the GUI'''

    # Create window attached to left side of screen, 3/4 width of screen and equal to screens height.
    win = curses.newwin(curses.LINES - __PLAYBACK_BAR_HEIGHT__, __main_width, __PLAYBACK_BAR_HEIGHT__, 0)
    win.erase()
    win.box()

    global __main_panel
    __main_panel = curses.panel.new_panel(win)


def draw_playlist():
    '''Draws the playlist element of the GUI'''

    # Create window attached to right side of screen, 1/4 width of screen and equal to screens height.
    win = curses.newwin(curses.LINES, __playlist_width + 1, 0, curses.COLS - (curses.COLS - __main_width))
    win.erase()
    win.box()

    global __playlist
    __playlist = curses.panel.new_panel(win)


# -----------------------------------------
# Update UI elements
# -----------------------------------------

def update_playback():
    win = __playback_panel.window()
    y, x = win.getmaxyx()

    win.addstr(0, 1, __PLAYBACK_BAR_HEADER__.format(get_playback_state().name).ljust(x - 2), curses.A_REVERSE)

    if get_playback_state() is not audio.PlaybackState.STOPPED:
        track = get_current_track()
        if track is not None:
            win.addnstr(1, 2, __PLAYBACK_BAR_INFO__.format(track), x - 1)

    current_time = get_current_track_time()
    a, b, total_time = get_current_track_info()

    # Timestamps
    win.addnstr(2, 2, total_time.get_timestamp_str().rjust(x - 4), x - 2)
    win.addnstr(2, 2, current_time.get_timestamp_str(), x - 2)

    # Progress bar
    fill = 0
    if total_time.totalseconds > 0:
        fill = int((x - 4) * (current_time.totalseconds / total_time.totalseconds)) + 1
    win.addnstr(3, 1, '[', x - 1)
    win.addnstr(3, x - 2, ']', x - 1)
    win.addnstr(3, 2, ''.ljust(fill), x - 2, curses.A_REVERSE)


def update_main():
    '''Draws the current state of the main panel'''
    win = __main_panel.window()
    y, x = win.getmaxyx()

    # Print all available modes, enclosing our current mode in brackets
    header_text = ''
    for name, member in MainPanelMode.__members__.items():
        item_format = '[{}] ' if name == __main_state.name else '{} '
        header_text = header_text + ' ' + item_format.format(name)
    win.addstr(0, 1, header_text.ljust(x - 2), curses.A_REVERSE)

    start_x, end_x = 1, x - 2

    # Wrap in try-catch so that if the terminal is smaller than the data to write we effectively short-exit.
    try:
        if __main_state is MainPanelMode.HELP:
            win.addnstr(2, start_x,  ":                                          Activates input mode", end_x)

            win.addnstr(4, start_x,  "Commands:", end_x)
            win.addnstr(5, start_x,  "h | help                                   Displays information to navigate to this screen", end_x)
            win.addnstr(6, start_x,  "m | mode   [help | details]                Changes the main panel mode", end_x)
            win.addnstr(7, start_x,  "p | play                                   Toggles play / pause of the current track", end_x)
            win.addnstr(8, start_x,  "p | play   [-f | -file] [filename]         Plays the file specified", end_x)
            win.addnstr(9, start_x,  "p | play   [playlist_track_num]            Plays the track specified from the playlist", end_x)
            win.addnstr(10, start_x, "s | stop                                   Stops playback", end_x)
            win.addnstr(11, start_x, "a | add    [filename [, ...]]              Adds the file(s) specified to the playlist", end_x)
            win.addnstr(12, start_x, "a | add    -dir                            Adds all supported audio files in the current directory", end_x)
            win.addnstr(13, start_x, "r | remove [playlist_track_num [, ...]]    Removes the track(s) specified from the playlist", end_x)
            win.addnstr(14, start_x, "r | remove [-all | -a]                     Removes all tracks from the playlist", end_x)
            win.addnstr(15, start_x, "q | quit                                   Quits the applicatio safely", end_x)

            win.addnstr(17, start_x, "Quick controls:  ", end_x)
            win.addnstr(18, start_x, "p|spacebar:play/pause     s:stop     b:previous     n:next", end_x)
            

        elif __main_state is MainPanelMode.DETAILS:
            info, audiof, duration = get_current_track_info()
            
            if info is not None:
                win.addnstr(2, start_x, "Title: {}".format(info.title.decode('utf-8') if info.title else __UNKNOWN_TRACK_DATA__), end_x)
                win.addnstr(3, start_x, "Artist: {}".format(info.author.decode('utf-8') if info.author else __UNKNOWN_TRACK_DATA__), end_x)
                win.addnstr(4, start_x, "Album: {}".format(info.album.decode('utf-8') if info.album else __UNKNOWN_TRACK_DATA__), end_x)
                win.addnstr(5, start_x, "Year: {}".format(info.year if info.year else __UNKNOWN_TRACK_DATA__), end_x)
                win.addnstr(6, start_x, "Track: {}".format(info.track if info.track else __UNKNOWN_TRACK_DATA__), end_x)
                win.addnstr(7, start_x, "Duration: {}".format(duration.get_timestamp_str() if duration else __UNKNOWN_TRACK_DATA__), end_x)
                win.addnstr(8, start_x, "Genre: {}".format(info.genre.decode('utf-8') if info.genre else __UNKNOWN_TRACK_DATA__), end_x)
            if audiof is not None:
                win.addnstr(10, start_x, "Channels: {}".format(audiof.channels if audiof.channels else __UNKNOWN_TRACK_DATA__), end_x)
                win.addnstr(11, start_x, "Sample rate: {}".format(audiof.sample_rate if audiof.sample_rate else __UNKNOWN_TRACK_DATA__), end_x)
                win.addnstr(12, start_x, "Sample size: {}".format(audiof.sample_size if audiof.sample_size else __UNKNOWN_TRACK_DATA__), end_x)
    except:
        pass


def update_playlist():
    '''Draws the current playlist to the playlist UI element'''
    win = __playlist.window()
    y, x = win.getmaxyx()
    
    win.addstr(0, 1, __PLAYLIST_HEADER__.ljust(x - 2), curses.A_REVERSE)
    
    width = __playlist_width - 1
    offset = 1
    for track in get_playlist_tracks():
        highlight = curses.A_REVERSE if (offset - 1 == get_current_track_idx()) else curses.A_NORMAL
        win.addnstr(offset, 1 , "{}. {}".format(offset, track).ljust(width), width, highlight)
        offset = offset + 1

    curses.panel.update_panels()


# -----------------------------------------
# Command input
# -----------------------------------------

def read_cmd_line(message = ''):
    '''Draws and focuses the input panel that allows the user to issue commands to the music player.
       A string can be passed in, which will be prepended before the input cursor (as a prompt, etc).'''

    __stdscr.hline(curses.LINES - 3, 1, '_', __main_width - 2)
    __stdscr.addstr(curses.LINES - 2, 1, message + __INPUT_PROMPT_CHAR__)
    __stdscr.refresh()

    # Display string prompt with message. Adjust cursor pos according to input indicator and any message, and limit to length of input panel.
    curses.echo()
    cmd = __stdscr.getstr(curses.LINES - 2, 1 + len(__INPUT_PROMPT_CHAR__) + len(message), __main_width - len(__INPUT_PROMPT_CHAR__) - len(message) - 2).decode(encoding="utf-8")
    curses.noecho()

    return cmd


def write_cmd_line(message):
    '''Writes the provided message to the input panel, halting until the user provides input to dismiss it'''

    __stdscr.hline(curses.LINES - 3, 1, '_', __main_width - 2)
    __stdscr.addnstr(curses.LINES - 2, 1, __OUTPUT_FORMAT__.format(message).ljust(__main_width - 2), __main_width - 2)
    __stdscr.refresh()
    # Halt until user presses another key
    __stdscr.getch()


# -----------------------------------------
# Helpers
# -----------------------------------------

def get_playlist_tracks():
    '''Returns the list of tracks to display in the playlist'''
    return audio.get_playlist()

def get_current_track():
    '''Returns the current track'''
    return audio.get_current_track()

def get_current_track_idx():
    '''Returns the current track index'''
    return audio.get_current_track_idx()

def get_playback_state():
    '''Returns the current state of playback from the audio controller'''
    return audio.get_playback_state()

def get_current_track_info():
    '''Returns info regarding the currently playing track'''
    return audio.get_current_track_info()

def get_current_track_time():
    '''Returns the timestamp of the currently playing track'''
    return audio.get_current_track_time()


def set_mode(mode):
    '''Sets the mode of the app (main panel)'''
    global __main_state
    if (isinstance(mode, MainPanelMode)):
        __main_state = mode
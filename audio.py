'''
Handles all-audio related logic
'''

from enum import Enum
import os.path
import pyglet


# -----------------------------------------
# Types
# -----------------------------------------

class PlaybackState(Enum):
    '''The different states that the player can be in'''
    STOPPED = 1
    PLAYING = 2
    PAUSED = 3

class Duration(object):
    '''Stores the duration of a track'''
    def __init__(self, hours = 0, minutes = 0, seconds = 0):
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.totalseconds = (hours * 3600) + (minutes * 60) + seconds

    def set_from_sec(self, sec):
        self.hours = int(sec / 3600)
        self.minutes = int(sec / 60) % 60
        self.seconds = int(sec) % 60
        self.totalseconds = sec

    def get_timestamp_str(self):
        '''Returns a string-type timestamp in the format of hh:mm:ss'''
        return '{}:{}:{}'.format('{}'.format(self.hours).rjust(2, '0'), '{}'.format(self.minutes).rjust(2, '0'), '{}'.format(self.seconds).rjust(2, '0'))


# -----------------------------------------
# Global constants
# -----------------------------------------

__SUPPORTED_FORMATS__ = ['au', 'mp2', 'mp3', 'ogg', 'wav', 'wma', 'flac', 'm4a']


# -----------------------------------------
# Global variables
# -----------------------------------------

__player__ = None

__playlist__ = []
__current_track_idx__ = 0
__playback_state__ = PlaybackState.STOPPED


# -----------------------------------------
# Functions - Getters
# -----------------------------------------

def get_playback_state():
    return __playback_state__


def get_playlist():
    return __playlist__


def get_current_track():
    if __current_track_idx__ < len(__playlist__):
        return __playlist__[__current_track_idx__]
    else:
        return None

def get_current_track_idx():
    return __current_track_idx__

def get_current_track_time():
    '''Returns the current playing time of the current track.'''
    duration = Duration()
    if (__player__ is not None):
        duration.set_from_sec(__player__.time)
    return duration

def get_current_track_duration():
    '''Returns the total playing time of the current track.'''
    duration = Duration()
    if (__player__ is not None):
        if __player__.source.duration:
            duration.set_from_sec(__player__.source.duration)
    return duration

def get_current_track_info():
    '''Returns a tuple of three objects: trackInfo, audioFormat, and trackDuration.
       Available trackInfo properties (accessible as info.property_name):     title, album, author, year, track, genre, copyright, comment
       Available audioFormat properties (accessible as audiof.property_name): channels, sample_size, sample_rate
       Available trackDuration properties (accessible as trackDuration.property_name): hours, minutes, seconds'''
    info = None
    audiof = None
    if (__player__ is not None):
        if __player__.source.info:
            info = __player__.source.info
        if __player__.source.audio_format:
            audiof = __player__.source.audio_format
        
    return info, audiof, get_current_track_duration()


# -----------------------------------------
# Functions - Playlist Managagment
# -----------------------------------------

def add_to_playlist(tracklist):
    '''Appends the provided files to the playlist, firest checking for their existence and then if they are supported'''
    global __playlist__
    count = 0
    for track in tracklist:
        if os.path.isfile(track) and (os.path.splitext(track)[1][1:].strip().lower() in __SUPPORTED_FORMATS__):
            __playlist__.append(track)
            count = count + 1
    
    return count


def rem_from_playlist(indices):
    '''Removes the playlist item at the specified index'''
    global __playlist__, __current_track_idx__

    for i in range(len(indices) -1, -1, -1):
        index = int(indices[i])
        del __playlist__[index - 1]

        if __current_track_idx__ == index:
            stop()
            __current_track_idx__ = 0
        elif __current_track_idx__ > index:
            __current_track_idx__ = __current_track_idx__ - 1   


def clear_playlist():
    '''Clears all songs from the playlist'''
    __playlist__.clear()


# -----------------------------------------
# Functions - Playback
# -----------------------------------------

def sel_next_track():
    '''Advances the current track index to the next track in the playlist'''
    if len(__playlist__) > 0:
        global __current_track_idx__
        __current_track_idx__ = (__current_track_idx__ + 1) % len(__playlist__)


def sel_prev_track():
    '''Returns the current track index to the previous track in the playlist'''
    if len(__playlist__) > 0:
        global __current_track_idx__
        __current_track_idx__ = (__current_track_idx__ - 1) % len(__playlist__)
        

def play_current():
    '''Plays the current song'''
    if __current_track_idx__ < len(__playlist__):
        play(__playlist__[__current_track_idx__])
    

def play_playlist_no(playlist_no):
    '''Plays the song at the specified index in the playlist'''
    global __current_track_idx__
    __current_track_idx__ = playlist_no - 1
    play_current()


def play_pause():
    '''Toggles between playing and pausing of the current playback'''
    global __playback_state__
    if __playback_state__ is PlaybackState.PLAYING:
        __player__.pause()
        __playback_state__ = PlaybackState.PAUSED
    elif __playback_state__ is PlaybackState.PAUSED:
        __player__.play()
        __playback_state__ = PlaybackState.PLAYING
    else:
        play_current()


def play(audio_file_path):
    '''Begins playback of the specified file'''

    global __player__, __playback_state__

    if __playback_state__ is not PlaybackState.STOPPED:
        stop()

    # Create new player
    __player__ = pyglet.media.Player()
    __player__.push_handlers(on_eos=sel_next_track)
        
    source = pyglet.media.load(audio_file_path)
    __player__.queue(source)
    __player__.play()
    __playback_state__ = PlaybackState.PLAYING


def stop():
    '''Discards the current player'''
    global __player__, __playback_state__
    if __player__ is not None:
        __player__.pause()
        # Discard. Pyglet doesn't support stopping - this is the recommended way of handling it
        __player__ = None
    __playback_state__ = PlaybackState.STOPPED


def seek(timestamp):
    '''Seeks to the provided timestamp'''
    global __player__, __playback_state__
    if __player__ is not None:
        __player__.source.seek(timestamp)

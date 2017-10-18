# Argon Music Player

A terminal-based music player for Unix.
**Note: This is still a work in progress.**

### Commands
#### Quick controls
Pressing these keys at any time will immediately trigger the functionality.
(To be expanded)
```
p | spacebar                                  play/pause the current track
s                                             stop playback of the current track
b                                             select the previous song in playlist
n                                             select the next song in the playlist
```

#### Command line
In order to activate the command line, ":" must be provided as input. A command input field will appear, and the following commands are supported.
(To be expanded)
```
GENERAL
   q  | quit                                   safely exits the application
   h  | help                                   displays information to navigate to the mode:help view
   rf | refresh                               request a full redraw of the screen
   mode         [help | details]              sets the current mode to that specified
   
PLAYLIST
   a | add      filename [filename ...]       adds the specified files to the playlist
   a            -dir                          adds all files in the current directory

   r | remove   idx                           removes the playlist item at the specified index
   r            -all | -a                     clears the current playlist
   
   p | play                                   plays/pauses the current track
   p             idx                          plays the track in the playlist at the specified index
   p             -f | -file    filename       plays the file specified without adding it to the current playlist

   s | stop                                   stops playback of the currently playing track
```

### Dependencies
* **curses** for rendering terminal UI
* **pyglet** for audio support
* **AVbin** (pyglet depency)

### Known Issues
* AVbin throws an exception after playing multiple files
* Some files cannot be played (float exception)
* Playlists that exceed the length of the terminal window's height will crash the application

### To Do (Project Management)
* Organize profect directory into a more "pythonic" structure
* Include requirements file

### To Do (Development)
* UI does not refresh continuously (seek bar / timestamp do not update continuously)
* Playlist scrolling
* Track queueing (current only a single track will play)
* Shuffle / repeat mode
* Browse file directory
* Add files recursively
* Add files in specified directory (only current dir is supported)

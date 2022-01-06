<html>
<div align="center">
<img src="https://marcas-logos.net/wp-content/uploads/2019/11/Spotify-logo.jpg" alt="alt text" width="300" height="150"></img>
</div>
<h1 align="center">@danielaceros
<div align="center">
<a href=https://github.com/danielaceros><img src="https://img.shields.io/static/v1?label=&labelColor=505050&message=@danielaceros&color=%230076D6&style=flat&logo=google-chrome&logoColor=%230076D6" alt="website"/></a>
<img src="https://img.shields.io/github/followers/danielaceros?style=social" alt="Star Badge"/>
<a><img src="https://img.shields.io/github/last-commit/danielaceros/spotipybot" alt="Join Community Badge"/></a>
<a><img src="https://img.shields.io/github/repo-size/danielaceros/spotipybot" />
</div>
</html>

# spotipybot
A BOT who allows you to play with SPOTIFY API, adding some tracks, creating playlist or getting tracked about de songs you are playing in REALTIME.

## Getting Started
Install NECESARY MODULES, if you don't have it and download de .py file called 'spotipybot.py':
```bash
pip install pandas
pip install requests
pip install urllib3
pip install socket
pip install keyboard
pip install spotipy
pip install datetime
pip install plotly
pip install tqdm
```
## Running Code
Run from IDE or from PowerShell or instead Comand Prompt
```bash
python spotipybot.py
python3 spotipybot.py
```
## Auth
You will see an AUTH FLOW WINDOW, then you have to put, (you can get it through Spotify API DEVELOPERS):
* CLIENT ID = Your CLIENT ID ej. '9c9e0o8ef5174g04322ce51se59d6e2b'
* CLIENT SECRET = Your CLIENT SECRET ej. '2g27570068954e63b958e36d9dd3b879'
* USERNAME = Your USERNAME CODE NUMBER or instead the NAME ej. 'danielacero'
* REDIRECT URI = Your REDIRECT given URI ej. 'https://localhost:888/callback'

## Functions
You will see the MAIN WINDOW, then you can chose between
* 1-Get the CURRENT PLAY SONG at REALTIME
* 2-Get RECOMMENDED SONGS and save it as CSV
* 3-Create a PLAYLIST by a NAME given
* 4-Delete a PLAYLIST by a NAME given
* 5-Show all user PLAYLISTS
* 6-Show saved user TRACKS
* 7-Get user's TOP TRACKS
* 8-EXIT
## License
[GPL](https://choosealicense.com/licenses/gpl-3.0/)

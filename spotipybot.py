import pandas as pd
import requests
import urllib3
import socket
import keyboard as k
import spotipy
import spotipy.util as util
import spotify_token as sp
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from requests.api import delete
from spotipy.oauth2 import SpotifyClientCredentials
from time import sleep
from tqdm import tqdm
from statistics import mean
dt = datetime.now().strftime('%Y-%m-%d_%H-%M')




# authentication by 'token'
def token(cid, csecret, user, ruri):
    if os.path.exists(".cache-danielacero"):
        os.remove(".cache-danielacero")
    if not os.path.exists("csv"):
        os.mkdir("csv")
    SPOTIPY_CLIENT_ID = cid
    SPOTIPY_CLIENT_SECRET = csecret
    os.environ['SPOTIPY_CLIENT_ID']= cid # '3c9e0b8ef5174f04994ce51ee59d6e2a'
    os.environ['SPOTIPY_CLIENT_SECRET']= csecret # '3a27770068954e63b058e96d9dd3b879'
    scope = 'user-read-recently-played playlist-modify-public user-top-read user-read-playback-state user-read-private'
    # "http://localhost:8888/callback"
    token = util.prompt_for_user_token(user, scope,
                                    SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,
                                    redirect_uri=ruri)
    sp = spotipy.Spotify(auth=token)
    return sp
# get current playback
def currentplay(sp):
    names = []
    times = []
    ids = []
    ais = []
    popularity = []	
    p = []
    while True:
        if k.is_pressed("esc"):
            break
        else:
            try:
                current_track = sp.current_user_playing_track()
                playing = current_track.get('is_playing')
                if playing == True:
                    state = current_track.get('progress_ms')
                    s = (float(state)/1000)%60
                    m = (float(state)/(1000*60))%60
                    timestamp = current_track.get('timestamp')
                    times.append(datetime.fromtimestamp(int(timestamp)/1000))
                    tracks = current_track.get('item') 
                    pop = tracks.get('popularity')
                    popularity.append(pop)
                    name = tracks.get('name')
                    names.append(name)
                    id = tracks.get('id')
                    ids.append(id)
                    artist = tracks.get('artists')
                    a = artist[0].get('name')
                    ais.append(a)
                    print(f"[ClientStatus] Playing '{name}' of {a} at {id} on {int(m)}:{format(s, '.2f')}")

                    df = pd.DataFrame({
                        'URI':ids,
                        'Title':names,
                        'Artist':ais,
                        'Popularity':popularity,
                        'Timestamp':times
                    })

                    dfs = df.drop_duplicates(subset="URI").reset_index()
                    x = df.groupby('URI', as_index=False).count()
                    y = x.drop(['URI', 'Title', "Artist", "Popularity"], axis=1)
                    c = y.rename(columns={"Timestamp": "Listened"})
                    merged = pd.merge(dfs, c, left_index=True, right_index=True, how='outer', indicator=False).drop(['index'], axis=1)
                    merged.to_csv(f"csv/listened-{dt}.csv")
                else:
                    print(f"[ClientStatus] Stopped")
                    pass

            except spotipy.exceptions.SpotifyException:
                currentplay(token(cid, csecret, user, ruri))
            except AttributeError:
                pass
            except ValueError:
                pass
            except socket.timeout:
                currentplay(token(cid, csecret, user, ruri))
            except urllib3.exceptions.ReadTimeoutError:
                currentplay(token(cid, csecret, user, ruri))
            except requests.exceptions.ReadTimeout:
                currentplay(token(cid, csecret, user, ruri))

# get recommendations     
def recommended(sp, n):
    try:
        u = sp.current_user_recently_played(limit=5)
        dic = u.get("items")
        uris = []
        urias = []
        for song in dic:
            track = song.get('track')
            uri = track.get('uri')
            artis = track.get('artists')
            ar = artis[0]
            uria = ar.get('id')
            uris.append(uri)
            urias.append(uria)

        df = pd.DataFrame(columns=['URI', 'Title', 'Artist'])

        uriss = []
        nameas = []
        titles = []

        for i in range(0, n):
            print(f"[ClientStatus] Extracting RECOMMENDED SONG {i} out of {n}")
            re = sp.recommendations(seed_artists=None, seed_genres=None, seed_tracks=uris, limit=1, market="ES")
            dics = re.get("tracks")

            d = dics[0].get('artists')
            namea = d[0].get('name')
            nameas.append(namea)
            title = dics[0].get('name')
            titles.append(title)
            ids = dics[0].get('uri')
            uriss.append(ids)
        print(f"[ClientStatus] Extracted!")

        dances = []
        energies = []
        speechs = []
        acoustics = []
        valences = []
        for uri in uriss:
            t = sp.audio_features(uri)
            f = t[0]
            dance = f.get('danceability')
            dances.append(dance)
            energy = f.get('energy')
            energies.append(energy)
            speech = f.get('speechiness')
            speechs.append(speech)
            acoustic = f.get('acousticness')
            acoustics.append(acoustic)
            vale = f.get('valence')
            valences.append(vale)

        df = pd.DataFrame({
            'URI': uriss,
            'Name': nameas,
            'Title':titles,
            'Danceability':dances,
            'Energy':energies,
            'Speech':speechs,
            'Acousticness':acoustics,
            'Valence':valences
        })
        df.to_csv(f'csv/recommended-{dt}.csv')
        print(df)
        print(f"[ClientStatus] Results saved as CSV in 'csv/recommended-{dt}.csv'")
        return df
    except TypeError:
        print("[ClientError] 'N' should be a NUMBER")
# add recomended songs by a CSV['URI'] 
def addrecomendedsongs(sp, df, id):
    try:
        sp.user_playlist_add_tracks(user, id, df['URI'])
    except spotipy.exceptions.SpotifyException:
        print("[ClientError] ID is not valid or DF is not generated")
# delete songs of a playlist
def deleteallsongs(sp, id):
    try:
        items = sp.playlist_items(id)
        itemsp = items.get('items')

        deluris = []
        for item in itemsp:
            us = item.get('track').get('uri')
            deluris.append(us)

        sp.playlist_remove_all_occurrences_of_items(id, deluris, snapshot_id=None)
    except spotipy.exceptions.SpotifyException:
        print("[ClientError] ID is not valid or PLAYLIST is not YOURS")
# create a playlist
def createplaylist(sp, name):
    try:
        playlist = sp.user_playlist_create(user, name)
        nameplay = playlist["name"]
        id = playlist["id"]
        print(f"[ClientStatus] Created PLAYLIST '{nameplay}' at {id}")
        return id
    except spotipy.exceptions.SpotifyException:
        print("[ClientError] Name is NOT VALID")
# delete a playlist
def deleteplaylist(sp, id):
    try:
        playlistd = sp.user_playlist_unfollow(user, id)
        print(f"[ClientStatus] Deleted PLAYLIST {id}")
    except spotipy.exceptions.SpotifyException:
        print("[ClientError] Error deleting USER PLAYLIST")
# show all playlists
def showplaylists(sp):
    try:
        pl = sp.user_playlists(user)
        dis = pl.get('items')
        a = 0
        for i in dis:
            a = a + 1
            items = i.get('name')
            uri = i.get('id')
            print(f"[ClientStatus] [{a}] '{items}' with ID {uri}")
    except spotipy.exceptions.SpotifyException:
        print("[ClientError] Error handling USER'S PLAYLISTS")
# get ID from a playlist by NAME
def findbyname(sp, name):
    try:
        pl = sp.user_playlists(user)
        dis = pl.get('items')
        for i in dis:
            items = i.get('name')
            if name == items:
                uri = i.get('id')
                print(f"[ClientStatus] Founded PLAYLIST '{name}' with ID {uri}")
            else:
                pass
        return uri
    except UnboundLocalError:
        print("[ClientError] Name is not VALID or PLAYLIST is not YOURS")
# get saved tracks
def savedtracks(sp):
    try:
        utracks = sp.current_user_saved_tracks(limit=50)
        dictracks = utracks.get('items')
        i = 0
        for t in dictracks:
            i = i + 1
            name = t.get('track').get('name')
            artist = t.get('track').get('artists')[0].get('name')
            print(f"[ClientStatus] [{i}] '{name}' of {artist}")
    except spotipy.exceptions.SpotifyException:
        print("[ClientError] Error handling USER'S TRACKS")
# get the user's most listened tracks
def usertoptracks(sp):
    utracks = sp.current_user_top_tracks(limit=50)
    dictracks = utracks.get('items')
    i = 0
    for t in dictracks:
        i = i + 1
        name = t.get('name')
        artist = t.get('artists')[0].get('name')
        print(f"[ClientStatus] [{i}] '{name}' of {artist}")
# make a star-graph from a CSV about audio_features()
def graph(df):
    dfs = pd.DataFrame(dict(
        r=[mean(df['Danceability']), mean(df['Energy']), mean(df['Speech']), mean(df['Acousticness']), mean(df['Valence'])],
        theta=['Danceability','Energy','Speechiness',
            'Acousticness', 'Valence']))
    fig = px.line_polar(dfs, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself')
    path = f"images/starplot-{dt}.jpeg"
    fig.write_image(path)
# GUI of auth
def authgui():
    print("""

 ███████╗██████╗  ██████╗ ████████╗██╗██████╗ ██╗   ██╗██████╗  ██████╗ ████████╗
 ██╔════╝██╔══██╗██╔═══██╗╚══██╔══╝██║██╔══██╗╚██╗ ██╔╝██╔══██╗██╔═══██╗╚══██╔══╝
 ███████╗██████╔╝██║   ██║   ██║   ██║██████╔╝ ╚████╔╝ ██████╔╝██║   ██║   ██║   
 ╚════██║██╔═══╝ ██║   ██║   ██║   ██║██╔═══╝   ╚██╔╝  ██╔══██╗██║   ██║   ██║   
 ███████║██║     ╚██████╔╝   ██║   ██║██║        ██║   ██████╔╝╚██████╔╝   ██║   
 ╚══════╝╚═╝      ╚═════╝    ╚═╝   ╚═╝╚═╝        ╚═╝   ╚═════╝  ╚═════╝    ╚═╝   
                                                                                
                                                                                                                                                                                                    
 """)
    global cid
#     cid = input("""
#  [ClientInput] Enter your CLIENT ID
#  > """)
    global csecret
#     csecret = input("""
#  [ClientInput] Enter your CLIENT SECRET
#  > """)
    global user
#     user = input("""
#  [ClientInput] Enter your USERNAME
#  > """)
    global ruri
#     ruri = input("""
#  [ClientInput] Enter your REDIRECT URL
#  > """)
    cid = "3c9e0b8ef5174f04994ce51ee59d6e2a"
    csecret = "3a27770068954e63b058e96d9dd3b879"
    user = "danielacero"
    ruri = "http://localhost:8888/callback"
    try:
        print("[ClientOAuth] Trying to AUTHENTICATE...")
        for i in tqdm(range(100)):
            sleep(0.001)
        token(cid, csecret, user, ruri)
        print("[ClientOAuth] AUTHENTICATED")
    except (spotipy.exceptions.SpotifyException, spotipy.oauth2.SpotifyOauthError) as e:
        print("[ClientOAuth] Credentials are INCORRECT or NOT VALID")
        exit()
# GUI of main
def gui(cid, csecret, user, ruri):
    menu = int(input("""

 ███████╗██████╗  ██████╗ ████████╗██╗██████╗ ██╗   ██╗██████╗  ██████╗ ████████╗
 ██╔════╝██╔══██╗██╔═══██╗╚══██╔══╝██║██╔══██╗╚██╗ ██╔╝██╔══██╗██╔═══██╗╚══██╔══╝
 ███████╗██████╔╝██║   ██║   ██║   ██║██████╔╝ ╚████╔╝ ██████╔╝██║   ██║   ██║   
 ╚════██║██╔═══╝ ██║   ██║   ██║   ██║██╔═══╝   ╚██╔╝  ██╔══██╗██║   ██║   ██║   
 ███████║██║     ╚██████╔╝   ██║   ██║██║        ██║   ██████╔╝╚██████╔╝   ██║   
 ╚══════╝╚═╝      ╚═════╝    ╚═╝   ╚═╝╚═╝        ╚═╝   ╚═════╝  ╚═════╝    ╚═╝   
                                                                                
                                                                                                                                                                                                         
 1-CURRENT PLAY
 2-RECOMMENDED SONGS
 3-CREATE PLAYLIST
 4-DELETE PLAYLIST
 5-SHOW PLAYLISTS
 6-SAVED TRACKS
 7-TOP TRACKS
 8-EXIT

 > """))

    if menu == 1:
        print("[ClientStart] Starting SCRAPPING PLAYBACK, saving as CSV, press ESC to ABORT")
        for i in tqdm(range(200)):
            sleep(0.001)
        while True:
            currentplay(token(cid, csecret, user, ruri))
            gui(cid, csecret, user, ruri)
    elif menu == 2:
        print("[ClientStart] Starting RECOMENDATIONS, will be saved as CSV, press Ctrl + C to EXIT")
        for i in tqdm(range(200)):
            sleep(0.001)
        ninput = int(input("""
 [ClientInput] Enter the NUMBER of SONGS you WANT
 > """))
        recommended(token(cid, csecret, user, ruri), ninput)
        gui(cid, csecret, user, ruri)
    elif menu == 3:
        print("[ClientStart] Starting CREATING PLAYLISTS, press Ctrl + C to EXIT")
        for i in tqdm(range(200)):
            sleep(0.001)
        nameinput = input("""
 [ClientInput] Enter the NAME of the PLAYLIST you WANT to CREATE
 > """)
        createplaylist(token(cid, csecret, user, ruri), nameinput)
        gui(cid, csecret, user, ruri)
    elif menu == 4:
        print("[ClientStart] Starting DELETING PLAYLISTS, press Ctrl + C to EXIT")
        for i in tqdm(range(200)):
            sleep(0.001)
        nainput = input("""
    [ClientInput] Enter the NAME of the PLAYLIST you WANT to DELETE
    > """)
        deleteplaylist(token(cid, csecret, user, ruri), findbyname(token(cid, csecret, user, ruri), nainput))
        gui(cid, csecret, user, ruri)
    elif menu == 5:
        print("[ClientStart] Starting SHOWING PLAYLISTS, FETCHING DATA, press Ctrl + C to EXIT")
        for i in tqdm(range(200)):
            sleep(0.001)
        showplaylists(token(cid, csecret, user, ruri))
        gui(cid, csecret, user, ruri)
    elif menu == 6:
        print("[ClientStart] Starting SAVED TRACKS, FETCHING DATA, press Ctrl + C to EXIT")
        for i in tqdm(range(200)):
            sleep(0.001)
        savedtracks(token(cid, csecret, user, ruri))
        gui(cid, csecret, user, ruri)
    elif menu == 7:
        print("[ClientStart] Starting USER'S TOP TRACKS, press Ctrl + C to EXIT")
        for i in tqdm(range(200)):
            sleep(0.001)
        usertoptracks(token(cid, csecret, user, ruri))
        gui(cid, csecret, user, ruri)
    elif menu == 8:
        print("[ClientStatus] Exiting...")
        exit()
    else:
        print("[ClientError] INPUT is not VALID")
        gui(cid, csecret, user, ruri)

# starting stuff
if __name__ == '__main__':
    authgui()
    gui(cid, csecret, user, ruri)

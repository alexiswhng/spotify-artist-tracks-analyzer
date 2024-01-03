from io import BytesIO
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


#Spotify API Authentication
client_id = '075102bfd14b4cd6baa68b2db1186ecf'
client_secret = '7ed2f38949bb4821b530515b0507d96c'

client_credentials_manager = SpotifyClientCredentials(client_id = client_id, 
                                                      client_secret = client_secret)

sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

#Streamlit App
st.title("Spotify Artist Analyzer")
artist_name = st.sidebar.text_input("Enter Artist Name:") #user input

#retrieve data from Spotify API
if artist_name:
    results = sp.search(q='artist:' + artist_name, type='artist')
    if results:
        artist_id = results['artists']['items']
    else:
        st.write("No artists found with that name.")
        artist_id = None
else:
    artist_id = None

if artist_id:
    name = artist_id[0]['name']
    uri = artist_id[0]['uri']
    image_url = artist_id[0]['images'][0]['url']
    r = requests.get(image_url)

    top_tracks = sp.artist_top_tracks(uri)

    track_names = [track['name'] for track in top_tracks['tracks']]
    track_artists = [", ".join([artist["name"] for artist in track["artists"]]) for track in top_tracks['tracks']]
    track_album = [track['album']['name'] for track in top_tracks['tracks']]
    track_duration = [track['duration_ms'] for track in top_tracks['tracks']]
    track_popularity = [track['popularity'] for track in top_tracks['tracks']]
    track_release_date = [track['album']['release_date'] for track in top_tracks['tracks']]
    track_audio = [track['external_urls']['spotify'] for track in top_tracks['tracks']]

# display the artist data in a table
    st.image(BytesIO(r.content), width = 200)
    st.write(f"## {name}")
    st.write()
    st.write("#### Top 10 Songs")

    for i in range(len(top_tracks['tracks'])):
        # url = top_tracks['external_urls']['spotify']
        st.write(f"**Track:** {track_names[i]}")
        st.write(f"**Artists:** {track_artists[i]}")
        st.write(f"**Release Date:** {track_release_date[i]}")
        st.write(f"**Track Album:** {track_album[i]}")
        st.write(f"**Track Duration:** {track_duration[i]} ms")
        st.write(f"**Track Popularity:** {track_popularity[i]}")
        st.write(f"**Audio:** {track_audio[i]} ")
        st.write("Album Cover")
        st.write("--")

# create a dataframe from the playlist data
    data = {"Name": track_names, "Artist": track_artists, "Album": track_album, "Release Date": track_release_date, "Popularity": track_popularity, "Duration (ms)": track_duration}
    df = pd.DataFrame(data)

# display a histogram of track popularity
    fig_popularity = px.histogram(df, x="Popularity", nbins=20, title="Track Popularity Distribution")
    st.plotly_chart(fig_popularity)

    
# add a dropdown menu for bivariate analysis
    st.write("#### Bivariate Analysis")
    x_axis = st.selectbox("Select a variable for the x-axis:", ["Popularity", "Duration (ms)"])
    y_axis = st.selectbox("Select a variable for the y-axis:", ["Popularity", "Duration (ms)"])
    fig_bivariate = px.scatter(df, x=x_axis, y=y_axis, title=f"{x_axis} vs. {y_axis}")
    st.plotly_chart(fig_bivariate)

# add a dropdown menu for multivariate analysis
    st.write("#### Multivariate Analysis")
    color_by = st.selectbox("Select a variable to color by:", ["Artist", "Album", "Release Date"])
    size_by = st.selectbox("Select a variable to size by:", ["Popularity", "Duration (ms)"])
    fig_multivariate = px.scatter(df, x="Duration (ms)", y="Popularity", color=color_by, size=size_by, hover_name="Name", title="Duration vs. Popularity Colored by Artist")
    st.plotly_chart(fig_multivariate)

# add a summary of the playlist data
    st.write("")
    st.write("### Playlist Summary")
    st.write(f"**Most popular track:** {df.iloc[df['Popularity'].idxmax()]['Name']} by {df.iloc[df['Popularity'].idxmax()]['Artist']} ({df['Popularity'].max()} popularity)")
    st.write(f"**Least popular track:** {df.iloc[df['Popularity'].idxmin()]['Name']} by {df.iloc[df['Popularity'].idxmin()]['Artist']} ({df['Popularity'].min()} popularity)")

# display a bar chart of the top 10 most popular artists in the playlist
    st.write("#### Top 10 Artists")
    st.write("The bar chart below shows the top 10 most popular artists in the playlist.")
    top_artists = df.groupby("Artist").mean().sort_values("Popularity", ascending=False).head(10)
    fig_top_artists = px.bar(top_artists, x=top_artists.index, y="Popularity", title="Top 10 Artists")
    st.plotly_chart(fig_top_artists)    

# display a bar chart of the top 10 most popular songs in the playlist
    st.write("#### Top 10 Songs")
    st.write("The bar chart below shows the top 10 most popular songs in the playlist.")
    top_artistss = df.groupby("Name").mean().sort_values("Popularity", ascending=False).head(10)
    fig_top_artistss = px.bar(top_artistss, x=top_artistss.index, y="Popularity", title="Top 10 Songs")
    st.plotly_chart(fig_top_artistss)


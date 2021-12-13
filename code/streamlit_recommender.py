import pandas as pd
import numpy as np
import streamlit as st
import ast
import os

dir_path = os.getcwd().replace('\\','/')

games = pd.concat([pd.read_csv(dir_path+'/data/steam_games_cleaned_1.csv'), pd.read_csv(dir_path+'/data/steam_games_cleaned_2.csv'), pd.read_csv(dir_path+'/data/steam_games_cleaned_3.csv')], axis=0).set_index('appid')
search_keys = pd.read_csv(dir_path+'/data/search_keys.csv').set_index('name')
closest_games = pd.read_csv(dir_path+'/data/top100_simils.csv').set_index('Unnamed: 0')

def get_games(game):
    return ast.literal_eval(closest_games.loc[search_keys.loc[game]].values[0][0])

st.title('Recommend Me a Game on Steam')

page = st.sidebar.selectbox('Select a Page', ('Seach Games', 'Make a Recommendation'))

if page == 'Search Games':
    st.write('Search games by genre, developer, tags and more!')
    
if page == 'Make a Recommendation':
    st.write('Search for games that are similar on Steam')
    search = st.text_input('Search for a game', value='Beat Hazard').lower()
    search_titles = list(search_keys[search_keys.index.str.contains(search)].index)
    game_titles = list(games.loc[search_keys.loc[search_titles]['appid']]['name'].values)
    st.write(f'Titles that match your search: {" ,".join(game_titles)}')
    if st.button('Check for similar games!'):
        results = get_games(search)
        search_range = 10
        st.dataframe(games.loc[results, ['name', 'developer', 'price']][ : search_range].set_index('name'))
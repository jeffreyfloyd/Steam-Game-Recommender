import pandas as pd
import numpy as np
import streamlit as st
import ast
import os
import requests

dir_path = os.getcwd().replace('\\','/')

games = pd.concat([pd.read_csv(dir_path+'/data/steam_games_cleaned_1.csv'), pd.read_csv(dir_path+'/data/steam_games_cleaned_2.csv'), pd.read_csv(dir_path+'/data/steam_games_cleaned_3.csv')], axis=0).set_index('appid')
search_keys = pd.read_csv(dir_path+'/data/search_keys.csv').set_index('name')
closest_games = pd.read_csv(dir_path+'/data/top100_simils.csv').set_index('Unnamed: 0')
output_columns = ['name', 'developer', 'genre', 'tags', 'languages', 'pos_rating_pct', 'owners','price']

st.set_page_config(page_title = 'Steam Game Recommender', layout = 'wide')


def get_games(game):
    skv = search_keys.loc[game]
    if len(skv) > 1:
        skv = skv.values[0]
    return ast.literal_eval(closest_games.loc[skv].values[0][0])


def generate_results_table(search_title, tag_filters = [], search_range = 20):
    
    st.title(f'Titles most similar to {search_title}')
    results = get_games(search_title.lower())
    results_df = games.loc[results]
    
    if len(tag_filters) > 0:
        for tag in tag_filters:
            results_df = results_df[results_df[tag] > 0]
    
    results_df['name'] = [f'<a href = https://store.steampowered.com/app/{results[y]}>{games.loc[results[y], "name"]}</a>' for y in range(len(results_df))]
    results_df['price'] = [f'${price}' for price in results_df['price']]
    results_df['pos_rating_pct'] = (results_df['pos_rating_pct']*100).astype('int32')
    results_df = results_df.loc[ : , output_columns].iloc[:min(len(results_df), search_range)].set_index('name')
    results_df.index.name = None
    results_df = results_df.to_html(escape=False)
    results_df = results_df.replace('<th></th>','<th>name</th>').replace('<tr style="text-align: right;">', '<tr style="text-align: left;">').replace('pos_rating_pct','average rating /100')
    
    st.write(results_df, unsafe_allow_html=True)

def generate_game_info(game_title):
    search_key_values = search_keys.loc[game_title.lower()].values
    if len(search_key_values) > 1:
        search_key_values = search_key_values[0]
                     
    st.write(f'More Details on {game_title}:')
    info_columns = st.columns(len(output_columns)+1)
                    
    res = requests.get(f'http://store.steampowered.com/api/appdetails?appids={search_key_values[0]}')
    if res.status_code == 200:
        try:
            img_link = res.json()[f'{search_key_values[0]}']['data']['screenshots'][0]['path_thumbnail']
            info_columns[0].image(img_link)
        except:
            info_columns[0].write('Thumbnail not available')
    else:
        info_columns[0].write('Thumbnail not available')
    
    for x in range(len(output_columns)):
        if output_columns[x] != 'pos_rating_pct':
            info_columns[x+1].write(f'{output_columns[x]}'.title())
        else:
            info_columns[x+1].write('Average Rating /100')
            
        if output_columns[x] == 'name':
            info_columns[x+1].write(f'[{games.loc[search_key_values, output_columns[x]].values[0]}](https://store.steampowered.com/app/{search_keys.loc[game_title.lower()].values[0]})')
        elif output_columns[x] == 'price':
            info_columns[x+1].write(f'${games.loc[search_key_values, output_columns[x]].values[0]}')
        elif output_columns[x] == 'pos_rating_pct':
            info_columns[x+1].write(f'{int(games.loc[search_key_values, output_columns[x]].values[0]*100)}')
        else:
            info_columns[x+1].write(f'{games.loc[search_key_values, output_columns[x]].values[0]}')


st.title('Search for Games on Steam')
search = st.text_input('Search for a game', value='Beat Hazard').lower()

filters = []
if st.checkbox('Filter by Tags?'):
    popular_tags = list(games.loc[:,'1980s':'e-sports'].sum().sort_values(ascending=False).index)
    tag_filter_count = st.slider('Choose number of tags to display (listed in order of how commonly they are used)', min_value=12, max_value = len(popular_tags))
    check_cols = st.columns(6)
    for box in range(tag_filter_count):
        if check_cols[box%6].checkbox(popular_tags[box]):
            filters.append(popular_tags[box])
else:
    filters = []
            
search_titles = list(search_keys[search_keys.index.str.contains(search)].index)
    
if len(search_titles) < 1:
    st.write('Unable to find any game titles like that one. Try a different search!')
else:
    game_titles = list(set(list(games.loc[search_keys.loc[search_titles]['appid']]['name'].values)))
    game_titles.sort()
        
    st.write(f'Titles names that are similar to your search:')
    choice_cols = st.columns(min(10, len(game_titles)))
        
    for i in range(len(game_titles)):
        if choice_cols[i%10].button(f'{game_titles[i]}'):
            generate_game_info(game_titles[i])
            generate_results_table(game_titles[i], filters)
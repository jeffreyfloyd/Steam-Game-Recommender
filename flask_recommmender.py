from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import ast
import os
import requests

dir_path = os.getcwd().replace('\\','/')

games = pd.concat([pd.read_csv(dir_path+'/data/steam_games_cleaned_1.csv'), pd.read_csv(dir_path+'/data/steam_games_cleaned_2.csv'), pd.read_csv(dir_path+'/data/steam_games_cleaned_3.csv')], axis=0).set_index('appid')
search_keys = pd.read_csv(dir_path+'/data/search_keys.csv').set_index('name')
closest_games = pd.read_csv(dir_path+'/data/top100_simils.csv').set_index('Unnamed: 0')
output_columns = ['name', 'developer', 'genre', 'tags', 'languages', 'pos_rating_pct', 'owners','price']

def get_games(game):
    skv = search_keys.loc[game]
    if len(skv) > 1:
        skv = skv.values[0]
    return ast.literal_eval(closest_games.loc[skv].values[0][0])

def generate_results_table(search_title, game_filts = [], search_range = 20):
    
    results = get_games(search_title.lower())
    results_df = games.loc[results]
    
    results_df['name'] = [f'<a href = https://store.steampowered.com/app/{results[y]}>{games.loc[results[y], "name"]}</a>' for y in range(len(results_df))]
    results_df['price'] = [f'${price}' for price in results_df['price']]
    results_df['pos_rating_pct'] = (results_df['pos_rating_pct']*100).astype('int32')
    results_df = results_df.loc[ : , output_columns].iloc[:min(len(results_df), search_range)].set_index('name')
    results_df.index.name = None
    results_df = results_df.to_html(escape=False)
    results_df = results_df.replace('<th></th>','<th>name</th>').replace('<tr style="text-align: right;">', '<tr style="text-align: left;">').replace('pos_rating_pct','average rating /100')

    return results_df

def generate_game_info(game_title):
    search_key_values = search_keys.loc[game_title.lower()].values

    if len(search_key_values) > 1:
        search_key_values = search_key_values[0]
    
    game_info = games.loc[search_key_values, output_columns]
    game_info['name'] = f'<a href = https://store.steampowered.com/app/{search_key_values[0]}>{games.loc[search_key_values[0], "name"]}</a>'
    game_info.loc[search_key_values[0],'pos_rating_pct'] = (game_info.loc[search_key_values[0],'pos_rating_pct']*100).astype(int)
    game_info.loc[search_key_values[0],'price'] = f"${game_info.loc[search_key_values[0],'price']}"
    game_info.index.name = None
    game_info = game_info.to_html(escape=False)
    game_info = game_info.replace('<th></th>','').replace(f'<th>{search_key_values[0]}</th>','').replace('<tr style="text-align: right;">', '<tr style="text-align: left;">').replace('pos_rating_pct','average rating /100')

    return game_info

    # res = requests.get(f'http://store.steampowered.com/api/appdetails?appids={search_key_values[0]}')

    # if res.status_code == 200:
    #     try:
    #         img_link = res.json()[f'{search_key_values[0]}']['data']['screenshots'][0]['path_thumbnail']
    #     except:
    #         img_link = 'Thumbnail not available'
    # else:
    #     img_link = 'Thumbnail not available'
    
    

app = Flask(__name__)

@app.route('/')
def home():
    homepage = '''
    <html>
        <head>
            <title>Steam Game Recommender</title>
            <link rel="stylesheet" href="{{ url_for('style', filename='css/main.css') }}">
        </head>

        <body>
            <h1>Steam Game Recommendation Engine</h1>
            <p>How many times have you used the search function on the Steam store and found that many of its suggestions have little to no similarity to the game you're insterested in? <br>This app is designed to help you find more of the games you didn't know you wanted to play. Search your favorite games in your Steam library so you can find more of what you love!</p>
            <p></p>
            <p><a href="/search-by-title">Search for similar games by title</p>
            <p><a href="/search-by-tag">Search games by tag</p>
        </body>
    </html>
    '''
    return homepage

@app.route('/search-by-title')
def title_search():
    
    template = '''
    <html>
        <head>
            <title>Search Games by Title</title>
        </head>

        <body style>
            <form action="/submit">
                <h1>Search Games by Title Name</h1>
                <p>
                    <label for="game_title">Please Enter a Game Title</label>
                    <input type="string" name="game_title">
                </p>
                
                <p><button type="submit">Submit</button></p>
            </form>
        </body>

    </html>'''
    return template

@app.route('/search-by-tag')
def tag_search():
    return 'under construction'

@app.route('/submit')
def matching_titles():

    user_input = request.args
    search = user_input['game_title'].lower()
    search_titles = list(search_keys[search_keys.index.str.contains(search)].index)

    if len(search_titles) < 30:
        matches = ''
        for title in search_titles:
            matches += f'<p><a href="/results?title={title}">{title}</p>'
    else:
        matches = '<table>'
        for title_ind in range(len(search_titles)//3):
            matches += '<tr>'
            for col_ind in range(3):
                matches += f'<td><a href="/results?title={search_titles[title_ind*3+col_ind]}">{search_titles[title_ind*3+col_ind]}</td>'
            matches += '</tr>'
        if len(search_titles) % 3 > 0:
            if len(search_titles) % 3 == 1:
                matches += f'<tr><td><a href="/results?title={search_titles[-1]}">{search_titles[-1]}</td></tr>'
            else:
                matches += f'<tr><td><a href="/results?title={search_titles[-2]}">{search_titles[-2]}</td><td><a href="/results?title={search_titles[-1]}">{search_titles[-1]}</td></tr>'
        matches += '</table>'

    form_format = f'''
    <html>
        <head>
            <title>Matching Titles</title>
        </head>

        <body>
            <form action="/results">
                <h1>Games Titles Similar to Your Search</h1>
                {matches}

            </form>
        </body>

    </html>
    '''
    return form_format

@app.route('/results')
def results():
    user_input = request.args
    game_info = generate_game_info(user_input['title'])
    results_table = generate_results_table(user_input['title'])

    results_page = f'''
    <html>
        <h1>More information about {user_input['title']}</h1>
        {game_info}

        <h1>Games similar to {user_input['title']}</h1>
        {results_table}
    </html>
    '''
    return results_page
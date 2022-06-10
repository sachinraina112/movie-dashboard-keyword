import json

import pandas as pd
import plotly.colors
import plotly.graph_objs as go
import requests

from .AppConfig import api_config
from .Security import Security


def get_response(keyword, page='1'):
    sec = Security()
    key = api_config['key']
    api_key = sec.decrypt(sec.string_to_bytes(key))

    url = "https://api.themoviedb.org/3/search/movie?api_key=" + api_key + "&adult=false&query=" + keyword + "&page=" + page
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    res_json = json.loads(response.text)
    return res_json


def get_number_of_pages(keyword):
    content = get_response(keyword)
    pages = content['total_pages']
    return pages


def get_all_movies(keyword, pages):
    res_list = []
    if pages < 5:
        pages = pages
    else:
        pages = 5
    final_df = pd.DataFrame()
    cols_reqd = ['id', 'genre_ids', 'original_language', 'title', 'popularity', 'release_date', 'vote_average',
                 'vote_count']
    for i in range(1, pages):
        trial = get_response(keyword, str(i))
        df = pd.DataFrame()
        for movs in range(len(trial['results'])):
            mov_dict = trial['results'][movs]
            mov_df = pd.DataFrame([mov_dict], columns=mov_dict.keys())
            df = df.append(mov_df)
        final_df = final_df.append(df)
        final_df = final_df.reset_index(drop=True)
        final_df = final_df.drop_duplicates(subset='title')
        final_df = final_df[cols_reqd]
    return final_df


def genre_map(x, genre_df):
    list_of_genres = []
    for item in x:
        val = genre_df[genre_df['genre_ids'] == item]['genre'].item()
        list_of_genres.append(val)
    x = list_of_genres
    return x


def match_genres(movie_df):
    sec = Security()
    key = api_config['key']
    api_key = sec.decrypt(sec.string_to_bytes(key))
    url = "https://api.themoviedb.org/3/genre/movie/list?api_key=" + api_key

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    genre_res = json.loads(response.text)
    genre_df = pd.DataFrame(genre_res['genres'])
    genre_df.rename(columns={'id': 'genre_ids', 'name': 'genre'}, inplace=True)
    movie_df['genre'] = movie_df['genre_ids'].apply(lambda x: genre_map(x, genre_df))
    return movie_df


def get_result_df(keyword):
    tot_pages = get_number_of_pages(keyword)
    movie_df = get_all_movies(keyword, tot_pages)
    df_with_genre = match_genres(movie_df)
    return df_with_genre


def return_figures(keyword):
    """Creates four plotly visualizations using the The Movie DataBase API

    # Example of the The Movie DataBase API endpoint:
    # Fetch relevant movies for a keyword query input
    #

      Args:
          keyword (string): keyword for fetching relevant movies

      Returns:
          list (dict): list containing the four plotly visualizations

    """

    # when the keyword variable is empty, use the default keyword 'hero'
    if not bool(keyword):
        keyword = 'hero'

    result_df = get_result_df(keyword)

    # first chart gives top five relevant movies wrt popularity
    for_plot_1 = result_df.sort_values(['popularity'], ascending=False)[:5]
    x_val = for_plot_1['title'].values.tolist()
    y_val = for_plot_1['popularity'].values.tolist()

    graph_one = []
    graph_one.append(
        go.Bar(
            x=x_val,
            y=y_val,
        )
    )

    layout_one = dict(title='Top Five Relevant Movies for the given keyword wrt popularity',
                      xaxis=dict(title='Movie', automargin=True),
                      yaxis=dict(title='popularity'),
                      )
    # second chart plots Top Five Relevant Movies for the given keyword wrt average vote rating
    for_plot_2 = result_df.sort_values(['vote_average'], ascending=False)[:5]
    x_val_2 = for_plot_2['title'].values.tolist()
    y_val_2 = for_plot_2['vote_average'].values.tolist()

    graph_two = []
    graph_two.append(
        go.Bar(
            x=x_val_2,
            y=y_val_2,
        )

    )
    layout_two = dict(title='Top Five Relevant Movies for the given keyword wrt <br> average vote rating',
                      xaxis=dict(title='Movie', automargin=True ),
                      yaxis=dict(title='Average Vote Rating'),
                      )

    # third chart plots Top Five Relevant Movies for the given keyword wrt vote count

    for_plot_3 = result_df.sort_values(['vote_count'], ascending=False)[:5]
    x_val_3 = for_plot_3['title'].values.tolist()
    y_val_3 = for_plot_3['vote_count'].values.tolist()

    graph_three = []
    graph_three.append(
        go.Bar(
            x=x_val_3,
            y=y_val_3,
        )

    )
    layout_three = dict(title='Top Five Relevant Movies for the given keyword wrt vote count',
                        xaxis=dict(title='Movie',automargin=True ),
                        yaxis=dict(title='Vote Count'),
                        )

    # fourth chart shows Scatter plot of popularity vs average vote rating with vote count as bubble size
    for_plot_4 = result_df.copy(deep=True)
    x_val_4 = for_plot_4['popularity'].values.tolist()
    y_val_4 = for_plot_4['vote_average'].values.tolist()
    z_val_4 = for_plot_4['vote_count'].values.tolist()

    graph_four = []
    graph_four.append(
        go.Scatter(
            x=x_val_4,
            y=y_val_4,
            mode='markers',
            marker=dict(color='hsv(0,100%,100%)', size=[i/100 for i in z_val_4])

        )

    )
    layout_four = dict(title='Scatter plot of popularity vs average vote rating <br> with vote count as bubble size',
                       xaxis=dict(title='Popularity', ),
                       yaxis=dict(title='Average Vote Rating'),
                       )
    plotly_default_colors = plotly.colors.DEFAULT_PLOTLY_COLORS

    # append all charts
    figures = []
    figures.append(dict(data=graph_one, layout=layout_one))
    figures.append(dict(data=graph_two, layout=layout_two))
    figures.append(dict(data=graph_three, layout=layout_three))
    figures.append(dict(data=graph_four, layout=layout_four))

    return figures

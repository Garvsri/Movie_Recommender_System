import streamlit as st
import pickle
import pandas as pd
import requests
API_KEY = "dc6d44583556df23bd932ce476175a91"

import requests

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {
        "api_key": API_KEY
    }
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        PLACEHOLDER_POSTER = "https://via.placeholder.com/500x750?text=No+Poster"

        poster_path = data.get("poster_path")
        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path
        return PLACEHOLDER_POSTER
        

    except requests.exceptions.RequestException as e:
        print("TMDB request failed:", e)
        return None

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        key=lambda x: x[1],
        reverse=True
    )[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in movies_list:
        movie_row = movies.iloc[i[0]]
        movie_id = movie_row['id']

        poster = fetch_poster(movie_id)
        if poster is not None:
            recommended_movies.append(movie_row.title)
            recommended_movies_posters.append(poster)

        # ✅ stop when we have 5 valid posters
        if len(recommended_movies) == 5:
            break

    return recommended_movies, recommended_movies_posters

movies_dict = pickle.load(open("movies_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open("similarity.pkl","rb"))

st.title("Movie Recommender System")

selected_movie = st.selectbox(
    "Select a movie",
    movies['title'].values
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie)

    cols = st.columns(len(names))

    for i in range(len(names)):
     with cols[i]:
        st.text(names[i])
        st.image(posters[i])
import streamlit as st
import pickle
import pandas as pd
import requests
import ast
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

        if len(recommended_movies) == 5:
            break

    return recommended_movies, recommended_movies_posters

@st.cache_data
def load_data_and_similarity():
    movies = pd.read_csv("tmdb_5000_movies.csv")
    credits = pd.read_csv("tmdb_5000_credits.csv")

    movies = movies.merge(credits, on="title")
    movies = movies[["movie_id", "title", "overview", "genres", "keywords", "cast", "crew"]]
    movies.dropna(inplace=True)

    def convert(obj):
        return [i["name"] for i in ast.literal_eval(obj)]

    def convert_cast(obj):
        return [i["name"] for i in ast.literal_eval(obj)[:3]]

    def fetch_director(obj):
        for i in ast.literal_eval(obj):
            if i["job"] == "Director":
                return [i["name"]]
        return []

    movies["genres"] = movies["genres"].apply(convert)
    movies["keywords"] = movies["keywords"].apply(convert)
    movies["cast"] = movies["cast"].apply(convert_cast)
    movies["crew"] = movies["crew"].apply(fetch_director)

    movies["overview"] = movies["overview"].apply(lambda x: x.split())
    movies["tags"] = movies["overview"] + movies["genres"] + movies["keywords"] + movies["cast"] + movies["crew"]
    movies["tags"] = movies["tags"].apply(lambda x: " ".join(x).lower())

    new_df = movies[["movie_id", "title", "tags"]]

    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    cv = CountVectorizer(max_features=5000, stop_words="english")
    vectors = cv.fit_transform(new_df["tags"]).toarray()
    similarity = cosine_similarity(vectors)

    return new_df, similarity


movies, similarity = load_data_and_similarity()

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
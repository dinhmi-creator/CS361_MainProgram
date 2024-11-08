from flask import Flask, jsonify
import requests
import os
from dotenv import load_dotenv
from details_microservice.cache import get_from_cache, set_in_cache


# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# TMDB API Key
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

def fetch_movie_from_tmdb(movie_id):
    """Fetch movie details from TMDB API."""
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

@app.route('/movie/<movie_id>', methods=['GET'])
def get_movie_details(movie_id):
    """Fetch movie details with Redis caching."""
    # Check Redis cache
    cached_data = get_from_cache(movie_id)
    if cached_data:
        return jsonify(cached_data), 200

    # Fetch from TMDB if not in cache
    movie_data = fetch_movie_from_tmdb(movie_id)
    if movie_data:
        # Store in Redis cache
        set_in_cache(movie_id, movie_data)
        return jsonify(movie_data), 200

    return jsonify({"error": "Movie not found"}), 404

if __name__ == '__main__':
    app.run(port=5001, debug=True)

from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv
import os
import requests
from datetime import timedelta

from details_microservice.app import get_movie_details

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')  # Ensure this is set in your .env file
app.permanent_session_lifetime = timedelta(minutes=30)  # Set session timeout

# Temporary mock database of users with specified username and password
users_db = {
    "Bob7Bobby": {"password": "HelloWorld123!", "email": "bob7bobby@example.com"}
}

def fetch_popular_movies():
    """Fetch popular movies from the TMDB API."""
    TMDB_API_KEY = os.getenv("TMDB_API_KEY")
    url = f'https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page=1'
    response = requests.get(url)
    if response.status_code == 200:
        movies_data = response.json().get('results', [])
        movies = [
            {
                "id": movie['id'],
                "title": movie['title'],
                "year": movie.get('release_date', "Unknown")[:4],
                "rating": movie.get('vote_average', "N/A"),
                "description": movie.get('overview', "No description available.")
            }
            for movie in movies_data
        ]
        return movies
    else:
        flash("Failed to fetch popular movies from TMDB")
        return []

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_db.get(username)

        if user and user['password'] == password:
            session['username'] = username
            session.permanent = True
            flash("Login successful!")
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password.")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/home')
def home():
    if 'username' in session:
        return render_template('home.html')
    else:
        flash("Please log in to access the website.")
        return redirect(url_for('login'))

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        if username in users_db:
            flash("Username already exists. Please choose a different username.")
            return redirect(url_for('create_account'))
        
        users_db[username] = {"password": password, "email": email}
        flash("Account created successfully! Please log in.")
        return redirect(url_for('login'))

    return render_template('create_account.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.")
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'username' not in session:
        flash("Please log in to view your profile.")
        return redirect(url_for('login'))
    
    user_data = {
        "username": session['username'],
        "email": users_db[session['username']]['email']
    }
    return render_template('profile.html', user=user_data)

@app.route('/popular_movies')
def popular_movies():
    movies = fetch_popular_movies()
    return render_template('popular_movies.html', movies=movies)

@app.route('/movie_details/<int:movie_id>')
def movie_details(movie_id):
    movie = get_movie_details(movie_id)
    if movie:
        return render_template('movie_details.html', movie=movie, movie_id=movie_id)
    else:
        return redirect(url_for('error'))

@app.route('/favorites')
def favorites():
    favorites_list = [
        {"title": "Deadpool", "year": 2016},
        {"title": "Iron Man 3", "year": 2013},
        {"title": "Thor: The Dark World", "year": 2013},
        {"title": "Luca", "year": 2021}
    ]
    return render_template('favorites.html', favorites=favorites_list)

@app.route('/remove_favorite', methods=['POST'])
def remove_favorite():
    movie_title = request.form.get('movie_title')
    flash(f"{movie_title} has been removed from your favorites.")
    return redirect(url_for('favorites'))

@app.route('/rate_movie', methods=['GET', 'POST'])
def rate_movie():
    if request.method == 'POST':
        rating = request.form['rating']
        flash(f"Your rating of {rating} has been submitted.")
        return redirect(url_for('home'))
    return render_template('rate_movie.html')

@app.route('/save_to_favorites', methods=['POST'])
def save_to_favorites():
    movie_title = request.form.get('movie_title', "Unknown Movie")
    flash(f"{movie_title} has been added to your favorites.")
    return redirect(url_for('favorites'))

@app.route('/search_results', methods=['GET', 'POST'])
def search_results():
    results = []
    if request.method == 'POST':
        search_query = request.form['query']
        genre = request.form.get('genre')
        year = request.form.get('year')
        rating = request.form.get('rating')

        # Placeholder: Implement actual filtering logic
        results = [
            {"title": "Luca", "year": "2021", "genre": "Animation", "rating": "8"},
            {"title": "Moana", "year": "2016", "genre": "Animation", "rating": "7"}
        ]
        
        # Filter results based on user inputs (genre, year, rating)
        if genre:
            results = [movie for movie in results if movie.get("genre") == genre]
        if year:
            results = [movie for movie in results if movie.get("year") == year]
        if rating:
            results = [movie for movie in results if int(movie.get("rating")) >= int(rating)]
    
    return render_template('search_results.html', results=results)

@app.route('/help_support')
def help_support():
    return render_template('help_support.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
    if request.method == 'POST':
        message = request.form['message']
        flash("Your message has been sent.")
        return redirect(url_for('home'))
    return render_template('contact_us.html')

@app.route('/error')
def error():
    return render_template('error.html')

if __name__ == '__main__':
    app.run(debug=True)

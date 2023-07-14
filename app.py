from flask import Flask, render_template, request, redirect, url_for
import requests
import sqlalchemy as db
import pandas as pd

app = Flask(__name__)

# Function to query the API
def query_api(author=None, rank=None, lines=None):
    url = 'https://poetrydb.org/random/1'
    params = {}

    if author:
        params['author'] = author
    if rank:
        params['rating'] = rank
    if lines:
        params['lines'] = f'{lines}/'

    response = requests.get(url, params=params)
    data = response.json()

    return data

# Function to fetch ranked poems from the database
def fetch_ranked_poems():
    engine = db.create_engine('sqlite:///RankedAndRead.db')
    query = db.text("SELECT * FROM RankedPoems")
    connection = engine.connect()
    results = connection.execute(query).fetchall()
    connection.close()

    return results

# Home Page - Querying the API and Ranking Poems
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Get form data
        author = request.form.get('author')
        rank = int(request.form.get('rank'))
        lines = request.form.get('lines')

        # Query the API
        results = query_api(author=author, rank=rank, lines=lines)

        if results:
            poem = results[0]  # Get the first/only poem in the response
            line_count = int(poem['linecount'])
            if line_count <= 20:
                # Create a DataFrame from the selected poem
                poem_df = pd.DataFrame({'Title': [poem['title']], 'Author': [poem['author']], 'Linecount': [poem['linecount']], 'Rank': [rank]})

                # Create an engine object
                engine = db.create_engine('sqlite:///RankedAndRead.db')

                # Append the poem to the database table
                poem_df.to_sql('RankedPoems', con=engine, if_exists='append', index=False)

    return render_template('home.html')

# Ranked Poems Page - Revisiting/Updating Poems
@app.route('/ranked-poems', methods=['GET', 'POST'])
def ranked_poems():
    if request.method == 'POST':
        # Get form data
        poem_id = request.form.get('poem_id')
        new_rank = request.form.get('rank')

        # Update rank in the database
        engine = db.create_engine('sqlite:///RankedAndRead.db')
        query = db.text("UPDATE RankedPoems SET Rank = :rank WHERE id = :id")
        connection = engine.connect()
        connection.execute(query, rank=new_rank, id=poem_id)
        connection.close()

    # Fetch ranked poems from the database
    poems = fetch_ranked_poems()

    return render_template('ranked_poems.html', poems=poems)

# About Page - Project Information
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run()

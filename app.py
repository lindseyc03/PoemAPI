from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Function to fetch random poems from the PoetryDB API
def fetch_random_poems(num_poems):
    poems = []

    while len(poems) < num_poems:
        response = requests.get('https://poetrydb.org/random/1')
        data = response.json()
        poem = data[0]

        line_count = int(poem['linecount'])
        if line_count <= 20:
            poems.append(poem)

    return poems

@app.route('/', methods=['GET', 'POST'])
def home():
    poems = []

    if request.method == 'POST':
        try:
            num_poems = int(request.form.get('num_poems', 1))
            poems = fetch_random_poems(num_poems)
        except ValueError:
            pass

    return render_template('home.html', poems=poems)

if __name__ == '__main__':
    app.run(debug=True)

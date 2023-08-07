from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import requests


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///poemshistory.db'  # Change the database URI if needed
app.static_url_path = '/static'  
app.static_folder = 'static' 

db = SQLAlchemy(app)
migrate = Migrate(app, db) 

class Poem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    author = db.Column(db.String(128), nullable=False)
    lines = db.Column(db.Text, nullable=False)
    linecount = db.Column(db.Integer, nullable=True) 

# Move db.create_all() within the app context
with app.app_context():
    db.create_all()

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
            for poem in poems:
                poem_entry = Poem(title=poem['title'], author=poem['author'], lines='\n'.join(poem['lines']), linecount=poem['linecount'])
                db.session.add(poem_entry)
            db.session.commit()
        except ValueError:
            pass

    return render_template('home.html', poems=poems)

@app.route('/poem_history')
def poem_history():
    poems = Poem.query.all()
    return render_template('poem_history.html', poems=poems, history_cleared=False)

@app.route('/clear_history', methods=['POST'])
def clear_history():
    try:
        Poem.query.delete()
        db.session.commit()
        return render_template('poem_history.html', poems=[], history_cleared=True)
    except:
        db.session.rollback()
        return render_template('poem_history.html', poems=[], history_cleared=False)

if __name__ == '__main__':
    app.run(debug=True)

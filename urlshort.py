from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import random
import string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.secret_key = 'your_secret_key'
db = SQLAlchemy(app)

class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(200), nullable=False)
    short_url = db.Column(db.String(6), unique=True, nullable=False)

    def __init__(self, original_url):
        self.original_url = original_url
        self.short_url = self.generate_short_url()

    def generate_short_url(self):
        characters = string.ascii_letters + string.digits
        short_url = ''.join(random.choice(characters) for i in range(6))
        return short_url

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten():
    original_url = request.form['original_url']
    if not original_url.startswith(('http://', 'https://')):
        flash('Please enter a valid URL starting with http:// or https://', 'danger')
        return redirect(url_for('home'))

    existing_url = Url.query.filter_by(original_url=original_url).first()
    if existing_url:
        return render_template('result.html', short_url=existing_url.short_url)

    new_url = Url(original_url)
    db.session.add(new_url)
    db.session.commit()
    
    return render_template('result.html', short_url=new_url.short_url)

@app.route('/<string:short_url>')
def redirect_to_original(short_url):
    url = Url.query.filter_by(short_url=short_url).first()
    if url:
        return redirect(url.original_url)
    else:
        flash('Short URL not found!', 'danger')
        return redirect(url_for('home'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

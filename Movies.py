from flask import Flask, request, render_template, session, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import datetime, os, cgi, hashlib, random

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Movies:Jackson1313@localhost:8889/Movies'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = os.urandom(24)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    releaseyear = db.Column(db.Integer)
    title = db.Column(db.String(120))
    originethno = db.Column(db.String(120))
    director = db.Column(db.String(120))
    cast = db.Column(db.String(120))
    genre = db.Column(db.String(120))
    wikipage = db.Column(db.String(120))
    plot = db.Column(db.String(1200))


    def __init__(self, releaseyear, title, originethno, director, cast, genre, wikipage, plot):
        self.releaseyear = releaseyear
        self.title = title
        self.originethno = originethno
        self.director = director
        self. cast = cast
        self.genre = genre
        self.wikipage = wikipage
        self.plot = plot

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(120))

    def __init__(self, email, password):
        self.email = email
        self.password = password

def make_salt():
    sal = ""
    for elem in range(5):
        num1 = random.randrange(9)
        num2 = str(num1)
        sal += num2
    return sal
    
def make_pw_hash(password):
    hash = hashlib.sha256(str.encode(password)).hexdigest()
    return hash

def check_pw_hash(password, hash):
    hash2 = hash[5:]
    if make_pw_hash(password) == hash2:
        return True
    else:
        return False

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_pw_hash(password, user.password):
            session['email'] = email
            #flash("Logged in")
            return redirect('/movies')
        elif not user:
            flash("User does not exist")
            return redirect('/signup')
        else:
            flash('User password incorrect')
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        if not email or not password or not verify:
            flash("Please fill in all form spaces")
            return redirect('/signup')
        if password != verify:
            flash("Password and Password Verify fields do not match")
            return redirect('/signup')
        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            salt = make_salt()
            hash = make_pw_hash(password)
            password = salt + hash
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            flash("Signed In")
            return redirect('/movies')
        else:
            flash('Duplicate User')
            return redirect('/signup')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/login')

@app.route('/movies', methods=['GET'])
def index2():
    return render_template('index2.html')

@app.route("/list", methods =['GET'])
def index():
    movies = Movie.query.all()
    movielist = []
    for movie in movies:
        relyr = str(movie.releaseyear)
        moviestr = movie.title + ": " + relyr + "/ " + movie.originethno + "/ " + movie.director + "/ " + movie.cast + "/ " + movie.genre + "/ " + movie.wikipage + "/ " + movie.plot
        movielist.append(moviestr)
    movielist.sort()
    return render_template('list.html', movies = movielist)

@app.route("/login", methods =['GET', 'POST'])
def frontpage():
    return render_template('login.html')

@app.route("/add", methods =['GET', 'POST'])
def add():
    if request.method == "GET":
        return render_template('add.html')
    if request.method == "POST":
        error = ""
        movietitle = request.form['title']
        moviereleaseyear = request.form['releaseyear']
        movieoriginethno = request.form['originethno']
        moviedirector = request.form['director']
        moviecast = request.form['cast']
        moviegenre = request.form['genre']
        moviewikipage = request.form['wikipage']
        movieplot = request.form['plot']
        movietitle = cgi.escape(movietitle)
        moviereleaseyear = cgi.escape(moviereleaseyear)
        movieoriginethno = cgi.escape(movieoriginethno)
        moviedirector = cgi.escape(moviedirector)
        moviecast = cgi.escape(moviecast)
        moviegenre = cgi.escape(moviegenre)
        moviewikipage = cgi.escape(moviewikipage)
        movieplot = cgi.escape(movieplot)
        old_movie = Movie.query.filter_by(title=movietitle, releaseyear = moviereleaseyear).first()
        if old_movie or not movietitle or not moviereleaseyear:
            if not moviereleaseyear:
                error = "Please enter a release year, in order to add it."
            if not movietitle:
                error = "Plese enter the movie's title, in order to add it."
            if old_movie:
                error = "That movie is already in the database."
            return render_template('add.html', error = error)
        else:
            new_movie = Movie(moviereleaseyear, movietitle, movieoriginethno, moviedirector, moviecast, moviegenre, moviewikipage, movieplot)
            db.session.add(new_movie)
            db.session.commit()
            return render_template('index2.html')

@app.route("/remove", methods =['GET', 'POST'])
def remove():
    if request.method == "GET":
        return render_template('remove.html')
    if request.method == "POST":
        movietitle = request.form['remtitle']
        movietitle = cgi.escape(movietitle)
        the_movie = Movie.query.filter_by(title = movietitle).first()
        if the_movie:
            db.session.delete(the_movie)
            db.session.commit()
            return render_template('index2.html')
        else:
            error2 = "That movie is not in the database."
            return render_template('index2.html', error2 = error2)

@app.route("/search", methods =['GET', 'POST'])
def search():
    if request.method == "GET":
        return render_template('search.html')
    if request.method == "POST":
        searchterm = request.form['searchterm']
        searchterm = cgi.escape(searchterm)
        searchterm.lower()
        foundmovies = []
        movies = Movie.query.all()
        for movie in movies:
            testtitle = movie.title.lower()
            testreleaseyear = str(movie.releaseyear)
            testoriginethno = movie.originethno.lower()
            testdirector = movie.director.lower()
            testcast = movie.cast.lower()
            testgenre = movie.genre.lower()
            testwikipage = movie.wikipage.lower()
            testplot = movie.plot.lower()
            if searchterm in testtitle or searchterm in testreleaseyear or searchterm in testoriginethno or searchterm in testdirector or searchterm in testcast or searchterm in testgenre or searchterm in testwikipage or searchterm in testplot:
                foundmovies.append(movie)
        if foundmovies:
            movielist = []
            for movie in foundmovies:
                relyr = str(movie.releaseyear)
                moviestr = movie.title + ": " + relyr + "/ " + movie.originethno + "/ " + movie.director + "/ " + movie.cast + "/ " + movie.genre + "/ " + movie.wikipage + "/ " + movie.plot
                movielist.append(moviestr)
            movielist.sort()
            return render_template('search.html', movies = movielist)
        else:
            error = "That text was not found in the database."
            return render_template('search.html', error = error)
        
@app.route("/edit", methods =['GET', 'POST'])
def edit():
    if request.method == "GET":
        return render_template('edit.html', movie = "")
    if request.method == "POST":
        edittitle = request.form['edittitle']
        edittitle = cgi.escape(edittitle)
        movie = Movie.query.filter_by(title = edittitle).first()
        if not movie or not edittitle:
            error = "That movie was not found in the database."
            return render_template('edit.html', error = error)
        else:
            moviereleaseyear = request.form['releaseyear']
            movieoriginethno = request.form['originethno']
            moviedirector = request.form['director']
            moviecast = request.form['cast']
            moviegenre = request.form['genre']
            moviewikipage = request.form['wikipage']
            movieplot = request.form['plot']
            moviereleaseyear = cgi.escape(moviereleaseyear)
            movieoriginethno = cgi.escape(movieoriginethno)
            moviedirector = cgi.escape(moviedirector)
            moviecast = cgi.escape(moviecast)
            moviegenre = cgi.escape(moviegenre)
            moviewikipage = cgi.escape(moviewikipage)
            movieplot = cgi.escape(movieplot)
            movie.releaseyear = moviereleaseyear
            movie.originethno = movieoriginethno
            movie.director = moviedirector
            movie.cast = moviecast
            movie.genre = moviegenre
            movie.wikipage = moviewikipage
            movie.plot = movieplot
            db.session.commit()
            return render_template('index2.html')


## THE GHOST OF THE SHADOW ##

if __name__ == '__main__':
    app.run()




from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm, form
from sqlalchemy import Float
from sqlalchemy.orm import session
from wtforms import StringField, SubmitField, FloatField, validators
from wtforms.validators import DataRequired, InputRequired, ValidationError
import requests

API_KEY="b3abf67ad76ca3d1dad227ef209ba027"
ACCESS_TOCKEN="Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJiM2FiZjY3YWQ3NmNhM2QxZGFkMjI3ZWYyMDliYTAyNyIsInN1YiI6IjY0NzA3ZjlhYzVhZGE1MDBhODJkZWU0OCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.ni3rg0TGPIPk0yPTZ5vzzXepX0G9IZIfZLxHxaFEe0o"

#all_movies=[]

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///movie-collection.db"
db=SQLAlchemy(app)
Bootstrap(app)


def movie_details(movie_name):
    url = f"https://api.themoviedb.org/3/search/movie?query={movie_name}"

    headers = {
        "accept": "application/json",
        "Authorization": ACCESS_TOCKEN
    }

    response = requests.get(url, headers=headers)
    print(response)

    print(response)
    # print(response.json())
    # print(response.text)
    movies=response.json()["results"]
    # print(movies)
    # print("///////////////////////////////////////////////////")
    return movies




class RatingForm(FlaskForm):
    rating=FloatField('Your Rating Out of 10 e.g. 7.5', validators=[InputRequired()])
    review = StringField('Your Review', validators=[InputRequired()])
    submit=SubmitField('Done')

class AddForm(FlaskForm):
    title=StringField('Movie Title',validators=[DataRequired()])

    submit=SubmitField('Done')

class Movie(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(250),unique=True,nullable=False)
    year=db.Column(db.Integer, nullable=False)
    description=db.Column(db.String(250),nullable=False)
    rating=db.Column(db.Float, nullable=True)
    ranking=db.Column(db.Integer, nullable=True)
    review=db.Column(db.String(250),nullable=True)
    img_url=db.Column(db.String(250),nullable=False)

with app.app_context():
    db.create_all()


    # new_movie = Movie(
    #     title="Phone Booth",
    #     year=2002,
    #     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    #     # rating=7.3,
    #     # ranking=10,
    #     review="My favourite character was the caller.",
    #     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
    # )
    #
    # db.session.add(new_movie)
    # db.session.commit()


@app.route("/")
@app.route("/index")
def home():
    # global all_movies
    all_movies = db.session.query(Movie).order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        # This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)

@app.route("/update/<int:movie_id>", methods=["GET", "POST"])
def update(movie_id):

    movie_to_update = Movie.query.get(movie_id)
    rating_form=RatingForm()

    if request.method=='POST':

        New_rating=request.form['rating']
        New_review = request.form['review']
        movie_to_update.rating=New_rating
        movie_to_update.review = New_review
        db.session.commit()
        return redirect(url_for('home'))

    else:
        print("-------------False in Update--------------")
    # global all_movies
    # all_movies = db.session.query(Movie).all()
    return render_template("edit.html",movie=movie_to_update,rating_form=rating_form)

@app.route("/delete")
def delete():
    movie_id=request.args.get("id")
    movie_to_delete=Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/add",  methods=["GET", "POST"])
def add():

    add_movie=AddForm()
    if request.method=='POST':
        request_movie = request.form['title']
        movie_list=movie_details(request_movie)

        return render_template("select.html", movies=movie_list)


    return render_template("add.html",add_form=add_movie)


@app.route("/select")
def select():
    movie_id = request.args.get('id')

    photo_url="https://image.tmdb.org/t/p/w500"
    movie_api_url=f"https://api.themoviedb.org/3/movie/{movie_id}"
    response = requests.get(movie_api_url, params={"api_key": API_KEY, "language": "en-US"})
    print(response)
    print(response.text)
    select_movie=response.json()


    new_movie=Movie(

        title=select_movie["original_title"],
        description=select_movie["overview"],
        year=select_movie["release_date"].split('-')[0],
        img_url=f"{photo_url}{select_movie['poster_path']}"

    )

    db.session.add(new_movie)
    db.session.commit()

    return redirect(url_for('update', movie_id= new_movie.id))



if __name__ == '__main__':
    app.run(debug=True)

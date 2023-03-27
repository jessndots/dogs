from flask import Flask, request, render_template, flash, redirect, session, jsonify, g, url_for
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, TraitPreferences, Search, BreedRecommendations, AgePreference, SizePreference, SavedDog
from forms import AboutForm, AddToFavorites, LoginForm, SignupForm, EditAccountForm
from flask_bootstrap import Bootstrap
from breedsApi import BreedsApi
from petFinderApi import PetFinderApi
from pf_api_key import api_secret, api_key
from score_functions import *
from flask_bcrypt import Bcrypt


app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = "oh-so-secret" 
debug=DebugToolbarExtension(app)

bcrypt = Bcrypt()

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///dogs'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False       
connect_db(app)

pf = PetFinderApi(api_key=api_key, api_secret=api_secret)

@app.route("/")
def show_home():
  """About, login, sign up. If logged in - saved pups, current settings?"""
  if session.get("user_id"):
    user = User.query.get(session["user_id"])
  else: 
    user = None

  return render_template("home.html", user=user)

@app.route("/signup", methods=["GET", "POST"])
def signup():
  """Register user: produce form & handle form submission"""

  form = SignupForm()
  if form.validate_on_submit():
    first_name = form.first_name.data
    last_name = form.last_name.data
    email = form.email.data
    password = form.password.data
    user=User.signup(first_name=first_name, last_name=last_name, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    session["user_id"] = user.id
    return redirect("/about")
  user = None

  return render_template("signup.html", form=form, user=user)
  


@app.route("/login", methods=["GET", "POST"])
def login():
  """Produce login form or handle login"""
  form = LoginForm()
  if form.validate_on_submit():
    email = form.email.data
    password = form.password.data

    # authenticate will return a user or false
    user = User.authenticate(email, password)

    if user:
      session["user_id"] = user.id
      # keep logged in
      return redirect("/")
    else: 
      form.email.errors = ["Invalid email or password"]
  user = None
  return render_template("login.html", form=form, user=user)

@app.route("/logout")
def logout():
  """Logs user out and redirects to home page"""
  session.pop("user_id")
  return redirect("/")

@app.route("/about", methods=["GET","POST"])
def about():
  """About user form. handle submit."""
  if session.get("user_id"):
    user = User.query.get(session["user_id"])
  else: 
    user = None
    return redirect("/login")

  form = AboutForm() 
  if form.validate_on_submit():
    zip=form.zip.data
    distance=form.distance.data
    size=form.size.data
    size_p=form.size_priority.data
    age=form.age.data
    age_p=form.age_priority.data
    good_with_children=form.good_with_children.data
    children_p=form.children_priority.data
    good_with_dogs=form.good_with_dogs.data
    dogs_p=form.dogs_priority.data
    good_with_cats=form.good_with_cats.data
    cats_p=form.cats_priority.data
    house_trained=form.house_trained.data
    house_trained_p=form.house_trained_priority.data
    sex=form.sex.data
    sex_p=form.sex_priority.data
    barking_min=form.barking_min.data
    barking_max=form.barking_max.data
    energy_min=form.energy_min.data
    energy_max=form.energy_max.data
    protectiveness_min=form.protectiveness_min.data
    protectiveness_max=form.protectiveness_max.data
    shedding_min=form.shedding_min.data
    shedding_max=form.shedding_max.data
    trainability_min=form.trainability_min.data
    trainability_max=form.trainability_max.data


    if user.search:
      Search.query.filter(Search.user_id==user.id).delete()

    search=Search(user_id=session["user_id"], zip_code=zip, distance=distance, good_with_children=good_with_children, good_with_children_p=children_p, good_with_dogs=good_with_dogs, good_with_dogs_p=dogs_p, good_with_cats=good_with_cats, good_with_cats_p=cats_p, house_trained=house_trained, house_trained_p=house_trained_p, sex=sex, sex_p=sex_p, age_p=age_p, size_p=size_p)
    db.session.add(search)
    db.session.commit()
    print(search)

    if user.age_preferences:
      AgePreference.query.filter(AgePreference.user_id==user.id).delete()

    for a in age:
      age_preference=AgePreference(user_id=session["user_id"], search_id=search.id, age=a)
      db.session.add(age_preference)
      db.session.commit()
      print(age_preference)

    if user.size_preferences:
      SizePreference.query.filter(SizePreference.user_id==user.id).delete()

    for s in size:
      size_preference=SizePreference(user_id=session["user_id"], search_id=search.id, size=s)
      db.session.add(size_preference)
      db.session.commit()
      print(size_preference)

    if user.trait_preferences:
      TraitPreferences.query.filter(TraitPreferences.user_id==user.id).delete()

    traits = TraitPreferences(user_id=session["user_id"],barking_min=min(barking_min, barking_max), barking_max=max(barking_min, barking_max), energy_min=min(energy_max, energy_min), energy_max=max(energy_min, energy_max), protectiveness_min=min(protectiveness_min, protectiveness_max), protectiveness_max=max(protectiveness_min, protectiveness_max), shedding_min=min(shedding_min, shedding_max), shedding_max=max(shedding_min, shedding_max), trainability_min=min(trainability_min, trainability_max), trainability_max=max(trainability_min, trainability_max))
    db.session.add(traits)
    db.session.commit()
    print(traits)

    return redirect("/dogs")
  else:
    return render_template("about.html", form=form, user=user)
  
@app.route("/dogs", methods=['GET', 'POST'])
def get_dogs():
  """Show dogs based on user info & about form results"""
  if session.get("user_id"):
    user = User.query.get(session['user_id'])
  else:
    return redirect("/login")
  try:
    trait_preferences = user.trait_preferences[0]
    search = user.search[0]
    size = user.size_preferences
    age = user.age_preferences
  except:
    return redirect("/about")

  resp = pf.get_dogs(search, age, size)
  scored_dogs = score_dogs(dog_list=resp['animals'], search_obj=search, age_list=age, size_list=size, trait_prefs=trait_preferences)
  sorted_dogs = sort_by_score(scored_dogs)

  def get_photo(dog):
    if type(dog['primary_photo_cropped']) == list:
      return dog['primary_photo_cropped'][0]['medium']
    elif type(dog['primary_photo_cropped']) == dict:
      return dog['primary_photo_cropped']['medium']
    else: 
      return None
    
  def get_dog_link(dog):
    return f'/dogs/{dog["id"]}'

  return render_template("dogs.html", user=user, dogs=sorted_dogs, get_photo=get_photo, get_dog_link=get_dog_link)
  
@app.route("/dogs/<int:id>", methods=['GET', 'POST'])
def show_dog(id):
  """Show dogs based on user info & about form results"""
  if session.get("user_id"):
    user = User.query.get(session['user_id'])
  else:
    redirect("/login")

  # trait_preferences = user.trait_preferences[0]
  # search = user.search[0]
  # size = user.size_preferences
  # age = user.age_preferences

  dog = pf.get_dog(id)
  favorited = SavedDog.query.filter(SavedDog.user_id == user.id, SavedDog.pf_id == dog['id']).first()
  
  form = AddToFavorites()
  if form.validate_on_submit():
    if favorited:
      db.session.delete(favorited)
      db.session.commit()
    else:
      saved = SavedDog(user_id=user.id, pf_id=dog['id'])
      db.session.add(saved)
      db.session.commit()
    return redirect(f"/dogs/{dog['id']}")
  else: 
    # move to helper functions file
    def get_photo(dog):
      if type(dog['primary_photo_cropped']) == list:
        return dog['primary_photo_cropped'][0]['medium']
      elif type(dog['primary_photo_cropped']) == dict:
        return dog['primary_photo_cropped']['medium']
      else: 
        return None
      
    def format_breeds(dog):
      if dog['breeds']['mixed'] == False:
        return f"{dog['breeds']['primary']}"
      elif dog['breeds']['secondary']: 
        return f"{dog['breeds']['primary']} / {dog['breeds']['secondary']} Mix"
      elif dog['breeds']['primary']: 
        return f"{dog['breeds']['primary']} Mix"
      else:
        return "Mixed Breed"
      

    return render_template("dog.html", user=user, form=form, dog=dog, get_photo=get_photo, format_breeds=format_breeds, favorited=favorited)
  

@app.route("/favorites")
def show_favorites():
  if session.get("user_id"):
    user = User.query.get(session['user_id'])
  else:
    return redirect("/login")
  saved = SavedDog.query.filter(SavedDog.user_id==user.id).all()
  favorites = []
  for dog in saved:
    favorites.append(pf.get_dog(dog.pf_id))

  def get_photo(dog):
    print(dog)
    if type(dog['primary_photo_cropped']) == list:
      return dog['primary_photo_cropped'][0]['medium']
    elif type(dog['primary_photo_cropped']) == dict:
      return dog['primary_photo_cropped']['medium']
    else: 
      return None
    
  def get_dog_link(dog):
    return f'/dogs/{dog["id"]}'

  return render_template("favorites.html", user=user, favorites=favorites, get_photo=get_photo, get_dog_link=get_dog_link)

@app.route("/account")
def show_account():
  if session.get("user_id"):
    user = User.query.get(session['user_id'])
  else:
    return redirect("/login")
  
  return render_template("account.html", user=user)

@app.route("/account/edit", methods=["GET", "POST"])
def edit_account():
  if session.get("user_id"):
    user = User.query.get(session['user_id'])
  else:
    return redirect("/login")
  
  form=EditAccountForm(obj=user)
  if form.validate_on_submit():
    user.update(firstName=form.first_name.data, lastName=form.last_name.data, email=form.email.data, password=form.password.data)
    db.session.add(user)
    db.session.commit()
    return redirect("/account")
  
  return render_template("account-edit.html", user=user, form=form)


  
  



from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_bcrypt import Bcrypt
from sqlalchemy_utils import IntRangeType

db= SQLAlchemy()
def connect_db(app):
    db.app = app
    db.init_app(app)

bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = "users"
    def __repr__(self): 
        """Show info about user"""
        u = self
        return f"<User {u.id}: {u.first_name} {u.last_name}, {u.email}, {u.timestamp}>"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    trait_preferences = db.relationship('TraitPreferences', backref='users')
    search = db.relationship('Search', backref='users')
    breed_recs = db.relationship('BreedRecommendations', backref='users')
    size_preferences = db.relationship('SizePreference', backref='users')
    age_preferences = db.relationship('AgePreference', backref='users')
    saved_dogs = db.relationship('SavedDog', backref="users")

    @classmethod
    def signup(cls, first_name, last_name, email, password):
        """Register user w/ hashed password and return user"""

        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")

        return cls(first_name=first_name, last_name=last_name, email=email, password=hashed_utf8)
    
    @classmethod
    def authenticate(cls, email, password):
        """Validate that user exists & password is correct. Return user if valid; else return False"""

        u = db.session.query(cls).filter(User.email==email).first()
        if u and bcrypt.check_password_hash(u.password, password):
            return u
        else:
            return False
        
    def update(self, firstName="", lastName="", email="", password=""):
        self.first_name=firstName if firstName else self.first_name
        self.last_name=lastName if lastName else self.last_name
        self.email=email if email else self.email
        if password:
            hashed = bcrypt.generate_password_hash(password)
            hashed_utf8 = hashed.decode("utf8")
            self.password = hashed_utf8





class TraitPreferences(db.Model):
    __tablename__ = "trait_preferences"
    def __repr__(self): 
        """Show info about trait preferences"""
        p = self
        return f"<Trait Preferences for User {p.user_id}: Barking {p.barking_min}-{p.barking_max}, Energy {p.energy_min}-{p.energy_max}, Protectiveness {p.protectiveness_min}-{p.protectiveness_max}, Shedding {p.shedding_min}-{p.shedding_max}, Trainability {p.trainability_min}-{p.trainability_max}>"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    shedding_min = db.Column(db.Integer)
    shedding_max = db.Column(db.Integer)
    barking_min = db.Column(db.Integer)
    barking_max = db.Column(db.Integer)
    energy_min = db.Column(db.Integer)
    energy_max = db.Column(db.Integer)
    protectiveness_min = db.Column(db.Integer)
    protectiveness_max = db.Column(db.Integer)
    trainability_min = db.Column(db.Integer)
    trainability_max = db.Column(db.Integer)

    recommended_breeds = db.relationship('BreedRecommendations', backref='trait_preferences')

class Search(db.Model):
    __tablename__ = "searches"
    def __repr__(self):
        """Show info about a search instance"""
        p = self
        return f"<Search {p.id}: User - {p.user_id}, Timestamp - {p.timestamp}, Zip Code - {p.zip_code}, Distance - {p.distance}>"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    zip_code = db.Column(db.Integer, nullable=False)
    distance = db.Column(db.Integer, nullable=False, default=100)
    good_with_children = db.Column(db.Boolean)
    good_with_children_p = db.Column(db.Integer) 
    good_with_dogs = db.Column(db.Boolean)
    good_with_dogs_p = db.Column(db.Integer)
    good_with_cats = db.Column(db.Boolean)
    good_with_cats_p = db.Column(db.Integer)
    house_trained = db.Column(db.Boolean)
    house_trained_p = db.Column(db.Integer)
    sex = db.Column(db.String(20))
    sex_p = db.Column(db.Integer)
    age_p = db.Column(db.Integer)
    size_p = db.Column(db.Integer)

    age=db.relationship('AgePreference', backref='searches')
    size = db.relationship('SizePreference', backref='searches')

class BreedRecommendations(db.Model):
    __tablename__ = "breed_recommendations"
    def __repr__(self):
        """Show user's preferred breeds"""
        b = self
        return f"<Breed Recommendation {b.id}: {b.breed_name}, User {b.user_id}, used in Search {b.search_id}, recommended from Trait Preferences {b.trait_preferences_id}>"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    trait_preferences_id = db.Column(db.Integer, db.ForeignKey('trait_preferences.id', ondelete='CASCADE'))
    breed_name = db.Column(db.String(100), nullable=False)

class SizePreference(db.Model):
    __tablename__ = "size_preferences"
    def __repr__(self):
        """Show user's preferred dog sizes"""
        s = self
        return f"<Size Preference {s.id}: {s.size}, User {s.user_id}, from Search {s.search_id}>"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    search_id = db.Column(db.Integer, db.ForeignKey('searches.id', ondelete='CASCADE'), nullable=False)
    size = db.Column(db.String(50), nullable=False)

    
class AgePreference(db.Model):
    __tablename__ = "age_preferences"
    def __repr__(self):
        """Show user's preferred dog ages"""
        a = self
        return f"<Age Preference {a.id}: {a.age}, User {a.user_id}, from Search {a.search_id}>"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    search_id = db.Column(db.Integer, db.ForeignKey('searches.id', ondelete='CASCADE'), nullable=False)
    age = db.Column(db.String(50), nullable=False)


class SavedDog(db.Model):
    __tablename__="saved_dogs"
    def __repr__(self):
        """Show user's saved dogs"""
        d = self
        return f"<Saved Dog {d.id}: User {d.user_id}, PetFinder Id {d.pf_id}>"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    pf_id = db.Column(db.Integer, nullable=False)
    note = db.Column(db.Text)


from models import *
from app import app, db
from unittest import TestCase
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///dogs-test'
app.app_context().push()
with app.app_context():
  db.drop_all()
  print('dropped')
  db.create_all()
  print('created')

class TestUser(TestCase):
  def setUp(self):
    with app.app_context():
      User.query.delete()
      User.signup(first_name='Test', last_name='User', email='test@email.com', password='testtest')

  def tearDown(self):
      db.session.rollback()

  def test_signup(self):
      """Model instance should exist"""
      self.assertTrue(
          db.session.query(User).filter(User.first_name=='Test').first()
          is not None)
      
  def test_authenticate(self):
      """Model should return user with accurate email and password"""
      authenticated = User.authenticate(email='test@email.com', password='testtest')
      self.assertEqual(
        authenticated.first_name, 'Test'
      )

  def test_update(self):
      """Model modification should modify model"""
      user = db.session.query(User).filter(User.first_name=='Test').first()
      user.update(lastName='New')
      db.session.flush()
      self.assertTrue(
          db.session.query(User).filter(User.last_name=='New').first()
          is not None)
      

# class TestTraitPreferences(TestCase):
#   @classmethod
#   def setUpClass(cls):
#       # Create schema
#       cls.app = app
#       cls.app_context = cls.app.app_context()
#       cls.app_context.push()

#       db.create_all()
#       user = User.signup(first_name='Test', last_name='Test', email='test@email.com', password='testtest')
#       db.session.add(user)
#       db.session.commit()
#       db.session.add(TraitPreferences(user_id=user.id, shedding_min=1, shedding_max = 4, barking_min = 1, barking_max = 4, energy_min = 1, energy_max = 4,   protectiveness_min = 1, protectiveness_max = 4, trainability_min = 1, trainability_max = 4))

#   @classmethod
#   def tearDownClass(cls):
#       # Drop schema
#       db.drop_all()


#   def tearDown(self):
#       db.session.rollback()

#   def test_exists(self):
#       """Model instance should exist"""
#       user = db.session.query(User).filter(User.first_name=='Test').first()
#       self.assertTrue(
#           db.session.query(TraitPreferences).filter(TraitPreferences.user_id==user.id).first() is not None)
      
#   def test_deletion(self):
#       """Model isntance is properly deleted"""
#       user = db.session.query(User).filter(User.first_name=='Test').first()
#       db.session.query(TraitPreferences).filter(TraitPreferences.user_id==user.id).delete()
#       self.assertTrue(
#           db.session.query(TraitPreferences).filter(TraitPreferences.user_id==user.id).first() is None
#       )
      


  


from breedsApi import *
from operator import itemgetter

breeds_api = BreedsApi()

def score_dogs(dog_list, search_obj, age_list, size_list, trait_prefs):
  breed_scores = {}
  dogs=[]
  for d in dog_list:
    dog=d
    score=0
    if dog['environment']['children'] == None:
      score += 0
    elif dog['environment']['children'] == search_obj.good_with_children:
      score += search_obj.good_with_children_p
    else:
      score -= search_obj.good_with_children_p

    if dog['environment']['dogs'] == None:
      score += 0

    elif dog['environment']['dogs'] == search_obj.good_with_dogs:
      score += search_obj.good_with_dogs_p
    else: 
      score -= search_obj.good_with_dogs_p

    if dog['environment']['cats'] == None:
      score += 0
    elif dog['environment']['cats'] == search_obj.good_with_cats:
      score += search_obj.good_with_cats_p
    else: 
      score -= search_obj.good_with_cats_p

    if dog['attributes']['house_trained'] == None:
      score += 0
    elif dog['attributes']['house_trained'] == search_obj.house_trained:
      score += search_obj.house_trained_p
    else:
      score -= search_obj.house_trained_p

    if dog['gender'] == search_obj.sex:
      score += search_obj.sex_p
    else: 
      score -= search_obj.sex_p

    if dog['age'] in [obj.age for obj in age_list]:
      score += search_obj.age_p
    else: 
      score -= search_obj.age_p
      
    if dog['size'] in [obj.size for obj in size_list]:
      score += search_obj.size_p
    else: 
      score -= search_obj.size_p

    if dog['breeds']['primary']:
      score += score_breed(dog['breeds']['primary'], trait_prefs)

    if dog['breeds']['secondary']:
      score += score_breed(dog['breeds']['secondary'], trait_prefs)

    dog.update({'score': score})
    dogs.append(dog)
  print(len(dogs))
  return dogs


def score_breed(breed, trait_prefs):
  if breed: 
    resp = breeds_api.getBreed(breed=breed)
    if len(resp) != 1 : return 0
    b = resp[0]  
    score = 0
    if b.get('barking',0) > trait_prefs.barking_min and b.get('barking',0) < trait_prefs.barking_max:
      score += 3
    
    if b.get('energy',0) > trait_prefs.energy_min and b.get('energy',0) < trait_prefs.energy_max:
      score += 3

    if b.get('protectiveness',0) > trait_prefs.protectiveness_min and b.get('protectiveness',0) < trait_prefs.protectiveness_max:
      score +=3

    if b.get('shedding',0) > trait_prefs.shedding_min and b.get('shedding',0) < trait_prefs.shedding_max:
      score += 3

    if b.get('trainability',0) > trait_prefs.trainability_min and b.get('trainability',0) < trait_prefs.trainability_max:
      score += 3

    return score
  return 0

def sort_by_score(dogs):
  sorted_dogs = sorted(dogs, key=itemgetter('score')) 
  return sorted_dogs



  
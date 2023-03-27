import requests

class PetFinderApi:

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.getToken()

    def request(self, data = {}, method = "get", path=""):
        print("API CALL:", data, method)

        url = 'https://api.petfinder.com/'+path

        headers = {"Authorization": f"Bearer {self.token['access_token']}"}
        params = data

        response = requests.get(url=url, headers=headers, params=params)

        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            if response.status_code == 401:
              self.getToken()
              response = requests.get(url=url, headers=headers, params=params)
              if response.status_code == requests.codes.ok:
                  return response.json()
            print("Error:", response.status_code, response.text)
            return response.json()
        
    
    def getToken(self):
        d={
            'grant_type': 'client_credentials', 
            'client_id': self.api_key, 
            'client_secret': self.api_secret,
        }

        resp = requests.post(url='https://api.petfinder.com/v2/oauth2/token', json=d)
        data = resp.json()
        
        self.token = data

        return self.token['access_token']
    
    def get_dogs(self, search_obj, age_list, size_list):
      d={
        'location': search_obj.zip_code,
        'distance': search_obj.distance,
        'type': 'dog', 
        'limit': '100', 
        'sort': 'distance'
      }
      if search_obj.good_with_children_p == 5:
        d.update({'good_with_children': search_obj.good_with_children})
      if search_obj.good_with_dogs_p ==5:
        d.update({'good_with_dogs': search_obj.good_with_dogs})
      if search_obj.good_with_cats_p ==5:
        d.update({'good_with_cats': search_obj.good_with_dogs})
      if search_obj.house_trained_p ==5:
        d.update({'house_trained': search_obj.house_trained})
      if search_obj.sex_p ==5:
        d.update({'gender': search_obj.sex})
      if search_obj.age_p ==5:
        a = [obj.age for obj in age_list]
        d.update({'age': ','.join(a)})
      if search_obj.size_p ==5:
        s = [obj.size for obj in size_list]
        d.update({'size': ','.join(s)})  

      resp = self.request(data=d, path='v2/animals')     
      return resp
    
    def get_dog(self, id):
      resp = self.request(path=f'v2/animals/{id}')
      return resp['animal']
       
    def get_organization(self, path):
       resp = self.request(path=f'{path}')
       return resp
    







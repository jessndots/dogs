import requests
import json

class BreedsApi:
    breeds = {}
    def request(self, data = {}, method = "get"):
        print("API CALL:", data, method)

        url = f'https://api.api-ninjas.com/v1/dogs'

        headers = {'X-Api-Key': 'Tln+izAUg/s32bUn0GAL9Q==Aaoac0NVgdIRKy4E'}
        params = data

        response = requests.get(url=url, headers=headers, params=params)
        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            print("Error:", response.status_code, response.text)
            return response.json()
        
    def getBreed(self, breed):
        if breed in self.breeds:
            return self.breeds[breed]
        else:
            resp = self.request(data={'name': breed})
            self.breeds[breed] = resp
            return resp
    


        





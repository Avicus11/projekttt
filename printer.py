import os

directory = 'static'

for datoteka in os.walk(directory):
    print(datoteka)

#poženemo v konzoli in nam da sledeč famozni seznam v modelu.py
# This file contains the descriptions of the endpoints. 
# It'll be used to import them in the respective route files so the code is kept clean and readable.


GET_SORTED_TOP_CHARACTERS_DESCRIPTION = """ 
Returns a list of the 10 characters that appear the most in all the Star Wars movies (listed in https://swapi.dev/) , sorted by their height in descending order (tall first).

It also generates a CSV file with the columns name, species, films, and height, saves it to disk, and sends it to https://httpbin.org
    
Internally it uses cache so it can be called multiple times without hitting the API.
"""
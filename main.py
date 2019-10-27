import gensim
import random
import json
from meronymizer import Meronymizer
from list_from_wikibooks import open_file
from ingredient_identificiation_wikibooks import get_ingredients
from replace_ingredients import replace_ingr_in_steps
from replace_ingredients import add_adjectives
from replace_ingredients import styling_n_save

#Creating list from Wikibooks

recipe_list=open_file("Wikibooks-20191025080703.xml")

ing_ins_orig_dict=get_ingredients(random.choice(recipe_list))


# I'm using http://vectors.nlpl.eu/repository/11/26.zip
print('Loading word embeddings\n')
model = gensim.models.KeyedVectors.load_word2vec_format('model.txt')

ingredients = []
for i in ing_ins_orig_dict["ingredients"]:
    ingredients.append(i[0].lower())

# If an imput word is given, the program finds the semantically most similar word
# with at least as many meronyms in WordNet as the number of ingredients given
meronymizer1 = Meronymizer(model, ingredients=ingredients, word='fortress')

new_ingredients = meronymizer1.get_new_ingredients()
print(new_ingredients)
random_new_ingredient = random.choice(new_ingredients)
#a_verb = 'chop'
#corresponding_verb = meronymizer1.find_corresponding_verb(random_new_ingredient, 'chop')
#print(f"\"{corresponding_verb}\" is the verb corresponding to \"{a_verb}\" for the word \"{random_new_ingredient}\"")

#  If an imput word is not given, the program picks a word randomly
#  with at least as many meronyms in WordNet as the number of ingredients given
meronymizer2 = Meronymizer(model, ingredients=ingredients)

new_ingredients = meronymizer2.get_new_ingredients()
print(new_ingredients)
random_new_ingredient = random.choice(new_ingredients)
#a_verb = 'chop'
#corresponding_verb = meronymizer2.find_corresponding_verb(random_new_ingredient, 'chop')
#print(f"\"{corresponding_verb}\" is the verb corresponding to \"{a_verb}\" for the word \"{random_new_ingredient}\"")

styling_n_save(ing_ins_orig_dict["ingredients"],new_ingredients, ing_ins_orig_dict["text_ingredients"], ing_ins_orig_dict["instructions"], ing_ins_orig_dict["original"])

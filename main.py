import gensim
import random
from meronymizer import Meronymizer

# I'm using http://vectors.nlpl.eu/repository/11/26.zip
print('Loading word embeddings\n')
model = gensim.models.KeyedVectors.load_word2vec_format('model.txt')

ingredients = ['ginger', 'salt', 'meat', 'potato', 'sugar', 'pasta', 'onions']

# If an imput word is given, the program finds the semantically most similar word
# with at least as many meronyms in WordNet as the number of ingredients given
meronymizer1 = Meronymizer(model, ingredients=ingredients, word='fortress')

new_ingredients = meronymizer1.get_new_ingredients()
print(new_ingredients)
random_new_ingredient = random.choice(new_ingredients)
a_verb = 'chop'
corresponding_verb = meronymizer1.find_corresponding_verb(random_new_ingredient, 'chop')
print(f"\"{corresponding_verb}\" is the verb corresponding to \"{a_verb}\" for the word \"{random_new_ingredient}\"")

#  If an imput word is not given, the program picks a word randomly
#  with at least as many meronyms in WordNet as the number of ingredients given
meronymizer2 = Meronymizer(model, ingredients=ingredients)

new_ingredients = meronymizer2.get_new_ingredients()
print(new_ingredients)
random_new_ingredient = random.choice(new_ingredients)
a_verb = 'chop'
corresponding_verb = meronymizer2.find_corresponding_verb(random_new_ingredient, 'chop')
print(f"\"{corresponding_verb}\" is the verb corresponding to \"{a_verb}\" for the word \"{random_new_ingredient}\"")


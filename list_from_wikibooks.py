#Author: Meri Vikman

#Creating list file with recipes from wikibooks
import io
import pickle

def open_file(filename):
    all_lines=[]
    file = io.open(filename, 'r', encoding='Utf-8', errors="ignore")
    fl=file.readlines()
    one_recipe_lines=[]
  
    found=False
    for line in fl:
        
        
        
        if "{{recipe}}" in line:
            found=True
            #print("found 'recipe'")
        elif  "Category:" in line:
            #print("found 'category'")
            if len(one_recipe_lines)>1:
                all_lines.append(one_recipe_lines)
            #print("added recipe to all_lines")
            one_recipe_lines=[]
            found=False
        
        elif found==True:
            #print(line)
            one_recipe_lines.append(line)
            #print("added line to recipe")
        
        
        
    return(all_lines)

recipes=open_file("Wikibooks-20191025080703.xml")


#with open("recipes2.txt", "wb") as fp: 
#    pickle.dump(recipes, fp)


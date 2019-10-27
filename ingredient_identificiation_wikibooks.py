#Author: Meri Vikman

import io
import re
import random
import pickle
import spacy
nlp = spacy.load("en_core_web_sm")
from spacy.symbols import nsubj, dobj, NOUN

def open_file(filename):
    with open(filename, "rb") as fp:
        all_lines = pickle.load(fp)
    
   
    return(all_lines)


#print(all_lines)

def get_ingredients(lines):
    ingredients=[]
    steps=[]
    #for line in lines:
        #print(line)
   
    found=False
    
    for l in lines:
        if l.startswith("#"):
            steps.append(l)

        if l.startswith("*"):
            ingredients.append(l)
            
            
    steps_cleaned=[]
    ing_meas_list=[]  
    ing_list=[]
    ing_amount_list=[]
    ingredients_orig_cleaned=[]
        
    for l in steps:
        l=re.sub(r'\[\[[Cc]ookbook\:([A-Za-z]*\s*)+\|', "", l)
        #l=re.sub(r'\(([A-Za-z]*\.*\,*\:*\s*)*\)', "", l)   #This would clean out any text inside paranthesis
        l=re.sub(r'\{\{[A-Za-z]*\}\}', "", l)
        l=re.sub(r'[\*\]\{\}\)\(\.]', "", l)
        words_l=l.split()
        steps_cleaned.append(l)
        
        


           
    for l in ingredients:
        #Here I'm cleaning away some of the XML code, such as links. However, I'm also removing paranthesis and any content inside paranthesis
        #this turned out to be useful to get to the main ingredient better. 
        
        l=re.sub(r'\[\[[Cc]ookbook\:([A-Za-z]*\s*)+\|', "", l)
        #l=re.sub(r'\(([A-Za-z]*\.*\,*\:*\s*)*\)', "", l)
        l=re.sub(r'\{\{[A-Za-z]*\}\}', "", l)
        l=re.sub(r'[\]\{\}\)\(\.]', "", l) 
        ingredients_orig_cleaned.append(l)
        l=re.sub(r'[\*]', "", l)
        words_l=l.split()
        
        
        
       
      #The list of possible units. This list has been expanded according to examples that came up in the data dyring development runs and is undoubtedly not complete. 
        
        measures=["drop", "drops", "dash", "oz", "oz.", "lb.", "lbs.", "tbsp", "tbsp.", "tsp", "tsp." "dl", "ml", "l", "cl", "g", "grams", "liter", "liters" "bag", 
                  "package", "thumb-sized", "piece", "cloves", "ounce", "ounces", "cup","cups", "tablespoon", "tablespoons", "teaspoon", "teaspoons", "pound", "pounds", 
                  "tbls", "gallon", "gallons", "kg", "pint", "pints", "part", "parts", "pinch", "can", "cans", "c."]
        
        ing_meas=""
        ing_amount=""
        ing=""
    
        num=""
        meas=""   
        for w in words_l:
            
            if w.lower() in measures:
                meas+=w+" "
            elif re.match(r'([0-9]+\-*\/*\s*\.*\,*)+', w):
                num=w
                #print("print number: ", w)
                
    
                
    
    
            elif re.match("^[a-zA-Z\(\)\,\.]*$", w) :
           
                ing+=w+" "
        meas[-1:]
        ing_amount_list.append(num)
        ing_meas_list.append(meas)
        ing[-1:]
#Here I am setting the maximum length of an ingredient to 10 words trying to avoid including long descriptions that are not ingredients.     
        if len(ing.split())<10:        
            ing_list.append(ing)
           
    final_ingredient_list=[]
    prepositions=["of", "with", "on", "in", "for", "to"]
    for i in range(len(ing_list)):
        
        for j in prepositions:
        
            ing_list[i]=ing_list[i].replace(j, "")
                  
             
        #print("Before spacy ingredient: ", ing_list[i])
            
        #print("amount: ",ing_amount_list[i])
        #print("measure: ", ing_meas_list[i])
        
       
            
        
        ingredient=nlp(ing_list[i])
        #print("Before spacy: ", ing_list[i])

#        for chunk in ingredient.noun_chunks:
#            print(chunk.text, chunk.root.text, chunk.root.dep_,
#            chunk.root.head.text) 
        
        for pos_subject in ingredient:
            fin_ingredient=[]


           
            if pos_subject.pos==NOUN:
                #print("pos_sub.head: ", pos_subject.head)
                fin_ingredient.append(str(pos_subject.head))
                #print("fin_ing ", fin_ingredient)
                
# Spacy gives several options for the possible subject/noun and I have here chosen the last one, which may not be the best choice.
           
            if len(fin_ingredient)>0 and fin_ingredient not in final_ingredient_list:
                final_ingredient_list.append(fin_ingredient)
        
    fin_dict={"ingredients": final_ingredient_list, "text_ingredients": ingredients_orig_cleaned, "instructions": steps_cleaned, "original": lines}
    return fin_dict   


            
    
    
    
#recipes=open_file("recipes.txt")
#ingredients, instructions, ing_orig, orig_recipe=get_ingredients(random.choice(recipes))

#The program saves a dictionary with four keys.

#fin_dict={"ingredients": ingredients, "text_ingredients": ing_orig, "instructions": instructions, "original": orig_recipe }

#return(fin_dict)

#f = open("ing_n_instr_dict.pkl","wb")
#pickle.dump(fin_dict,f)
#f.close()






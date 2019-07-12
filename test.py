import spacy
from spacy import displacy
import neuralcoref

from nltk.stem import WordNetLemmatizer


nlp = spacy.load("en_core_web_sm")
#neuralcoref.add_to_pipe(nlp)



#doc = nlp("There is a tall boy in a big room.") ############################################## ??

#doc = nlp("The boy and the man and the girl all walk towards the second red chair.")

doc = nlp("There was another short player with a black hair.")


#doc = nlp("The boy shoots the man with the gun.")
#doc = nlp("The short man shoots the boy with a black gun.")
#doc = nlp("There is a tall boy in a large black room.")
#print(len(doc._.coref_clusters))
#print(doc._.coref_clusters)
#print(doc._.coref_clusters[1].mentions[-1])



displacy.serve(doc, style="dep")


"""my_str = "the tall boy"
my_str_list= my_str.split(" ")
print(my_str_list)

if my_str_list[0] == "the":
    my_str_list[0]="a"
    my_str=' '.join(my_str_list)

print(my_str)"""



"""my_list = [8,2,9,10]

for i in range(0,len(my_list)):
    if i in my_list:
        print(i)
    else:
        continue"""

#lemmatizer = WordNetLemmatizer()



#print(lemmatizer.lemmatize("is",'v'))

"""print(lemmatizer.lemmatize("chairs"))
print(lemmatizer.lemmatize("balls"))
print(lemmatizer.lemmatize("plates"))
print(lemmatizer.lemmatize("tables"))
print(lemmatizer.lemmatize("bats"))
print(lemmatizer.lemmatize("cars"))
print(lemmatizer.lemmatize("bottles"))
print(lemmatizer.lemmatize("cups"))
print(lemmatizer.lemmatize("toys"))
print(lemmatizer.lemmatize("knives"))
print(lemmatizer.lemmatize("swords"))
print(lemmatizer.lemmatize("desks"))
print(lemmatizer.lemmatize("pianos"))
print(lemmatizer.lemmatize("guns"))"""


"""models_info = []

models_info.append(['box','box',['green',2],1])
models_info.append(['car','car',['black',1],2])
models_info.append(['computer','computer',['red',2],3])
models_info.append(['box','box',['green',1],4])

model_name="computer"
model_char=['red',2]

model_id = -1

for i in range(0,len(models_info)):


    if model_name == models_info[i][1]:

        char_mentioned = []
        for j in range(0,len(model_char)):
            if model_char[j] != "none" and model_char[j] != -1:
                char_mentioned.append(model_char[j])

        all_char_mentioned_found = 0

        if (all(x in models_info[i][2] for x in char_mentioned)):
            all_char_mentioned_found = 1

        if (all_char_mentioned_found):
            model_id = models_info[i][3]
            break


print(model_id)"""


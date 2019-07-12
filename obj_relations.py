import spacy
import neuralcoref
from spacy import displacy
from colour import Color
from nltk.stem import WordNetLemmatizer
import models_char
import re

nlp = spacy.load('en')
neuralcoref.add_to_pipe(nlp)

lemmatizer = WordNetLemmatizer()

object_coref_list =[]

#########################################################
count_char = ['first','second','third','fourth','fifth','sixth','seventh','eighth','ninth','tenth']
#########################################################
################################################################################################
rel_avail = ['in','on','behind','front','right','left']  # in , on , behind ,  in front of , on the right of , on the left of
################################################################################################


def get_model_id (models_info,model_name,model_char):
    model_id = -1

    for i in range(0, len(models_info)):

        if model_name == models_info[i][1]:

            char_mentioned = []
            for j in range(0, len(model_char)):
                if model_char[j] != "none" and model_char[j] != -1:
                    char_mentioned.append(model_char[j])

            all_char_mentioned_found = 0

            if (all(x in models_info[i][2] for x in char_mentioned)):
                all_char_mentioned_found = 1

            if (all_char_mentioned_found):
                model_id = models_info[i][3]
                break

    return model_id


##############################################################################################################
def detect_object_type (model_name,obj_coref):
    model_type = ""
    ##### 1- check if human
    current_model = model_name.lower()
    if current_model in models_char.boy_synonymy:
        model_type = "boy"
    elif current_model in models_char.girl_synonymy:
        model_type = "girl"
    elif current_model in models_char.man_synonymy:
        model_type = "man"
    elif current_model in models_char.woman_synonymy:
        model_type = "woman"
    elif current_model in models_char.boy_girl_synonymy:  # law mfesh coref , eh el default ???
        found_coref = False
        for i in range(0, len(obj_coref)):
            if current_model == obj_coref[i][0]:

                found_coref = True

                ## if coref is He
                if obj_coref[i][1] == 'he':
                    model_type = "boy"
                elif obj_coref[i][1] == 'she':
                    model_type = "girl"

                obj_coref.remove(obj_coref[i])

        if (not found_coref):
            model_type = "boy"  # -----------------> default is boy

    elif current_model in models_char.man_woman_synonymy:  # law mfesh coref , eh el default ???
        found_coref = False
        for i in range(0, len(obj_coref)):
            if current_model == obj_coref[i][0]:

                found_coref = True

                ## if coref is He
                if obj_coref[i][1] == 'he':
                    model_type = "man"
                elif obj_coref[i][1] == 'she':
                    model_type = "woman"

                obj_coref.remove(obj_coref[i])

        if (not found_coref):
            model_type = "man"  # -----------------> default is man

    #### 2- not human

    else:
        if (str(model_name) in models_char.models_avail) or (str(model_name) == 'boy') or (str(model_name) == 'girl') or (
                str(model_name) == 'man') or (str(model_name) == 'woman'):
            model_type = str(model_name)
        else:
            model_type = 'none'

    return model_type, obj_coref


#########################################################################

def detect_object_char (model_type, model_word):
    object_chars = []

    if (
            model_type == 'boy' or model_type == 'girl' or model_type == 'man' or model_type == 'woman'):
        object_chars = [-1, "none", -1,"none"]  # not mentioned age ,  not mentioned hair color, not mentioned height , copy number (the first,the second .....)
    else:
        object_chars = ["none", -1,"none"]  # not mentioned color, not mentioned size , copy number (the first,the second .....)

    is_tall = False
    is_short = False
    is_old = False
    is_big = False
    is_small = False
    is_color = False

    ############## find first adj ##############

    found_newAdj = False

    
    for child in model_word.children:
        

        if child.dep_ == "amod":
            found_newAdj = True

            ####### append only the specific char #################
            ## 1- check if human
            if (
                    model_type == 'boy' or model_type == 'girl' or model_type == 'man' or model_type == 'woman'):
                if str(child) in models_char.tall_synonymy:
                    is_tall = True
                    object_chars[2] = 2
                elif str(child) in models_char.short_synonymy:
                    is_short = True
                    object_chars[2] = 0

                elif str(child) in models_char.old_synonymy:
                    is_old = True
                    object_chars[0] = 1
                elif str(child) in count_char:
                    object_chars[3]=str(child)

            ## 2- not human
            else:
                if str(child) in models_char.big_synonymy:
                    is_big = True
                    object_chars[1] = 2
                elif str(child) in models_char.small_synonymy:
                    is_small = True
                    object_chars[1] = 0

                elif models_char.check_color(str(child)):
                    is_color = True
                    object_chars[0] = str(child)
                elif str(child) in count_char:
                    object_chars[2] = str(child)

            current_word = child

    ############ find conj adjs ###############

    while (found_newAdj):
        found_newAdj = False
        for child in current_word.children:
            if child.dep_ == "conj":
                found_newAdj = True
                current_word = child

                ## 1- check if human
                if (
                        model_type == 'boy' or model_type == 'girl' or model_type == 'man' or model_type == 'woman'):
                    if str(child) in models_char.tall_synonymy:
                        is_tall = True
                        object_chars[2] = 2

                    elif str(child) in models_char.short_synonymy:
                        is_short = True
                        object_chars[2] = 0

                    elif str(child) in models_char.old_synonymy:
                        is_old = True
                        object_chars[0] = 1

                ## 2- not human
                else:
                    if str(child) in models_char.big_synonymy:
                        is_big = True
                        object_chars[1] = 2
                    elif str(child) in models_char.small_synonymy:
                        is_small = True
                        object_chars[1] = 0
                    elif models_char.check_color(str(child)):
                        is_color = True
                        object_chars[0] = str(child)

        if (((is_tall or is_short) and is_old) or (
                (is_big or is_small) and is_color)):  # edit --> add new features
            break

    return object_chars

########################################################################
object_coref_list=[]


def get_objectCoref_map(input_text):

    doc=nlp(input_text)
    for i in range(0, len(doc._.coref_clusters)):
        clusters_coref = doc._.coref_clusters
        object_coref = doc._.coref_clusters[i].mentions[-1]._.coref_cluster.main

        

        object_coref_lst = str(object_coref).split(" ")

        if str(object_coref_lst[0]).lower() == "the":
            
            object_coref_lst[0] = "a"
            object_coref = ' '.join(object_coref_lst)

        

        if (str(clusters_coref[i][1]).lower() in models_char.male_pronoun) or (str(clusters_coref[i][1]).lower() in models_char.female_pronoun) or (str(clusters_coref[i][1]).lower() in models_char.rigid_pronoun):
                
                object_coref_list.append((str(object_coref).lower(), str(clusters_coref[i][1]).lower()))
                

#########################################################################

def get_refrencedObject(pronoun):

    for i in range(0,len(object_coref_list)):
        
        if  object_coref_list[i][1] == pronoun:
            return object_coref_list[i][0]

#########################################################################

def Objs_relations(input_text,models_fullInfo):


    object_coref = models_char.get_coref(input_text)

    get_objectCoref_map(input_text)

    

    doc = nlp(input_text)

    relations = []

    for sentence in doc.sents:

        for word in sentence:
            current_prep = pnoun = pobj = " "

            pnoun_id = -1
            pobj_id = -1

            if word.pos_ == "ADP" and (str(word) in rel_avail )and (  (str(word.head.pos_) != "VERB") or (lemmatizer.lemmatize(str(word.head),'v') == "be" )):   #make sure that it isn't a prep with a verb


                current_prep = str(word)

                

                pnoun_word = word
                pobj_word = word

                pnoun_list = []

                #################################### find pnoun #########################################

                if word.head.pos_ == "NOUN":  # There is a chair on the left of a table

       

                    pnoun_word = word.head

                    ################################# get conj_pnoun ########################################
                    current_pnoun = pnoun_word
                    found_conjPnoun = True

                    while found_conjPnoun:

                        found_conjPnoun = False

                        if current_pnoun.dep_ == "conj":

                            current_pnoun = pnoun_word.head
                            found_conjSubject = True

                            ########### detect type of current pnoun ################
                            model_type_conjPnoun, object_coref = detect_object_type(str(current_pnoun), object_coref)
                            if model_type_conjPnoun == 'none':
                                continue

                            ########## detect char of current pnoun #################
                            object_chars = []
                            object_chars = detect_object_char(model_type_conjPnoun, current_pnoun)
                            
                            new_pnoun_id = get_model_id(models_fullInfo, model_type_conjPnoun, object_chars)

                            pnoun_info = [model_type_conjPnoun, new_pnoun_id]
                            pnoun_list.append(pnoun_info)

                            break


                    ################################## detect pnoun type ####################################

                    model_type_mainPnoun, object_coref = detect_object_type(str(pnoun_word), object_coref)
                    if model_type_mainPnoun == 'none':
                        continue

                    ################################## get pnoun char #######################################
                    object_chars = []
                    object_chars = detect_object_char(model_type_mainPnoun, pnoun_word)
                    
                    pnoun_id = get_model_id(models_fullInfo, model_type_mainPnoun, object_chars)

                    pnoun_info = [model_type_mainPnoun, pnoun_id]
                    pnoun_list.append(pnoun_info)

                    


                elif word.head.pos_ == "VERB":  # a chair is on the left of a table

                    verb_word = word.head

                    for child_verb in verb_word.children:
                        if child_verb.dep_ == "nsubj" or child_verb.dep_ == "attr":  # a box is on the table # there is a chair in the room

                            if child_verb.pos_ == "PRON":

                                pnoun_pronoun = str(child_verb.text).lower()
                                

                                coref_pnoun = get_refrencedObject(pnoun_pronoun)
                                

                                pnounInfo = models_char.extract_models_char(coref_pnoun)
                                

                                coref_obj_word = ""
                                coref_obj_chars = []


                                for i in range(0, len(pnounInfo)):
                                    if pnounInfo[i][1] == 'boy' or pnounInfo[i][1] == 'man':
                                        if pnoun_pronoun in models_char.male_pronoun:
                                            coref_obj_word = pnounInfo[i][1]
                                            coref_pnoun_chars = pnounInfo[i][2]
                                            break
                                    elif pnounInfo[i][1] == 'girl' or pnounInfo[i][1] == 'woman':
                                        if pnoun_pronoun in models_char.female_pronoun:
                                            coref_obj_word = pnounInfo[i][1]
                                            coref_pnoun_chars = pnounInfo[i][2]
                                            break
                                    elif pnoun_pronoun in models_char.rigid_pronoun:
                                        coref_obj_word = pnounInfo[i][1]
                                        coref_pnoun_chars = pnounInfo[i][2]
                                        break


                                pnoun_id = get_model_id(models_fullInfo, coref_obj_word,coref_pnoun_chars)

                                pnoun_info = [coref_obj_word, pnoun_id]
                                pnoun_list.append(pnoun_info)

                            else:

                                pnoun_word = child_verb

                                ################################# get conj_pnoun ########################################
                                current_pnoun = pnoun_word
                                found_conjPnoun = True

                                while found_conjPnoun:

                                    found_conjPnoun = False

                                    for child_pnoun in current_pnoun.children:
                                        if child_pnoun.dep_ == "conj":
                                            current_pnoun = child_pnoun
                                            found_conjSubject = True

                                            ########### detect type of current pnoun ################
                                            model_type_conjPnoun, object_coref = detect_object_type(str(current_pnoun),
                                                                                                    object_coref)
                                            if model_type_conjPnoun == 'none':
                                                continue

                                            ########## detect char of current pnoun #################
                                            object_chars = []
                                            object_chars = detect_object_char(model_type_conjPnoun, current_pnoun)
                                            
                                            new_pnoun_id = get_model_id(models_fullInfo, model_type_conjPnoun,
                                                                        object_chars)

                                            pnoun_info = [model_type_conjPnoun, new_pnoun_id]
                                            pnoun_list.append(pnoun_info)

                                            break

                                ################################## detect pnoun type ####################################

                                model_type_mainPnoun, object_coref = detect_object_type(str(pnoun_word), object_coref)
                                if model_type_mainPnoun == 'none':
                                    continue

                                ################################## get pnoun char #######################################
                                object_chars = []
                                object_chars = detect_object_char(model_type_mainPnoun, pnoun_word)
                                
                                pnoun_id = get_model_id(models_fullInfo, model_type_mainPnoun, object_chars)

                                pnoun_info = [model_type_mainPnoun, pnoun_id]
                                pnoun_list.append(pnoun_info)

                                



                #################################  find pobj ############################################
                for child in word.children:
                    if child.dep_ == "pobj":
                        child_refer_to_prep = False
                        for Child in child.children:
                            if Child.dep_ == "prep":
                                child_refer_to_prep = True
                                break
                        if not child_refer_to_prep:
                            
                            pobj = str(child)
                            pobj_word = child

                            

                            ################################## detect pnoun type ####################################
                            model_type, object_coref = detect_object_type(pobj, object_coref)
                            if model_type == 'none':
                                continue

                            ################################## get pnoun char #######################################
                            object_chars = []
                            object_chars = detect_object_char(model_type, pobj_word)
                           
                            pobj_id = get_model_id(models_fullInfo, model_type, object_chars)

                            ######################################### add new relation ##############################

                            for i in range(0,len(pnoun_list)):
                                rel = [current_prep, pnoun_list[i][0], pnoun_list[i][1], model_type, pobj_id]
                                relations.append(rel)


            elif (word.pos_ == "ADP") and (str(word) == "of") and (str(word.head) in rel_avail):

                current_prep = str(word.head)

                

                pnoun_word = word
                pobj_word = word

                pnoun_list = []

                #################################### find pnoun #########################################
                current_word = word

                word_in_on = current_word.head.head

                if word_in_on.head.pos_ == "NOUN":  # There is a chair on the left of a table

                    pnoun_word = word_in_on.head

                    ################################# get conj_pnoun ########################################
                    current_pnoun = pnoun_word
                    found_conjPnoun = True

                    while found_conjPnoun:


                        found_conjPnoun = False

                        if current_pnoun.dep_ == "conj":

                            current_pnoun = pnoun_word.head
                            found_conjSubject = True

                            ########### detect type of current pnoun ################
                            model_type_conjPnoun, object_coref = detect_object_type(str(current_pnoun),object_coref)
                            if model_type_conjPnoun == 'none':
                                continue

                            ########## detect char of current pnoun #################
                            object_chars = []
                            object_chars = detect_object_char(model_type_conjPnoun, current_pnoun)
                            
                            new_pnoun_id = get_model_id(models_fullInfo, model_type_conjPnoun, object_chars)

                            pnoun_info = [model_type_conjPnoun, new_pnoun_id]
                            pnoun_list.append(pnoun_info)

                            break

                    ################################## detect pnoun type ####################################

                    model_type_mainPnoun, object_coref = detect_object_type(str(pnoun_word), object_coref)
                    if model_type_mainPnoun == 'none':
                        continue

                    ################################## get pnoun char #######################################
                    object_chars = []
                    object_chars = detect_object_char(model_type_mainPnoun, pnoun_word)
                    
                    pnoun_id = get_model_id(models_fullInfo, model_type_mainPnoun, object_chars)

                    pnoun_info = [model_type_mainPnoun, pnoun_id]
                    pnoun_list.append(pnoun_info)

                    


                elif  word_in_on.head.pos_ == "VERB": # a chair is on the left of a table

                    verb_word = word_in_on.head

                    for child_verb in verb_word.children:
                        if child_verb.dep_ == "nsubj" or child_verb.dep_ == "attr":  # a box is on the table # there is a chair in the room

                            if child_verb.pos_ == "PRON":

                                pnoun_pronoun = str(child_verb.text).lower()
                                

                                coref_pnoun = get_refrencedObject(pnoun_pronoun)
                                

                                pnounInfo = models_char.extract_models_char(coref_pnoun)
                                

                                coref_obj_word = ""
                                coref_obj_chars = []


                                for i in range(0, len(pnounInfo)):
                                    if pnounInfo[i][1] == 'boy' or pnounInfo[i][1] == 'man':
                                        if pnoun_pronoun in models_char.male_pronoun:
                                            coref_obj_word = pnounInfo[i][1]
                                            coref_pnoun_chars = pnounInfo[i][2]
                                            break
                                    elif pnounInfo[i][1] == 'girl' or pnounInfo[i][1] == 'woman':
                                        if pnoun_pronoun in models_char.female_pronoun:
                                            coref_obj_word = pnounInfo[i][1]
                                            coref_pnoun_chars = pnounInfo[i][2]
                                            break
                                    elif pnoun_pronoun in models_char.rigid_pronoun:
                                        coref_obj_word = pnounInfo[i][1]
                                        coref_pnoun_chars = pnounInfo[i][2]
                                        break

                                pnoun_id = get_model_id(models_fullInfo, coref_obj_word,coref_pnoun_chars)

                                pnoun_info = [coref_obj_word, pnoun_id]
                                pnoun_list.append(pnoun_info)

                            else:

                                
                                pnoun_word = child_verb

                                ################################# get conj_pnoun ########################################
                                current_pnoun = pnoun_word
                                found_conjPnoun = True

                                while found_conjPnoun:

                                    found_conjPnoun = False

                                    for child_pnoun in current_pnoun.children:
                                        if child_pnoun.dep_ == "conj":
                                            current_pnoun = child_pnoun
                                            found_conjSubject = True

                                            ########### detect type of current pnoun ################
                                            model_type_conjPnoun, object_coref = detect_object_type(str(current_pnoun),
                                                                                                    object_coref)
                                            if model_type_conjPnoun == 'none':
                                                continue

                                            ########## detect char of current pnoun #################
                                            object_chars = []
                                            object_chars = detect_object_char(model_type_conjPnoun, current_pnoun)
                                            
                                            new_pnoun_id = get_model_id(models_fullInfo, model_type_conjPnoun,
                                                                        object_chars)

                                            pnoun_info = [model_type_conjPnoun, new_pnoun_id]
                                            pnoun_list.append(pnoun_info)

                                            break


                                ################################## detect pnoun type ####################################

                                model_type_mainPnoun, object_coref = detect_object_type(str(pnoun_word), object_coref)
                                if model_type_mainPnoun == 'none':
                                    continue

                                ################################## get pnoun char #######################################
                                object_chars = []
                                object_chars = detect_object_char(model_type_mainPnoun, pnoun_word)
                                
                                pnoun_id = get_model_id(models_fullInfo, model_type_mainPnoun, object_chars)

                                pnoun_info = [model_type_mainPnoun, pnoun_id]
                                pnoun_list.append(pnoun_info)

                                



                #################################  find pobj ############################################
                for child in word.children:
                    if child.dep_ == "pobj":
                        child_refer_to_prep = False
                        for Child in child.children:
                            if Child.dep_ == "prep":
                                child_refer_to_prep = True
                                break
                        if not child_refer_to_prep:
                            
                            pobj = str(child)
                            pobj_word = child

                            

                            ################################## detect pnoun type ####################################
                            model_type, object_coref = detect_object_type(pobj, object_coref)
                            if model_type == 'none':
                                continue

                            ################################## get pnoun char #######################################
                            object_chars = []
                            object_chars = detect_object_char(model_type, pobj_word)
                            
                            pobj_id = get_model_id(models_fullInfo, pobj, object_chars)

                            ######################################### add new relation ##############################
                            for i in range(0,len(pnoun_list)):
                                rel = [current_prep, pnoun_list[i][0], pnoun_list[i][1], model_type, pobj_id]
                                relations.append(rel)

                ###########################################################################################
        #displacy.serve(parsed_sentence, style='dep')

    return relations
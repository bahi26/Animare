'''
import logging;
logging.basicConfig(level=logging.INFO)
import neuralcoref
'''
import spacy
import neuralcoref
from spacy import displacy
from colour import Color
from nltk.stem import WordNetLemmatizer
import re
import models_char






nlp = spacy.load('en')
neuralcoref.add_to_pipe(nlp)

object_coref_list =[]

#################### action_category ####################
verb_noObject = ['dance','clap','jump']                                   #cat_num =1
verb_prep = ['walk','talk','move','sit','sleep','wave','run']            #cat_num=2
verb_oneObject= ['kick','hit','push']                      #cat_num=3
verb_twoObject= ['shoot']                                   #cat_num=4


#########################################################
count_char = ['first','second','third','fourth','fifth','sixth','seventh','eighth','ninth','tenth']
#########################################################

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


def get_objectCoref_map(input_text):

    doc=nlp(input_text)
    for i in range(0, len(doc._.coref_clusters)):
        clusters_coref = doc._.coref_clusters
        object_coref = doc._.coref_clusters[i].mentions[-1]._.coref_cluster.main


        object_coref_lst = str(object_coref).split(" ")

        if str(object_coref_lst[0]).lower() == "the":
            object_coref_lst[0] = "a"
            object_coref = ' '.join(object_coref_lst)

        ###### search for the pronoun ######
        pronoun_word=""
        for k in range(0,len(clusters_coref[i])):
            if (str(clusters_coref[i][k]).lower() in models_char.male_pronoun) or (str(clusters_coref[i][k]).lower() in models_char.female_pronoun) or (str(clusters_coref[i][k]).lower() in models_char.rigid_pronoun):
                pronoun_word = str(clusters_coref[i][k]).lower()
                object_coref_list.append((str(object_coref).lower(), pronoun_word))


##################################################################################################
def get_refrencedObject(pronoun):

    for i in range(0,len(object_coref_list)):
        
        if  object_coref_list[i][1] == pronoun:
            return object_coref_list[i][0]

##################################################################################################
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


def extract_models_actions(input_text,models_fullInfo):

    

    object_coref = models_char.get_coref(input_text)

    get_objectCoref_map(input_text)

    

    lemmatizer = WordNetLemmatizer()
    tokinized_sentences = []
    doc = nlp(input_text)

    for sent in doc.sents:
        tokinized_sentences.append(str(sent.text))


    models_actions = []

    sentence_index = -1

    for sent in doc.sents:
        
        sentence_index += 1

        tokens_in_currentSentence = []

        for word in sent:
            tokens_in_currentSentence.append(str(word))

            verb = subj = obj = ""

            if word.pos_ == "VERB" and  ((lemmatizer.lemmatize(str(word), 'v') in verb_noObject ) or (lemmatizer.lemmatize(str(word), 'v') in verb_prep) or (lemmatizer.lemmatize(str(word), 'v') in verb_oneObject) or (lemmatizer.lemmatize(str(word), 'v') in verb_twoObject) ):
                verb = lemmatizer.lemmatize(str(word), 'v')


                obj_word = word
                subj_word = word

                subj_id = -1
                obj1_id = -1
                obj2_id = -1

                ###################### find objects ##################
                if (verb in verb_oneObject) or (verb in verb_twoObject):
                    for child in word.children:

                        if child.dep_ == "dobj":

                            if child.pos_ == "PRON":

                                obj_pronoun = str(child.text).lower()
                                
                                coref_obj = get_refrencedObject(obj_pronoun)
                       
                                objInfo = models_char.extract_models_char(coref_obj)                

                                coref_obj_word = ""
                                coref_obj_chars = []

                                for i in range(0, len(objInfo)):
                                    if objInfo[i][1] == 'boy' or objInfo[i][1] == 'man':
                                        if obj_pronoun in models_char.male_pronoun:
                                            coref_obj_word = objInfo[i][1]
                                            coref_obj_chars = objInfo[i][2]
                                            break
                                    elif objInfo[i][1] == 'girl' or objInfo[i][1] == 'woman':
                                        if obj_pronoun in models_char.female_pronoun:
                                            coref_obj_word = objInfo[i][1]
                                            coref_obj_chars = objInfo[i][2]
                                            break
                                    elif obj_pronoun in models_char.rigid_pronoun:
                                        coref_obj_word = objInfo[i][1]
                                        coref_obj_chars = objInfo[i][2]
                                        break


                                obj1_id = get_model_id(models_fullInfo, coref_obj_word, coref_obj_chars)


                            else:

                                obj_word = child
                                ################################## detect object type ####################################
                                model_type, object_coref = detect_object_type(str(obj_word), object_coref)
                                if model_type == 'none':
                                    continue
                                ################################## detect obj_chars ###########################################
                                object_chars = []
                                object_chars = detect_object_char(model_type, obj_word)
                                
                                obj1_id = get_model_id(models_fullInfo, model_type, object_chars)

                if (verb in verb_prep) or (verb in verb_twoObject):    #----------------------> add coref


                    for child in word.children:

                        if child.dep_ == "prep":
                            
                            current_word = child
                            for child_current_word in current_word.children:
                                if child_current_word.dep_ == "pobj":

                                    
                                    if child_current_word.pos_ == "PRON":

                                        obj_pronoun = str(child_current_word.text).lower()
                                        

                                        coref_obj = get_refrencedObject(obj_pronoun)
                                        

                                        objInfo = models_char.extract_models_char(coref_obj)
                                        

                                        coref_obj_word = ""
                                        coref_obj_chars = []

                                        for i in range(0, len(objInfo)):
                                            if objInfo[i][1] == 'boy' or objInfo[i][1] == 'man':
                                                if obj_pronoun in models_char.male_pronoun:
                                                    coref_obj_word = objInfo[i][1]
                                                    coref_obj_chars = objInfo[i][2]
                                                    break
                                            elif objInfo[i][1] == 'girl' or objInfo[i][1] == 'woman':
                                                if obj_pronoun in models_char.female_pronoun:
                                                    coref_obj_word = objInfo[i][1]
                                                    coref_obj_chars = objInfo[i][2]
                                                    break
                                            elif obj_pronoun in models_char.rigid_pronoun:
                                                coref_obj_word = objInfo[i][1]
                                                coref_obj_chars = objInfo[i][2]
                                                break

                                      
                                        obj_id = get_model_id(models_fullInfo, coref_obj_word, coref_obj_chars)

                                        if verb in verb_twoObject:
                                            
                                            obj2_id = obj_id
                                        else:
                                            
                                            obj1_id = obj_id
                                            


                                    else :

                                        obj_word = child_current_word

                                        ################################## detect object type ####################################
                                        model_type, object_coref = detect_object_type(str(obj_word), object_coref)
                                        if model_type == 'none':
                                            continue
                                        ################################## detect obj_chars ###########################################
                                        object_chars = []
                                        object_chars = detect_object_char(model_type, obj_word)
                                        
                                        obj_id = get_model_id(models_fullInfo, model_type, object_chars)

                                        if verb in verb_twoObject:
                                            
                                            obj2_id = obj_id
                                        else:
                                            obj1_id = obj_id


                 
                ############################################## find subjects ###############################################

                found_subj = False

                
                for child in word.children:
                    ######### first subject ###############
                    if child.dep_ == "nsubj":

                        

                        found_subj = True

                        found_conjSubject = True
                        current_subject = child

                        while found_conjSubject :

                            

                            ###### check if it is a PRON , then get its coreference , otherwise put it as it is ######
                            ### get the num of pronouns preceding it from the start
                            if current_subject.pos_ == "PRON":

                                subj_pronoun = str(current_subject.text).lower()
                                

                                coref_subj = get_refrencedObject(subj_pronoun)
                                

                                subjInfo = models_char.extract_models_char(coref_subj)
                                

                                coref_subj_word = ""
                                coref_subj_chars = []

                                for i in range(0, len(subjInfo)):
                                    if subjInfo[i][1] == 'boy' or subjInfo[i][1] == 'man':
                                        if subj_pronoun in models_char.male_pronoun:
                                            coref_subj_word = subjInfo[i][1]
                                            coref_subj_chars = subjInfo[i][2]
                                            break
                                    elif subjInfo[i][1] == 'girl' or subjInfo[i][1] == 'woman':
                                        if subj_pronoun in models_char.female_pronoun:
                                            
                                            coref_subj_word = subjInfo[i][1]
                                            coref_subj_chars = subjInfo[i][2]
                                            break


                                    elif subj_pronoun in models_char.rigid_pronoun:
                                            coref_subj_word = subjInfo[i][1]
                                            coref_subj_chars = subjInfo[i][2]
                                            break

                               
                                coref_subj_id = get_model_id(models_fullInfo, coref_subj_word, coref_subj_chars)

                                ################################# Add a new action to action list #######################

                                # action --> cat_num,verb_name,subj_id,obj1_id,obj2_id,action_pos
                                if verb in verb_noObject:
                                    action = (1, verb, coref_subj_id, obj1_id, obj2_id, word.i)
                                elif verb in verb_prep:
                                    action = (2, verb, coref_subj_id, obj1_id, obj2_id, word.i)
                                elif verb in verb_oneObject:
                                    action = (3, verb, coref_subj_id, obj1_id, obj2_id, word.i)
                                else:
                                    action = (4, verb, coref_subj_id, obj1_id, obj2_id, word.i)

                                models_actions.append(action)

                                ###### check if there is a conj subject ########

                                found_conjSubject = False

                                for child_subj in current_subject.children:
                                    if child_subj.dep_ == "conj":
                                        current_subject = child_subj
                                        found_conjSubject = True
                                        break

                            else:

                                subj_word = current_subject
                                ################################## detect subj type ####################################
                                model_type, object_coref = detect_object_type(str(subj_word), object_coref)
                                if model_type == 'none':
                                    continue
                                ################################# find subj chars #######################################
                                object_chars = []
                                object_chars = detect_object_char(model_type, subj_word)
                                
                                subj_id = get_model_id(models_fullInfo, model_type, object_chars)

                                ################################# Add a new action to action list #######################

                                # action --> cat_num,verb_name,subj_id,obj1_id,obj2_id,action_pos
                                if verb in verb_noObject:
                                    action = (1, verb, subj_id, obj1_id, obj2_id, word.i)
                                elif verb in verb_prep:
                                    action = (2, verb, subj_id, obj1_id, obj2_id, word.i)
                                elif verb in verb_oneObject:
                                    action = (3, verb, subj_id, obj1_id, obj2_id, word.i)
                                else:
                                    action = (4, verb, subj_id, obj1_id, obj2_id, word.i)

                                models_actions.append(action)

                                ###### check if there is a conj subject ########

                                found_conjSubject =False

                                for child_subj in current_subject.children:
                                    if child_subj.dep_ == "conj":
                                        current_subject = child_subj
                                        found_conjSubject = True
                                        break

                ######################################## if there are conj verbs of the same subject ######################

                if found_subj == False:

                    

                    current_verb = word
                    found_conj_verb = False

                    while ( (found_subj) == False ) and (current_verb.head.pos_ == "VERB") and (current_verb.head.i < current_verb.i) :

                        
                        found_conj_verb = True

                        current_verb = current_verb.head

                        for child_verb in current_verb.children:
                            if child_verb.dep_ == "nsubj":
                                found_subj = True
                                break

                    if found_conj_verb == True: ### conj_verb  --> copy only the subject
                        for verb_info in models_actions:
                            if verb_info[1] == lemmatizer.lemmatize(str(current_verb), 'v'):
                                subj_id = verb_info[2]

                    else:  # while playing --> copy all the information (subject and object(s) )
                        for verb_info in models_actions:
                            if verb_info[1] == lemmatizer.lemmatize(str(current_verb), 'v'):
                                subj_id = verb_info[2]
                                obj1_id = verb_info[3]
                                obj2_id = verb_info[4]

                    ################################# Add a new action to action list #######################

                    # action --> cat_num,verb_name,subj_id,obj1_id,obj2_id,action_pos
                    if verb in verb_noObject:
                        action = (1, verb, subj_id, obj1_id, obj2_id, word.i)
                    elif verb in verb_prep:
                        action = (2, verb, subj_id, obj1_id, obj2_id, word.i)
                    elif verb in verb_oneObject:
                        action = (3, verb, subj_id, obj1_id, obj2_id, word.i)
                    else:
                        action = (4, verb, subj_id, obj1_id, obj2_id, word.i)


                    models_actions.append(action)


    return models_actions
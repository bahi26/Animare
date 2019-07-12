from models_char import extract_models_char
from obj_relations import Objs_relations
from model_actions import extract_models_actions
from Scene_Inference import extract_totalInference
from Sequence import *


def nlp_module(input_text):

    ####################### files for the following modules ###########################
    file_models_char = open("models_char.txt", "w")
    file_models_actions = open("model_actions.txt", "w")
    file_models_relations = open("models_relations.txt", "w")
    ##################################################################################
    models_info = extract_models_char(input_text)
    relations_models = Objs_relations(input_text, models_info)
    infered_models,infered_relations=extract_totalInference(models_info, relations_models)
    print("infered_models : ",infered_models)
    print("infered_relations : ",infered_relations)
    model_actions = extract_models_actions(input_text, models_info)

    ############## add infered models and relations to models info and models relations #############
    for i in range(0,len(infered_models)):
        models_info.append(infered_models[i])


    for i in range(0,len(infered_relations)):
        relations_models.append(infered_relations[i])

    ########################### write model chars #################################################
    for i in range(0, len(models_info)):
        current_model_name = models_info[i][1]
        current_model_chars = models_info[i][2]
        file_models_char.write(current_model_name + " ")

        if len(current_model_chars) == 4:  # human
            for j in range(0, len(current_model_chars) - 1):
                if j == 0 and current_model_chars[j] == -1:  # not mentioned age then set it not old
                    current_model_chars[j] = 0
                    file_models_char.write(str(current_model_chars[j]) + " ")
                elif j == 2 and current_model_chars[j] == -1:  # not mentioned height then set it meduim height
                    current_model_chars[j] = 1
                    file_models_char.write(str(current_model_chars[j]) + " ")
                else:
                    file_models_char.write(str(current_model_chars[j]) + " ")


        else:
            for j in range(0, len(current_model_chars) - 1):
                if j == 1 and current_model_chars[j] == -1:  # not mentioned size then set it meduim size
                    current_model_chars[j] = 1
                    file_models_char.write(str(current_model_chars[j]) + " ")
                else:
                    file_models_char.write(str(current_model_chars[j]) + " ")

        file_models_char.write(str(models_info[i][3]) + "\n")
    file_models_char.close()
    ########################## write model actions #######################
    for i in range(0, len(model_actions)):
        file_models_actions.write(model_actions[i][1] + " " + str(model_actions[i][2]) + " " + str(
                model_actions[i][3]) + " " + str(model_actions[i][4]) + " " + str(model_actions[i][5]) + "\n")
    file_models_actions.close()
    ########################### write models relations ####################
    for i in range(0, len(relations_models)):
        file_models_relations.write(
            relations_models[i][0] + " " + relations_models[i][1] + " " + str(relations_models[i][2]) + " " +
            relations_models[i][3] + " " + str(relations_models[i][4]) + "\n")
    file_models_relations.close()

    #############################  Extract action sequence ###############
    sequence(input_text)
    ######################################################################

    return
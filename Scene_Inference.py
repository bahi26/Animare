import pandas as pd

models_needSupport = ['bed','plate','food','television','box','computer','laptop','bottle','cup','knife','car']

def support_inference (current_explicit_object):
    df = pd.read_csv("supportParentGivenChild.csv", sep=",")
    #print(df.head())

    #print(current_explicit_object)
    df_suggested_supports = df[df["child"] == current_explicit_object]
    #print("******", df_suggested_supports)
    max_prob = df_suggested_supports["p(parent|child)"].max()
    #print("max_prob : ", max_prob)
    infere_support = df_suggested_supports[df_suggested_supports["p(parent|child)"] == max_prob]
    infered_object_name = str(infere_support["parent"].values[0]).lower()
    infered_relation = infere_support["relation"].values[0]

    print("infered_object : ", infered_object_name)
    print("infered relation : ", infered_relation)



    return infered_object_name,infered_relation


def extract_totalInference(explicit_models_info,explicit_relations_models):

    infered_models = []
    infered_relations=[]

    ########################### scene_Inference #####################################
    total_number_objects = len(explicit_models_info)
    last_id = explicit_models_info[total_number_objects - 1][3]

    all_explicit_objects_names = []
    all_infered_objects_names = []

    for explicit_object_info in explicit_models_info:
        all_explicit_objects_names.append(explicit_object_info[1])

    for explicit_object_info in explicit_models_info:

        explicit_object_name = explicit_object_info[1]
        explicit_object_id = explicit_object_info[3]

        if explicit_object_name in models_needSupport:
            infered_object, infered_relation = support_inference(explicit_object_name)

            if (infered_object not in all_explicit_objects_names) and (infered_object not in all_infered_objects_names):

                ############  add this object to the scene ##########

                last_id = last_id + 1

                infered_models.append([infered_object, infered_object, ["none", -1,"first"], last_id])
                all_infered_objects_names.append(infered_object)

                ###########  add a new relation between this infered object and the explicit object #######

                rel = [infered_relation, explicit_object_name, explicit_object_id, infered_object, last_id]
                infered_relations.append(rel)

            else:

                ##### the infered object is in the scene , so search for an explicit relation , if not found add the infered relation ####

                found_relation = False

                for explicit_rel in explicit_relations_models:
                    if (explicit_rel[1] == explicit_object_name) and (explicit_rel[3] == infered_object):
                        found_relation = True
                        break

                if not found_relation:

                    ################################# get infered object id ######################################
                    infered_object_id = -1
                    found_in_explicit=False
                    for explicit_object_info in explicit_models_info:
                        if explicit_object_info[1] == infered_object:
                            infered_object_id = explicit_object_info[3]
                            found_in_explicit=True
                            break

                    if not found_in_explicit:
                        for infered_object_info in infered_models:
                            if infered_object_info[1] == infered_object:
                                infered_object_id = infered_object_info[3]
                                break


                    rel = [infered_relation, explicit_object_name, explicit_object_id, infered_object,
                           infered_object_id]
                    infered_relations.append(rel)

    return infered_models,infered_relations
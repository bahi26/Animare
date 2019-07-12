import re
import Graph
Actions=[]
#initial={"Location":[0,0,0],"State":"idle"}
#Goal={"Location":[0,5,0],"State" :"sit"}
initial={}
Goal={}
class action:
    def __init__(self, id, conditions,effect):
        self.id = id
        self.effect=effect
        self.conditions = conditions
    def meet_conditions(self,condition_list):
        for key, value in self.conditions.items():
            if key in condition_list:
                if self.conditions[key]!=condition_list[key]:
                    return False
            else:
                return False
        return True
def populate ():
    File = open("Actions.txt", "r")
    line = File.read()
    regex = r"\((.*?)\)"
    matches = re.finditer(regex, line, re.MULTILINE | re.DOTALL)
    for matchNum, match in enumerate(matches):
        temp_action_data = []
        temp1=match.group(1)
        action_data = temp1.split("\n")
        action_name = action_data[0].replace(",", "")
        fluents = action_data[1].replace("PRECOND:", "").split(",")
        pre_map = {}
        for fluent in fluents:
            if "~" in fluent:
                pre_map[fluent.replace("~", "")] = -1
            else:
                pre_map[fluent] = 1
        #temp_action_data.append(pre_map)

        # populating effects
        fluents = action_data[2].replace("EFFECT:", "").split(",")
        effect_map = {}
        for fluent in fluents:
            if "~" in fluent:
                effect_map[fluent.replace("~", "")] = -1
            else:
                effect_map[fluent] = 1
        #temp_action_data.append(effect_map)
        temp=action(action_name,pre_map,effect_map)
        #Actions[action_name] = temp_action_data
        Actions.append(temp)
        #print(temp.effect,temp.conditions,temp.id)
def Interference(preCond,Effects,state_num):
    literals = []
    for act, precond in preCond.items():
        for key, value in precond.items():
            for otherAct, otherEffect in Effects.items():
                if key in otherEffect:
                    if precond[key] != otherEffect[key]:
                        if any([state_num, otherAct, act] == x for x in literals)or act==otherAct:
                            continue
                        else:
                            literals.append([state_num, act, otherAct])
                            #print("Interference  at state ", state_num, act, otherAct)


def competingNeeds(states,state_num):
    literals = []
    for act, precond in states.items():
        for key, value in precond.items():
            for otherAct, otherPrecond in states.items():
                if key in otherPrecond:
                    if precond[key] != otherPrecond[key]:
                        if any([state_num, otherAct, act] == x for x in literals):
                            continue
                        else:
                            literals.append([state_num, act, otherAct])
                            #print("Competing needs  at state ", state_num, act, otherAct)

def negatedEffects(states,state_num):
    literals=[]
    for act,effect in states.items():
        for key,value in effect.items():
            for otherAct,otherEffect in states.items():
                if key in otherEffect:
                    if effect[key]!=otherEffect[key]:
                        if any([state_num,otherAct,act] == x for x in literals):
                            continue
                        else:
                            literals.append([state_num,act,otherAct])
                            #print("Inconsistent Effects at state ", state_num, act, otherAct)



"""""

    for literal in states:
        for key, value in literal.items():
            if key in literals:
                if literals[key]!= literal[key]:
                    print ("Inconsistent Effects at state ",state_num,key,'~'+key)
            else:
                literals[key]=literal[key]
   # print(literals)

"""

def Plan(State,Goal):

    queue = [State]
    #tempState.append(State.data)
    i = 0
    execAction = []
    while (queue and i < 77):
        initialState = queue.pop(0)
        if initialState.chechGoal(Goal):
            return initialState
        preConditions = {}
        Effects = {}
        #print("state number",i)
        for a,v in State.data.items():
           # print(a,"------------------------------------------------",{a:v})
            Effects[a] = {a:v}
            preConditions[a] = {a:v}
        # tempState.append(initialState.data)
        for temp in Actions:
            if temp.meet_conditions(initialState.data):
                newCond = initialState.data.copy()
                for key, value in temp.effect.items():
                    newCond[key] = temp.effect[key]
                #print(temp.conditions,"----------------------------",temp.id,"---------------------------------------------",temp.effect)
                State = Graph.node(newCond, temp, initialState)
                Effects[temp.id]=temp.effect
                preConditions[temp.id]=temp.conditions
                #tempState.append(temp.effect)
                execAction.append(temp)
                queue.append(State)
            # print(State.action.id)
        # states[i] = [tempState]
        #
        negatedEffects(Effects, i)
        competingNeeds(preConditions, i)
        Interference(preConditions,Effects,i)
        # print(tempState)
        i += 1
    return None


def FromGEngine(intial,goal):
    initialS={}
    state=intial["State"]
    initialS[state]=1
    if(intial["Location"]!=goal["Location"]):
        initialS["Location"]=-1
    else:
        initialS["Location"]=1
    GoalS={}
    GoalS["Location"]=1
    GoalState=goal["State"]
    GoalS[GoalState]=1
    populate()
    initialState=Graph.node(initialS,None)
    temp5=Plan(initialState,GoalS)
    Sequence_Plan=[]
    while(temp5!=None and temp5.action!=None):
        Sequence_Plan.append(temp5.action.id)
        temp5=temp5.pre_node

    Sequence_Plan.reverse()
    print(Sequence_Plan)
    return Sequence_Plan
"""""
ini={}
ini["Location"]=1
ini["State"]="idle"
gol={}
gol["Location"]=2
gol["State"]="sit"
FromGEngine(ini,gol)
"""
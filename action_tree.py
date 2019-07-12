import copy
map={}
class acion_node:
    def __init__(self,subject,action,frame):
        self.action=action
        self.frame=frame
        self.subject=subject

def populate():
    input=open('action_tree_input.txt','r')
    lines = input.readlines()
    for line in lines:
        line=line.split(':')
        action=line[0].split()
        subactions=line[1].split(',')
        arr=[]
        for subaction in subactions:
            subaction=subaction.split()
            a=acion_node(subaction[0],subaction[1],subaction[2])
            arr.append(a)

        if(len(action)>2):
            inst=[arr,action[0],action[2]]
        else:
            inst=[arr,action[0]]

        map[action[1]]=inst

def parse(action):
    action=action.split()
    data=map[action[1]]
    arr=copy.deepcopy(data[0])
    for d in arr:
        print(type(d))
        if d.subject==data[1]:
            d.subject=action[0]
        else:
            d.subject=action[2]
    return arr
populate()

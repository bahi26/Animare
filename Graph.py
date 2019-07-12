class node:
    def __init__(self,data,action,pre=None):
        self.data=data
        self.action=action
        self.pre_node=pre
    def chechGoal(self,Goal):
        for key, value in Goal.items():
            if key in self.data:
                if self.data[key] != Goal[key]:
                    return False
            else:
                return False
        return True
def parse(new_node):
    arr=[new_node]
    temp=new_node
    while temp.pre != None:
        temp=new_node.pre
        arr.append(temp)
    return arr
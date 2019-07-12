models=['table','chair',
        'computer','laptop',
        'tv','television',
        'toy','car',
        'bat','bed',
        'ball','sandwich',
        'plate','dish',
        'gun','piano',
        'desk','couch','sofa'
        'box','knife',
        'cup','bottle','food']
inv_math=[0.00,0.00,
          .00,.00,
          .00,.00,
          5,0.000,
          4,0.000,
          4,5,
          3,3,
          1,0.000,
          0.00,0.00,0.00,
          .0,4,
          .03,.03,4]
e=[.01,.01,
   .01,.1,
   .01,.01,
   .01,0.1,
   .01,.09,
   4,.01,
   .1,.1,
   .01,.1,
   .2,.01,.01,
   .1,.01,
   .01,.01,.01
   ]
environments=['street','playground','kitchen','room']
def human_path(name,age,hairColor):
    if is_human(name)==False:
        return None,None,None
    if (name =='boy'):
        if hairColor=='red' or hairColor=='none':
            return 'boy','none' ,.01
        else : return 'boy',hairColor ,.01
    if (name == 'girl'):
        if hairColor=='blond' or hairColor=='yellow' or hairColor=='none':
            return 'girl','none' ,.01
        else : return 'girl',hairColor ,.01
    if (name == 'man'):
        if(age=='0'):
            if hairColor == 'black' or hairColor == 'brunette' or hairColor == 'dark' or hairColor == 'none':
                return 'man', 'none' ,.005
            else:
                return 'man', hairColor ,.005
        else :
            return 'old_man','none' ,.01
    if (name == 'woman'):
        if(age=='0'):
            if hairColor == 'black' or hairColor == 'brunette' or hairColor == 'dark' or hairColor == 'none':
                return 'woman', 'none' ,.005
            else:
                return 'woman', hairColor ,.005
        else:
            if hairColor == 'none':
                return 'old_woman', 'gray' ,.005
            else:
                return 'old_woman', hairColor ,.005

def exists(name,type):
    if type == True:
        if name in models:
            return True
    else :
        if name in environments:
            return True
    return False

def is_human(name):
    if(name=='man' or name=='woman' or name=='girl' or name=='boy'):
        return True
    return False
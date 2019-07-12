import numpy as np
import bpy
import math
aaaa=open("actionssss.txt","w")
def collision_detection(object1,object2):
    i=j=1
    while i < len(object1['AABB']):
        while j < len(object2['AABB']):
            if collision_detection2(object1['AABB'][i],object2['AABB'][j],object1.location,object2.location):
                return True,i,j
            j+=1
        i+=1
    return False,0,0
def collision_detection2(AABB1,AABB2,location1,location2):
   
    if(AABB1[0][0]+location1[0]>AABB2[1][0]+location2[0] or
            AABB1[1][0]+location1[0]<AABB2[0][0]+location2[0]):
        return False
    if (AABB1[0][1]+location1[1] > AABB2[1][1]+location2[1] or
            AABB1[1][1]+location1[1] < AABB2[0][1]+location2[1]):
        return False
    if (AABB1[0][2]+location1[2] > AABB2[1][2]+location2[2] or
            AABB1[1][2]+location1[2] < AABB2[0][2]+location2[2]):
        return False
    return True

def ResolveCollision(object1,object2,aabb1,aabb2):

    relative_velocity=np.array(object1['velocity'])-np.array(object2['velocity'])
    if np.array_equal(object1['velocity'],object2['velocity']):
        return relative_velocity
    r=min(object1['e'],object2['e'])
    try:
       
        j = -(1 + r) * relative_velocity / (object1['inv_mass'] + object2['inv_mass'])
    except ZeroDivisionError:
        j=(0.0,0.0,0.0)
    normal1=calculate_normal(object1,object2,aabb1,aabb2)
    
    x2=x1=[1.0,1.0,1.0]
    x=[0.0,0.0,0.0]
    for i in range(len(x)) :
        if (relative_velocity[i])!=0:
            x[i]=relative_velocity[i]/abs(relative_velocity[i])
    x=np.array(x)

    object1['velocity']=np.array(object1['velocity'])-object1['inv_mass']*j*normal1*x*x1

    object2['velocity']=np.array(object2['velocity'])+object2['inv_mass']*j*normal1*x*x2


def apply_gravity(object):
    try:
        gravity=np.array([0,0,-9.8])
    except ZeroDivisionError:
        gravity=np.array([0,0,0])
   
    dimensions=object.dimensions
    area=dimensions[0]*dimensions[1]
    if object['velocity'][2] !=0:
        air_resistance =np.array([0.0,0.0,-1*.5* 1.2*4.7*area*object['velocity'][2]/abs(object['velocity'][2])])
    else:
        air_resistance=np.array([0.0,0.0,0.0])
    a=air_resistance*object['inv_mass']

    if a[2]+gravity[2]>0:
        a[2]/=3
    object['a']=(object['a']+(a+gravity))

def apply_speed(object):
    object['velocity'][2]+= object['a'][2]*(1/25)

def resitance(object):
    if object['inv_mass']==0 or object['velocity']==[0.0,0.0,0.0]:
        return
   
    ix=object['velocity'][0]
    if(ix!=0):
        cx=ix/abs(ix)
        x=object['velocity'][0]-(4/25)/object['inv_mass']*cx
        if (ix != 0):
            if(x/ix<0):
                x=0
        object['velocity'][0]=x
    iy=object['velocity'][1]
    if (iy != 0):
        cy = iy / abs(iy)
        y = object['velocity'][1]-(4 / 25)/object['inv_mass']*cy
        if (iy != 0):
            if (y / iy < 0):
                y = 0
        object['velocity'][1]=y
    

def calculate_normal(object1,object2,aabb1,aabb2):
    if (object1['AABB'][aabb1][1][0] + object1.location[0] > object2['AABB'][aabb2][1][0] + object2.location[0]):
        x_overlap=min(object1['AABB'][aabb1][1][0]-object1['AABB'][aabb1][0][0],
                      object2['AABB'][aabb2][1][0]
                      -object2['AABB'][aabb2][0][0],
                      object2['AABB'][aabb2][1][0] + object2.location[0]-object1['AABB'][aabb1][0][0] - object1.location[0])
    else:
        x_overlap =min(object1['AABB'][aabb1][1][0]-object1['AABB'][aabb1][0][0],object2['AABB'][aabb2][1][0]-object2['AABB'][aabb2][0][0],
                       object1['AABB'][aabb1][1][0] + object1.location[0] - object2['AABB'][aabb2][0][0] - object2.location[0])
    if (object1['AABB'][aabb1][1][1] + object1.location[1] > object2['AABB'][aabb1][1][1] + object2.location[1]):
        y_overlap = min(object1['AABB'][aabb1][1][1]-object1['AABB'][aabb1][0][1],object2['AABB'][aabb2][1][1]-object2['AABB'][aabb2][0][1],
                        object2['AABB'][aabb2][1][1] + object2.location[1] - object1['AABB'][aabb1][0][1] - object1.location[1])
    else:
        y_overlap = min(object1['AABB'][aabb1][1][1]-object1['AABB'][aabb1][0][1],object2['AABB'][aabb2][1][1]-object2['AABB'][aabb2][0][1],
                        object1['AABB'][aabb1][1][1] + object1.location[1] - object2['AABB'][aabb2][0][1] - object2.location[1])
    if (object1['AABB'][aabb1][1][2] + object1.location[2] > object2['AABB'][aabb2][1][2] + object2.location[2]):
        z_overlap = min(object1['AABB'][aabb1][1][2] - object1['AABB'][aabb1][0][2],object2['AABB'][aabb2][1][2]-object2['AABB'][aabb2][0][2],
                        object2['AABB'][aabb2][1][2] + object2.location[2] - object1['AABB'][aabb1][0][2] - object1.location[2])
    else:
        z_overlap = min(object1['AABB'][aabb1][1][2]-object1['AABB'][aabb1][0][2],object2['AABB'][aabb2][1][2]-object2['AABB'][aabb2][0][2],
                        object1['AABB'][aabb1][1][2] + object1.location[2] - object2['AABB'][aabb2][0][2] - object2.location[2])
    object1.location = np.array(object1.location) + .1*np.array(object1['velocity'])/25
    object2.location = np.array(object2.location) + .1*np.array(object2['velocity'])/25
    if (object1['AABB'][aabb1][1][0] + object1.location[0] > object2['AABB'][aabb2][1][0] + object2.location[0]):
        x_overlap2 = min(object1['AABB'][aabb1][1][0]-object1['AABB'][aabb1][0][0],object2['AABB'][aabb2][1][0]-object2['AABB'][aabb2][0][0],
                         object2['AABB'][aabb2][1][0] + object2.location[0] - object1['AABB'][aabb1][0][0] - object1.location[0])
    else:
        x_overlap2 =  min(object1['AABB'][aabb1][1][0]-object1['AABB'][aabb1][0][0],object2['AABB'][aabb2][1][0]-object2['AABB'][aabb2][0][0],
                         object1['AABB'][aabb1][1][0] + object1.location[0] - object2['AABB'][aabb2][0][0] - object2.location[0])
    if (object1['AABB'][aabb1][1][1] + object1.location[1] > object2['AABB'][aabb2][1][1] + object2.location[1]):
        y_overlap2 =  min(object1['AABB'][aabb1][1][1]-object1['AABB'][aabb1][0][1],object2['AABB'][aabb2][1][1]-object2['AABB'][aabb2][0][1],
                         object2['AABB'][aabb2][1][1] + object2.location[1] - object1['AABB'][aabb1][0][1] - object1.location[1])
    else:
        y_overlap2 =  min(object1['AABB'][aabb1][1][1]-object1['AABB'][aabb1][0][1],object2['AABB'][aabb2][1][1]-object2['AABB'][aabb2][0][1],
                         object1['AABB'][aabb1][1][1] + object1.location[1] - object2['AABB'][aabb2][0][1] - object2.location[1])
    if (object1['AABB'][aabb1][1][2] + object1.location[2] > object2['AABB'][aabb2][1][2] + object2.location[2]):
        z_overlap2 =  min(object1['AABB'][aabb1][1][2]-object1['AABB'][aabb1][0][2],object2['AABB'][aabb2][1][2]-object2['AABB'][aabb2][0][2],
                         object2['AABB'][aabb2][1][2] + object2.location[2] - object1['AABB'][aabb1][0][2] - object1.location[2])
    else:
        z_overlap2 =  min(object1['AABB'][aabb1][1][2]-object1['AABB'][aabb1][0][2],object2['AABB'][aabb2][1][2]-object2['AABB'][aabb2][0][2],
                         object1['AABB'][aabb1][1][2] + object1.location[2] - object2['AABB'][aabb2][0][2] - object2.location[2])
    object1.location = np.array(object1.location) - .1*np.array(object1['velocity'])/25
    object2.location = np.array(object2.location) - .1*np.array(object2['velocity'])/25
    normal = np.array([0.0,0.0,0])

    if abs(x_overlap-x_overlap2)==0 and abs(y_overlap-y_overlap2)==0 and abs(z_overlap-z_overlap2)==0:
        return normal
    if(abs(x_overlap-x_overlap2)>abs(y_overlap-y_overlap2)):
        if(abs(x_overlap-x_overlap2)>abs(z_overlap-z_overlap2)):
            if(object1['velocity'][0]<0):
                normal=np.array([1,0.0,0.0])
            else:
                normal=np.array([-1,0,0])
        else:
            if (object1['velocity'][2] < 0):
                normal = np.array([0, 0, 1])
            else:
                normal = np.array([0, 0, -1])
    else:
        if(abs(y_overlap-y_overlap2)>abs(z_overlap-z_overlap2)):
            if(object1['velocity'][1]<0):
                normal=np.array([0,1,0])
            else:
                normal=np.array([0,-1,0])
        else:
            if (object1['velocity'][2] < 0):
                normal = np.array([0, 0, 1])
            else:
                normal = np.array([0, 0, -1])
  
    return normal
def advance(object1,minz,minx,maxx,miny,maxy):
    if np.array_equal(object1['velocity'],[0.0,0.0,0.0]):
        return
   
    object1.location[2] = np.array(object1.location[2]) + (np.array(object1['velocity'][2]) * (1 / 25))
    object1.location[0]=np.array(object1.location[0])+(np.array(object1['velocity'][0])*(1/25))
    object1.location[1] = np.array(object1.location[1]) + (np.array(object1['velocity'][1]) * (1 / 25))
    object1.rotation_euler[0]=object1.rotation_euler[0]+(np.array(object1['velocity'][0])*(1/25))
    object1.rotation_euler[1] = object1.rotation_euler[1] + (np.array(object1['velocity'][1]) * (1 / 25))
    if (object1.location[2] < minimumz(object1,minz) and equals(object1.location[2] , minimumz(object1,minz))==False):
         object1.location[2] = minimumz(object1,minz)
    if (object1.location[0] <minx-abs(object1['AABB'][0][0][0]-object1['AABB'][0][1][0])-1):
   
        object1.location[0] = minx-abs(object1['AABB'][0][0][0]-object1['AABB'][0][1][0])+.3

    if (object1.location[1] < miny - abs(object1['AABB'][0][0][1] - object1['AABB'][0][1][1])-1):
        object1.location[1] = miny - abs(object1['AABB'][0][0][1] - object1['AABB'][0][1][1])+.3


    if (object1.location[0] > maxx - abs(object1['AABB'][0][0][0] - object1['AABB'][0][1][0])):
        object1.location[0] = maxx - abs(object1['AABB'][0][0][0] - object1['AABB'][0][1][0])
        object1['velocity'][0]=-object1['velocity'][0]
        object1.rotation_euler[0] = -object1.rotation_euler[0]

    if (object1.location[1] > maxy - abs(object1['AABB'][0][0][1] - object1['AABB'][0][1][1])+1):
        object1.location[1] = maxy - abs(object1['AABB'][0][0][1] - object1['AABB'][0][1][1]-.3)


def minimumz(object,minz):
    x=minz+-object['AABB'][0][0][2]
    return x
def equals(x,y):
    if x+.0002>y and y+.0002>x:
        return True
    else:
        return False

import bpy
import Astar
import os
from math import radians
import math
import numpy as np
import planning
import physics
import action_tree
from mathutils import Vector
models_path = "models\\models"
animation_path = "models\\animations"
render_path = models_path
objectFile=open("objects.txt", "r")
environmentFile=open("environments.txt", "r")
humanFile=open("humans.txt", "r")
inputFile = open("models.txt", "r")
SeqFile = open("ActionSequence.txt", "r")
models = []
imported_actions = {}
models = []
actions = []
Sequences = []
initial_locations={}
initial_angle={}
global matrix
object_names = []
#attatching an object to a human charcter
def hold(human,object):
    p = human.pose.bones['mixamorig:RightHandThumb1'].matrix
    data = p * human.matrix_world * human.location * .05
    initial_locations[object.name]=object.location = [data[0], -data[2], data[1]]
    initial_angle[object.name]=object.rotation_euler=human.rotation_euler
    object.constraints.new(type='CHILD_OF')
    object.constraints["Child Of"].target = human
    object.constraints["Child Of"].subtarget = "mixamorig:RightHandThumb1"
    lp = human.matrix_world * p
    object.constraints["Child Of"].inverse_matrix = lp.inverted()
action_tree.populate()
toUpdateScene=[]
actions_list=[]
velocity_array={}
def angle(ang):
    if ang==0:
        return [0,-1]
    elif ang==90:
        return [-1,0]
    elif ang==180:
        return [0,1]
    else:
        return [1,0]

def applay_deformation(obj_object, color, scale):
    if(color!=None):
        color=tuple(map(float,color[0:3]))
        for f in obj_object.data.polygons:
            if obj_object.material_slots[f.material_index].material is not None:
                obj_object.material_slots[f.material_index].material.diffuse_color = color
    obj_object.scale = scale

def applay_human_deformation(obj_object, haircolor, scale):
    for area in bpy.context.screen.areas:  # iterate through areas in current screen
        if area.type == 'VIEW_3D':
            for space in area.spaces:  # iterate through spaces in current VIEW_3D area
                if space.type == 'VIEW_3D':  # check if space is a 3D view
                    space.viewport_shade = 'MATERIAL'
    #print(obj_object.children[3].name)
    if (haircolor != None):
        haircolor = tuple(map(float, haircolor[0:3]))
        for a in obj_object.children:
            if 'Hair' in a.name:
                for f in a.data.polygons:
                    if a.material_slots[f.material_index].material is not None:
                        a.material_slots[f.material_index].material.diffuse_color = haircolor
    obj_object.scale = scale
def update_matrix(name,matrix):
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j]==name:
                matrix[i][j]='0'

def moveObject(obj_object,fillWith,location,matrix):

    di = [v[:] for v in obj_object.bound_box]
    scalex=obj_object['scale'][0]
    scaley=obj_object['scale'][1]
    scalez=obj_object['scale'][2]
    mi=np.matrix(di)
    maxx=(max(mi[:,[0]]))[0,0]
    maxy=(max(mi[:,[2]]))[0,0]
    maxz=(max(mi[:,[1]]))[0,0]
    minx=(min(mi[:,[0]]))[0,0]
    miny = (min(mi[:,[2]]))[0,0]
    minz = (min(mi[:,[1]]))[0,0]
    AABB = [[(minx) * scalex, (-maxy) * scaley,
                           (minz) * scalez],
                          [(maxx) * scalex, (-miny) * scaley,
                           (maxz) * scalez]]
    minx = math.ceil(((minx * scalex) + int(location[0])) - global_x)
    miny = math.ceil(((miny * scaley) + int(location[1])) - global_y)
    maxx = math.ceil(((maxx * scalex) + int(location[0])) - global_x)
    maxy = math.ceil(((maxy * scaley) + int(location[1])) - global_y)


    while minx <= maxx:
        y = miny
        while y <= maxy:
            try:
                if matrix[minx][y] =='0':
                    matrix[minx][y] = fillWith
            except IndexError:
                print('location error')
            y += 1
        minx += 1
    return AABB

def Rotate(prevLocation, NewLocation):
    if prevLocation[0] < NewLocation[0] and prevLocation[1] == NewLocation[1]:
        return radians(90)
    elif prevLocation[0] > NewLocation[0] and prevLocation[1] == NewLocation[1]:
        return radians(-90)
    elif prevLocation[0] == NewLocation[0] and prevLocation[1] > NewLocation[1]:
        return radians(0)
    elif prevLocation[0] == NewLocation[0] and prevLocation[1] < NewLocation[1]:
        return radians(180)
    elif prevLocation[0] > NewLocation[0] and prevLocation[1] > NewLocation[1]:
        return radians(-45)
    elif prevLocation[0] < NewLocation[0] and prevLocation[1] < NewLocation[1]:
        return radians(135)
    elif prevLocation[0] > NewLocation[0] and prevLocation[1] < NewLocation[1]:
        return radians(-135)
    elif prevLocation[0] < NewLocation[0] and prevLocation[1] > NewLocation[1]:
        return radians(45)
def get_dimensions(obj_object):
    di = [v[:] for v in obj_object.bound_box]
    scalex = obj_object['scale'][0]
    scaley = obj_object['scale'][1]

    mi = np.matrix(di)
    maxx = (max(mi[:, [0]]))[0, 0]
    maxy = (max(mi[:, [2]]))[0, 0]

    minx = (min(mi[:, [0]]))[0, 0]
    miny = (min(mi[:, [2]]))[0, 0]

    location=obj_object.location
    minx = math.ceil(((minx * scalex) + int(location[0])) - global_x)
    miny = math.ceil(((miny * scaley) + int(location[1])) - global_y)
    maxx = math.ceil(((maxx * scalex) + int(location[0])) - global_x)
    maxy = math.ceil(((maxy * scaley) + int(location[1])) - global_y)
    return minx,maxx,miny,maxy

def applyAnimation(SeqFile,matrix):
    ModelsAction = SeqFile.readlines()
    for MA in ModelsAction:
        MA = MA.split()

        Sequences.append((MA))

    global_offset = 0
    pre_sequence = 0
    pre_offset = 0

    for animatedAction in Sequences:
        GoalInstance = None
        bpy.ops.object.select_all(action='DESELECT')
        objName = animatedAction[1]
        actionName = animatedAction[2]
        sequence = animatedAction[0]
        offset_arr = [global_offset]
        if (pre_sequence == sequence):
            offset = pre_offset
        else:
            offset = pre_offset = global_offset

        obj=""
        if (animatedAction[3] != str(-1)):
            obj = goal = animatedAction[3]
            GoalInstance = bpy.data.objects[goal]
        object = bpy.data.objects[objName]
        if hasattr(object.animation_data, 'action'):
            object.animation_data.action = None

        initial_state = {'Location': object.location, 'State': object["State"]}

        if (actionName == 'walk'):
            actionName = 'idle'
        if (GoalInstance != None):
            goal = {'Location': GoalInstance.location, 'State': actionName}
        else:
            goal = {"Location": object.location, "State": actionName}

        plan = planning.FromGEngine(initial_state, goal)
        object.select = True

        if len(object.animation_data.nla_tracks) <= 0:
            track = object.animation_data.nla_tracks.new()
        else:
            track = object.animation_data.nla_tracks[0]
        offset1=offset
        for actionToExecute in plan:
            addActionToScene(actionToExecute + ".fbx",bpy.data.objects[objName]['type'])
            if actionToExecute.find("Walking") == 0:
                local_bbox_center = 0.125 * sum((Vector(b) for b in bpy.data.objects[obj].bound_box), Vector())
                global_bbox_center = bpy.data.objects[obj].matrix_world * local_bbox_center
                if bpy.data.objects[obj]['type']=='bed':
                    x=2
                else :x=1.5
                dest = [global_bbox_center[0] + abs((bpy.data.objects[obj].dimensions.x) /x )*angle(math.degrees(bpy.data.objects[obj].rotation_euler[2]))[0],
                        global_bbox_center[1] + abs((bpy.data.objects[obj].dimensions.y) / x)*angle(math.degrees(bpy.data.objects[obj].rotation_euler[2]))[1]]

                path = Astar.Search(matrix,object.name,[object.location[0], object.location[1]], dest, global_x, global_y, bpy.data.objects[obj].dimensions.x,bpy.data.objects[obj].dimensions.y)

                if path==0:
                    break
                action = imported_actions[bpy.data.objects[objName]['type']+'+'+actionToExecute].animation_data.action
                frame_num =offset1
                for i in range(int(len(path) *10/25)):
                    start, end = action.frame_range
                    track.strips.new(action.name, offset1, action)
                    offset1 += end - start

                i = 1
                offset_arr.append(offset1)
                moveObject(object,'0',object.location,matrix)
                # update_matrix(object.name,matrix)
                location=[]
                path.append(dest)
                f = open("before"+object.name+".txt", "w")
                for row in range(len(matrix)):
                    for cell in range(len(matrix[0])):
                        f.write(matrix[row][cell] + " ")
                    f.write("\n")

                while i < len(path):
                    previous = [object.location[0], object.location[1]]
                    actions_list.append([object.name,'rotation',object.rotation_euler,(radians(90), 0, Rotate(previous, path[i])),frame_num,frame_num+6])
                    actions_list.append([object.name, 'location',object.location,(path[i][0], path[i][1], 0),frame_num+7, frame_num + 12])

                    object.rotation_euler = (radians(90), 0, Rotate(previous, path[i]))
                    location = (path[i][0], path[i][1], 0)
                    object.location=location
                    i+=1
                    frame_num += 10

                moveObject(object, object.name,location,matrix)

            else:
                out = action_tree.parse(object.name + ' ' + actionToExecute+' '+obj)
                if obj in bpy.data.objects and hasattr( bpy.data.objects[obj].animation_data, 'action'):
                    bpy.data.objects[obj].animation_data.action = None
                subject=object

                offset2=offset1
                for out1 in out:
                    if(bpy.data.objects[out1.subject]['type']+'+'+out1.action not in imported_actions):
                        addActionToScene(out1.action + ".fbx",bpy.data.objects[out1.subject]['type'])
                    object = bpy.data.objects[out1.subject]
                    if len(bpy.data.objects[out1.subject].animation_data.nla_tracks) <= 0:
                        track = bpy.data.objects[out1.subject].animation_data.nla_tracks.new()
                    else:
                        track =bpy.data.objects[out1.subject].animation_data.nla_tracks[0]
                    object["State"] = goal["State"]
                    action = imported_actions[bpy.data.objects[out1.subject]['type']+'+'+out1.action].animation_data.action
                    start, end = action.frame_range
                    if out1.action=='Stand_To_Sit':
                        actions_list.append([object.name,'rotation',object.rotation_euler,(radians(90), 0, bpy.data.objects[obj].rotation_euler[2]),offset2+float(out1.frame),offset2+float(out1.frame)+(end-start-10)])
                    if out1.action=='hold':
                        hold(object,bpy.data.objects[obj].name)
                    elif out1.action=='Soccer_Pass':
                        actions_list.append([bpy.data.objects[obj].name,'location',bpy.data.objects[obj].location,[bpy.data.objects[obj].location[0]+math.cos(math.degrees(object.rotation_euler[2])-45)*3,
                                                                                                                   math.sin(math.degrees(object.rotation_euler[2])-45)*3+bpy.data.objects[obj].location[1],
                                                                                                                   bpy.data.objects[
                                                                                                                       obj].location[2]],offset2+float(out1.frame)+18,offset2+float(out1.frame)+30])
                        actions_list.append([bpy.data.objects[obj].name,
                                             'velocity',None,
                                             [math.cos(math.degrees(object.rotation_euler[2]))*13,math.sin(math.degrees(object.rotation_euler[2]))*13,0]
                                                ,offset2+float(out1.frame)+31,
                                             offset2+float(out1.frame)+31])
                    elif out1.action=="Right_Turn":
                        actions_list.append([bpy.data.objects[obj].name,'rotation',bpy.data.objects[obj].rotation_euler,(radians(90), 0, radians(180)+(subject.rotation_euler[2])),offset2+float(out1.frame),offset2+float(out1.frame)+end-start])
                        bpy.data.objects[obj]["State"] = "idle"
                    elif out1.action=="Sit_To_Stand":
                        actions_list.append(
                            [object.name, 'location', object.location, (object.location[0], object.location[1]+40*object.scale[1]
                                                                        ,object.location[2]), offset2+float(out1.frame),offset2+float(out1.frame)])
                        actions_list.append(
                            [object.name, 'location', object.location,
                             (object.location[0], object.location[1] - 40 * object.scale[1]
                              , object.location[2]), offset2+float(out1.frame)+ end - start-1, offset2+float(out1.frame)+ end - start])
                    elif out1.action=="Clapping" or out1.action=="Jumping" or out1.action=="Running" or out1.action=="Waving":
                        object["State"] = "idle"
                    track.strips.new(action.name, offset2+float(out1.frame), action)
                    offset1=offset2+float(out1.frame)+ end - start
                    offset_arr.append(offset1)

            object.animation_data.nla_tracks.active = track
        offset1=global_offset = max(offset_arr)
        pre_sequence=sequence
    return global_offset


def addActionToScene(action_path,type):
    path = os.path.join(animation_path+'\\'+type, action_path)
    bpy.ops.import_scene.fbx(filepath=path)
    obj = bpy.context.selected_objects[0]
    obj.name = action_path.split(".")[0]
    imported_actions[type+'+'+action_path.split(".")[0]] = obj
    obj.location = (20.0, 20.0, 20.0)  # zxy
    bpy.context.scene.objects.unlink(obj)
    return


def animate():
    context = bpy.context

    # create a scene
    scene = bpy.data.scenes.new("Scene")

    camera_data = bpy.data.cameras.new("Camera")

    camera = bpy.data.objects.new("Camera", camera_data)
    camera.location = (44, -0, 35)
    camera.rotation_euler = ([radians(a) for a in (53.0, 0.0, 90.0)])
    camera.location = (44+2.5*radians(53), -0, 35+2.5*radians(90.0))
    scene.objects.link(camera)
    bpy.data.cameras['Camera'].lens = 31
    # do the same for lights etc
    scene.update()
    context.screen.scene = scene
    scene.camera = camera
    bpy.ops.scene.new(type='LINK_OBJECTS')
    context.scene.name = 'new'
    # sun lamp
    light_data = bpy.data.lamps.new('sun', 'SUN')
    light_obj = bpy.data.objects.new('sun', light_data)
    bpy.context.scene.objects.link(light_obj)

    light_obj.location = (2.0, 2.0, 20.0)
    light_obj.rotation_euler = (radians(100), radians(150), radians(20))

    # spotlight
    light_data = bpy.data.lamps.new('light', 'SPOT')
    light_obj = bpy.data.objects.new('light', light_data)
    bpy.context.scene.objects.link(light_obj)

    light_obj.location = (2.0, 2.0, 20.0)
    light_constr = light_obj.constraints.new('TRACK_TO')

    light_constr.target = bpy.data.objects['Cube']
    light_constr.track_axis = 'TRACK_NEGATIVE_Z'
    light_constr.up_axis = 'UP_X'

    light_data.spot_size = radians(250)


    humans = humanFile.readlines()
    objects = objectFile.readlines()
    locations=inputFile.readlines()

    for loc in locations:

        loc=loc.split()
        initial_locations[loc[0]]=[float(loc[1]),float(loc[2]),float(loc[3])]
        initial_angle[loc[0]]=[radians(float(loc[4])),radians(float(loc[5])),radians(float(loc[6]))]

    environments=environmentFile.readline()
    enviro=environments.split()
    env=enviro[0]
    id=enviro[1]
    intial=initial_locations[id].copy()
    if env!='street':
        path = os.path.join(models_path,env+'.obj')
        bpy.ops.import_scene.obj(filepath=path)
    else:
        path = os.path.join(models_path,env+'.fbx')
        bpy.ops.import_scene.fbx(filepath=path)

    obj_object = bpy.data.objects['floor']
        # get boumd box
    di = [v[:] for v in obj_object.bound_box]
    minz = minx = miny = 10000
    maxz = maxx = maxy = -10000
    for d in di:
        if (d[0] > maxx):
            maxx = d[0]
        elif d[0] < minx:
            minx = d[0]
        if (d[2] > maxy):
            maxy = d[2]
        elif d[2] < miny:
            miny = d[2]
        if (d[1] > maxz):
            maxz = d[1]
        elif d[1] < minz:
            minz = d[1]
    obj_object['AABB'] = [[[minx, -maxy, minz], [maxx, -miny, maxz]],[[minx, -maxy, minz], [maxx, -miny, maxz]]]
    initial_locations['floor']=[initial_locations[id][0],initial_locations[id][1],initial_locations[id][2]]
    obj_object['inv_mass'] = 0
    obj_object.rotation_euler=initial_angle[id]
    global global_x
    global global_y
    global global_z
    global_x = minx = math.ceil(minx)
    global_y = miny = math.ceil(miny)
    global_z = maxz
    maxx = math.ceil(maxx)
    maxy = math.ceil(maxy)
    matrix = np.zeros(((maxx - minx+1), (maxy - miny+1)), int)
    matrix = matrix.astype(str)
    for obj_object in bpy.context.selected_objects:
        obj_object['velocity']=obj_object['rotation_velocity']=[0.0,0,0]
        obj_object['a'] = [0, 0, 0]
        obj_object['e']=1
        obj_object['inv_mass'] = 0
        if obj_object.name == 'floor':
            continue

        obj_object.rotation_euler = initial_angle[id]
        location = obj_object.location = [initial_locations[id][0], initial_locations[id][1],  initial_locations[id][2]]
        di = [v[:] for v in obj_object.bound_box]
        minx = minz = miny = 10000
        maxx = maxz = maxy = -10000
        for d in di:
            if (d[0] > maxx):
                maxx = d[0]
            elif d[0] < minx:
                minx = d[0]
            if (d[2] > maxy):
                maxy = d[2]
                maxy = d[2]
            elif d[2] < miny:
                miny = d[2]
            if (d[1] > maxz):
                maxz = d[1]
            elif d[1] < minz:
                minz = d[1]
        obj_object['AABB'] = [[[minx, -maxy, minz], [maxx, -miny, maxz]],[[minx, -maxy, minz], [maxx, -miny, maxz]]]

        minx = math.ceil((minx + int(location[0])) - global_x)
        miny = math.ceil((miny + int(location[1])) - global_y)
        maxx = math.ceil((maxx + int(location[0])) - global_x)
        maxy = math.ceil((maxy + int(location[1])) - global_y)


        while minx <= maxx:
            y = miny
            while y <= maxy:
                try:
                    matrix[minx][y] = obj_object.name
                except IndexError:
                    pass
                y += 1
            minx += 1



    for MA in humans:
        MA = MA.split()
        models.append(MA[0])
        path = os.path.join(models_path, MA[0]+'.fbx')
        bpy.ops.import_scene.fbx(filepath=path)
        obj_object1 = bpy.context.selected_objects[0]
        obj_object1['type']=MA[0]

        obj_object1["State"] = "idle"
        if MA[1]=='NA':
            color=None
        else :
            color=MA[1].split('_')

        scale=MA[2].split('_')
        scale=tuple(map(float, [scale[0], scale[1], scale[2]]))
        applay_human_deformation(obj_object1, color, scale)
        id=MA[3]
        obj_object1.location = initial_locations[id]
        obj_object1.rotation_euler = initial_angle[id]
        obj_object1.name = name = id
        object_names.append(id)
        scalex = obj_object1.scale[0]
        scaley = obj_object1.scale[1]
        scalez = obj_object1.scale[2]
        obj_object1['scale']=[scalex,scaley,scalez]
        if obj_object1['type']+'+idle' not in imported_actions:
            addActionToScene("Idle.fbx",obj_object1['type'])
        if hasattr(obj_object1.animation_data, 'action'):
          obj_object1.animation_data.action = imported_actions[MA[0]+'+Idle'].animation_data.action
        AABB1=[]

        AABB1.append(moveObject(obj_object1,name,initial_locations[id],matrix))
        AABB1.insert(0, moveObject(obj_object1, name, initial_locations[id], matrix))
        obj_object1['AABB'] = AABB1
        obj_object1.location= initial_locations[id]
        obj_object1['velocity'] =obj_object['rotation_velocity']= [0.0, 0.0, 0.0]
        obj_object1['scale'] = scale
        obj_object1['a'] = [0.0, 0.0, 0.0]
        obj_object1['e'] = .01
        obj_object1['inv_mass'] = 0.0
    for objecc in bpy.data.objects:
        if 'scale' in objecc:
            update_matrix(objecc.name,matrix)
            moveObject(objecc,objecc.name,objecc.location,matrix)

    for MA in objects:
        MA = MA.split()
        models.append(MA[0])
        path = os.path.join(models_path, MA[0]+'.obj')
        # import model
        bpy.ops.import_scene.obj(filepath=path)
        if MA[1]=='NA':
            color=None
        else :
            color=MA[1].split('_')
        scale = MA[2].split('_')
        scale = tuple(map(float, [scale[0], scale[1], scale[2]]))
        AABB=[]
        name=id = MA[3]
        location = initial_locations[id]
        for obj_object in bpy.context.selected_objects:
            obj_object['scale'] = scale
            AABB.append(moveObject(obj_object,name,location,matrix))
            bpy.context.scene.objects.active = obj_object
            bound=moveObject(obj_object,'0',location,matrix)
        bpy.ops.object.join()
        obj_object.rotation_euler = initial_angle[id]
        obj_object = bpy.context.selected_objects[0]
        AABB.insert(0, moveObject(obj_object, name, location, matrix))
        obj_object['AABB']=AABB
        obj_object['type']=MA[0]
        obj_object['velocity'] =obj_object['rotation_velocity']=[0.0, 0.0, 0.0]
        obj_object['scale'] = scale
        obj_object['a'] = [0.0, 0.0, 0.0]
        obj_object['e'] = float(MA[5])  # to be red
        obj_object['inv_mass'] = float(MA[4])  # to be red
        obj_object.location= initial_locations[id]
        initial_locations[id]=obj_object.location
        applay_deformation(obj_object, color, scale)
        obj_object.name = name = id
        object_names.append(id)
    f=open("matrix2.txt","w")
    for row in range(len(matrix)):
         for cell in range(len(matrix[0])):
             f.write(matrix[row][cell]+" ")
         f.write("\n")
    frame_number=applyAnimation(SeqFile,matrix)+50

    for objec in bpy.data.objects:
        if objec.name in initial_locations:
            objec.location = initial_locations[objec.name]
        if objec.name in initial_angle:
            objec.rotation_euler = initial_angle[objec.name]
    for frame in range(int(frame_number)):
        for action in actions_list:
            if frame == action[5]:
                if action[1] == 'location':
                    bpy.data.objects[action[0]].location = action[3]
                elif action[1] == 'velocity':
                    bpy.data.objects[action[0]]['velocity'] = action[3]
            if frame >= action[4] and frame < action[5]:
                start = action[4]
                end = action[5]
                inc = (np.array(action[3]) - np.array(action[2])) / (end - start)
                if action[1] == 'rotation':
                    bpy.data.objects[action[0]].rotation_euler = np.array(
                        bpy.data.objects[action[0]].rotation_euler) + inc
                    if frame + 1 == action[5]:
                        bpy.data.objects[action[0]].rotation_euler = action[3]

                    bpy.data.objects[action[0]].keyframe_insert("rotation_euler")
                elif action[1] == 'location':
                    bpy.data.objects[action[0]].location = np.array(bpy.data.objects[action[0]].location) + inc
                    if frame + 1 == action[5]:
                        bpy.data.objects[action[0]].location = action[3]
                    bpy.data.objects[action[0]].keyframe_insert("location")
        for i in range(len(bpy.data.objects)):
            ob = bpy.data.objects[i]
            if 'AABB' not in ob:
                continue
            physics.apply_speed(ob)
            physics.resitance(ob)
            if ob['inv_mass'] > 0:
                physics.advance(ob, global_z + bpy.data.objects['floor'].location[2],bpy.data.objects['floor']['AABB'][0][0][0],
                bpy.data.objects['floor']['AABB'][0][1][0],bpy.data.objects['floor']['AABB'][0][0][1],bpy.data.objects['floor']['AABB'][0][1][1])

            ob.keyframe_insert(data_path="location")
            ob.keyframe_insert(data_path="rotation_euler")
            j = 0
            no_collision = collision_check = False
            while j < len(bpy.data.objects):
                ob1 = bpy.data.objects[j]
                if 'AABB' in ob1 and ob1.name != ob.name:
                    collision_check, x, y = physics.collision_detection(ob, ob1)
                    if collision_check:
                        if ob1['inv_mass'] != 0 or ob['inv_mass'] != 0:
                            no_collision = True
                            if j>i:
                                physics.ResolveCollision(ob, ob1, x, y)
                j += 1
            if no_collision == False and ob.location[2] > physics.minimumz(ob, global_z) + .7:
                physics.apply_gravity(ob)
        bpy.context.scene.frame_set(frame)

    scene = bpy.context.scene
    rd = scene.render
    bpy.context.scene.frame_end=frame_number
    # # Set output type
    rd.image_settings.file_format = "FFMPEG"
    #
    # # Set output format
    rd.ffmpeg.format = "MPEG4"
    #
    # # Set the codec
    rd.ffmpeg.codec = "H264"
    #
    rd.filepath = '//videos//play'
    #
    bpy.ops.render.render(animation=True)
    i=0
    d=''
    while 4-len(str(int(frame_number)))>i:
        d+='0'
        i+=1

    return 'paly0001-'+d+str(int(frame_number))+'.mp4'
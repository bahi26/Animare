import networkx as nx
import numpy as np
import Model
import binvox_rw
import random
from pyevtk.hl import gridToVTK

objects = [] 
relations = [] 
dic = {'apple': None}
files_names = {'apple': None}
sorted_ob_size = []
enviro_name = None
G = None
sizes = []


def static_positioning():
    global objects
    global dic
    global sorted_ob_size
    global enviro_name
    global G

    read_files_names()
    print(files_names)

    dic.clear()
    # =========================read objects ===========
    file_input_text = open("models_char.txt", "r")

    input_text = file_input_text.read()
    content = input_text.split("\n")

    for entry in range(0, len(content) - 1):
        ch = content[entry].split(" ")
        
        if(ch[0] == 'woman' or ch[0] == 'man'):
            if(ch[1] == '1' ): ch[0] =('old_' + ch[0] )
            
        nc = ((ch[0], ch[len(ch) - 1]))
        objects.append(nc)
        s = ' '
        if (ch[len(ch) - 2] == '0'):
            s = '_s'
        elif (ch[len(ch) - 2] == '1'):
            s = '_m'

        elif (ch[len(ch) - 2] == '2'):
            s = '_l'
        sizes.append(s)

    file_input_text.close()
    print(objects)
    # ================read relations===========

    file_input_text = open("models_relations.txt", "r")

    input_text = file_input_text.read()
    content = input_text.split("\n")

    for entry in range(0, len(content) - 1):
        ch = content[entry].split(" ")
        nc = (ch[0], (ch[1], ch[2]), (ch[3], ch[4]))
        relations.append(nc)
    file_input_text.close()
    print(relations)

    # ============================load models =========================
    for index, ob in enumerate(objects):
        
        element = Model.object(ob)
        element.size = sizes[index]
        model, height = load_model(ob[0] + element.size, sizes[index])
        model = red_m(model)
        x, y, z = model.shape
        element.model = Model.Model(x, y, z, model, height)
        element.tx = element.model.dx + 1
        element.tz = element.model.dz + 1

        dic[ob] = element

    print(dic.keys())
    sorted_ob_size = sorted(dic.values(), key=sort_model_size, reverse=True)
    enviro_name = sorted_ob_size[0].name
    dic[enviro_name].setteled = 1
    if (dic[enviro_name].model.dz < dic[enviro_name].model.dx and dic[enviro_name].model.dz < dic[
        enviro_name].model.dy):
        dic[enviro_name].model.modify_dimensions()

    # ==================create the graph====================================
    G = nx.DiGraph()

    G.add_nodes_from(objects)
    for rel in relations:
        G.add_edge(rel[1], rel[2], weight=rel[0])

    # ===========================get right/ left / behind/ front ============================
    Gnodes = G.nodes()
    for n in Gnodes:
        get_neighbours(n)

    # =========================set the base ==================================
    find_base_2()

    sorted_ob_size = sorted(dic.values(), key=sort_model_size, reverse=True)
    for puto in sorted_ob_size:
        settele_obj(puto,1)

    save_to_vtk(dic[enviro_name].model.matrix, 'animations/trial_new_dimensions')

    for puto in sorted_ob_size:
        puto.real_x, puto.real_y, puto.real_z = get_real_dimensions_2(puto)

    write_output_to_file()

    return



def get_real_dimensions_2(obj):
    if (obj.setteled != 1):
        settele_obj(obj,1)
    real_x = (obj.model.least_p[0] * dic[enviro_name].model.h_y[4]) / (dic[enviro_name].model.dx + 1)
    real_z = (obj.model.least_p[2] * dic[enviro_name].model.h_y[2]) / (dic[enviro_name].model.dz + 1)
    
    real_y = 0
    # ================ loop for bases =================
    base = obj.base
    while (base != None):
        rel = base[1]
        if (rel == 'on'):
            real_y += dic[base[0]].model.h_y[3]
        elif (rel == 'in'):
            real_y += dic[base[0]].model.h_y[0]
        base = dic[base[0]].base
    

    
    
    return  real_x, real_z, real_y




def settele_obj(puto, logic):
    if (puto.setteled == 0):
        print(puto.name)
        xmin = ymin= zmin = -1
        xmax , ymax , zmax = dic[enviro_name].model.max_p
        left = right = back = front = 0
        # ===============in or on=================
        if (puto.base[1] == 'in'):
            if (dic[puto.base[0]].model.inner_o_p[0] == -1):
                dic[puto.base[0]].model.get_inner_dim()
            xmin, ymin, zmin = dic[puto.base[0]].model.inner_o_p
            xmax, ymax, zmax = dic[puto.base[0]].model.inner_m_p
            ymax = ymin
            '''    
            xmin,ymin,zmin= dic[puto.base[0]].model.least_p
            xmax,ymax,zmax=  dic[puto.base[0]].model.max_p
            ymax=ymin= (ymin+1)
            '''
        if (puto.base[1] == 'on'):
    
            if (dic[puto.base[0]].setteled == 0):
                settele_obj(dic[puto.base[0]])
    
            ymin = ymax = dic[puto.base[0]].model.max_p[1] + 1
    
            if (puto.model.dx <= dic[puto.base[0]].model.dx):
                xmin = dic[puto.base[0]].model.least_p[0]
                xmax = dic[puto.base[0]].model.max_p[0]
            else:
    
                xmin = max(xmin, dic[puto.base[0]].model.max_p[0] - puto.model.dx)
                xmax = min(xmax,dic[puto.base[0]].model.least_p[0] + puto.model.dx)
    
            if (puto.model.dz <= dic[puto.base[0]].model.dz):
                zmin = dic[puto.base[0]].model.least_p[2]
                zmax = dic[puto.base[0]].model.max_p[2]
    
            else:
                zmin = max(zmin, dic[puto.base[0]].model.max_p[2] - puto.model.dz)
                zmax = min(zmax,dic[puto.base[0]].model.least_p[2] + puto.model.dz)
    
                # ================back and front===========
        for l in puto.front:
            if (dic[l].setteled == 1):
                xmax = min(xmax, dic[l].model.least_p[0])
                
                if (puto.model.dz <= dic[l].model.dz):
                    zmin = max(zmin, dic[l].model.least_p[2])
                    zmax = min(zmax, dic[l].model.max_p[2])
                
                else:                 
                    zmin = max(zmin, dic[l].model.max_p[2] - puto.model.dz)
                    zmax = min(zmax, dic[l].model.least_p[2] + puto.model.dz)
                
                break
            else:
                front += (dic[l].model.dx+1)
    
        for l in puto.back:
            if (dic[l].setteled == 1):
                xmin = max(xmin, dic[l].model.max_p[0])
                
                if (puto.model.dz <= dic[l].model.dz):
                    zmin = max(zmin, dic[l].model.least_p[2])
                    zmax = min(zmax, dic[l].model.max_p[2])
                
                else:                 
                    zmin = max(zmin, dic[l].model.max_p[2] - puto.model.dz)
                    zmax = min(zmax, dic[l].model.least_p[2] + puto.model.dz)
                    
                break
            else:
                back += (dic[l].model.dx+1)
    
        # ================ right and left t================
    
        for l in puto.right:
            if (dic[l].setteled == 1):
                zmax = min(zmax,  dic[l].model.least_p[2])
                
                if (puto.model.dx <= dic[l].model.dx):
                    xmin = max(xmin, dic[l].model.least_p[0])
                    xmax = min(xmax, dic[l].model.max_p[0])
                
                else:
                    xmin = max(xmin, dic[l].model.max_p[0] - puto.model.dx)
                    xmax = min(xmax,dic[l].model.least_p[0] + puto.model.dx)
                break
            else:
                right += (dic[l].model.dz+1)
    
        for l in puto.left:
            if (dic[l].setteled == 1):
                zmin = max(zmin,  dic[l]. model.max_p[2])
                
                if (puto.model.dx <= dic[l].model.dx):
                    xmin = max(xmin, dic[l].model.least_p[0])
                    xmax = min(xmax, dic[l].model.max_p[0])
                
                else:
                    xmin = max(xmin, dic[l].model.max_p[0] - puto.model.dx)
                    xmax = min(xmax,dic[l].model.least_p[0] + puto.model.dx)
                break
            
            else:
                left += (dic[l].model.dz+1)
    
        right += (puto.model.dz)
        front += (puto.model.dx)
        # ========generate no within range
        en_x = random.randint((xmin + left), (xmax - right))
        en_z = random.randint((zmin + back), (zmax - front))
        #  ======== check place
        loop =0
        while (check_place(en_x, ymin, en_z, puto.model.max_p) == False):
            loop +=1
            if(loop == 100): raise Exception("infinite loop")
            en_x = random.randint((xmin + left ), (xmax - right ))
            en_z = random.randint((zmin + back ), (zmax - front ))

        place_model(en_x, ymin, en_z, puto)

    # ======== place objects in left/ right/ front/ back arrays
    if (logic == 1):
        for n in puto.right:
            if (dic[n].setteled == 0):
                settele_obj(dic[n],0)
    
        for n in puto.left:
            if (dic[n].setteled == 0):
                settele_obj(dic[n],0)
    
        for n in puto.front:
            if (dic[n].setteled == 0):
                settele_obj(dic[n],0)
    
        for n in puto.back:
            if (dic[n].setteled == 0):
                settele_obj(dic[n],0)
    return


def check_place(x, y, z, m_p):
    env = dic[enviro_name].model
    for i in range(x, x + m_p[0] + 1):
        for k in range(y, y + m_p[1] + 1):
            for e in range(z, z + m_p[2] + 1):
                if (env.matrix[i][k][e] == 1):
                    return False

    return True


def place_model(x, y, z, puto):
    enviro = dic[enviro_name].model
    model = puto.model
    m_p = model.max_p
    for i in range(x, x + m_p[0] + 1):
        for k in range(y, y + m_p[1] + 1):
            for e in range(z, z + m_p[2] + 1):
                enviro.matrix[i][k][e] = model.matrix[i - x][k - y][e - z]
    model.update_terminals(x, y, z)

    print(model.least_p, model.max_p)
    enviro.freepixels += (model.shape - model.freepixels)
    dic[puto.name].setteled = 1
    return


def get_neighbours(node):
    global dic

    get_right_neighbours(node, 1)
    get_left_neighbours(node, 1)
    get_front_neighbours(node, 1)
    get_back_neighbours(node, 1)

    # ========loop and calculate new dx and dz
    for e in dic[node].left:
        dic[node].tx += (dic[e].model.dx + 1)
    for e in dic[node].right:
        dic[node].tx += (dic[e].model.dx + 1)
    for e in dic[node].front:
        dic[node].tz += (dic[e].model.dz + 1)
    for e in dic[node].back:
        dic[node].tz += (dic[e].model.dz + 1)

    return


def get_right_neighbours(node, m):
    global dic
    returned_neighbours = []
    node_rel = list(G.in_edges(node, data=True))
    node_rel += list(G.out_edges(node, data=True))
    # print(node_rel)
    # ===============right neighbours===========
    for u, v, d in node_rel:
        if (v == node and d['weight'] == 'right'):
            returned_neighbours.append(u)
            returned_neighbours += get_right_neighbours(u, 0)
        elif (u == node and d['weight'] == 'left'):
            returned_neighbours.append(v)
            returned_neighbours += get_right_neighbours(v, 0)
    if (m == 1):
        for t in returned_neighbours:
            dic[node].right.append(t)

    return returned_neighbours


def get_left_neighbours(node, m):
    global dic
    returned_neighbours = []
    node_rel = list(G.in_edges(node, data=True))
    node_rel += list(G.out_edges(node, data=True))
    # print(node_rel)

    # ===============left neighbours===========
    for u, v, d in node_rel:
        if (v == node and d['weight'] == 'left'):
            returned_neighbours.append(u)
            returned_neighbours += get_left_neighbours(u, 0)
        elif (u == node and d['weight'] == 'right'):
            returned_neighbours.append(v)
            returned_neighbours += get_left_neighbours(v, 0)
    if (m == 1):

        for t in returned_neighbours:
            dic[node].left.append(t)

    return returned_neighbours


def get_front_neighbours(node, m):
    global dic
    returned_neighbours = []
    node_rel = list(G.in_edges(node, data=True))
    node_rel += list(G.out_edges(node, data=True))
    # print(node_rel)
    # ===============front neighbours===========
    for u, v, d in node_rel:
        if (v == node and d['weight'] == 'front'):
            returned_neighbours.append(u)
            returned_neighbours += get_front_neighbours(u, 0)
        elif (u == node and d['weight'] == 'behind'):
            returned_neighbours.append(v)
            returned_neighbours += get_front_neighbours(v, 0)
    if (m == 1):
        for t in returned_neighbours:
            dic[node].front.append(t)

    return returned_neighbours


def get_back_neighbours(node, m):
    global dic
    returned_neighbours = []
    node_rel = list(G.in_edges(node, data=True))
    node_rel += list(G.out_edges(node, data=True))
    # print(node_rel)
    # ===============back neighbours===========
    for u, v, d in node_rel:
        if (v == node and d['weight'] == 'behind'):
            returned_neighbours.append(u)
            returned_neighbours += get_back_neighbours(u, 0)
        elif (u == node and d['weight'] == 'front'):
            returned_neighbours.append(v)
            returned_neighbours += get_back_neighbours(v, 0)
    if (m == 1):
        for t in returned_neighbours:
            dic[node].back.append(t)

    return returned_neighbours


def sort_model_size(object):
    return (object.tx + 1) * (object.tz + 1)



def red_m(im):
    '''
    mask = im == 0
    all_white = ( mask).sum(axis=2) == 0
    rows = np.flatnonzero((~all_white).sum(axis=1))
    cols = np.flatnonzero((~all_white).sum(axis=0))
    crop = im[rows.min():rows.max()+1, cols.min():cols.max()+1, :]
    print(crop)
    '''
    x, y, z = im.shape

    # x ===============================
    x_start = 0
    x_end = x;
    check = False
    for i in range(x):
        for k in range(y):

            for e in range(z):
                if (im[i][k][e] == 1):
                    check = True
                    break
            if (check == True):
                x_start = i
                break

        if (check == True):
            check = False
            break

    # reverse x =======================================

    for i in reversed(range(x)):
        for k in range(y):
            for e in range(z):
                if (im[i][k][e] == 1):
                    check = True
                    break
            if (check == True):
                x_end = i
                break
        if (check == True):
            check = False
            break
    im = im[x_start:x_end + 1, :, :]

    # y ======================================
    x, y, z = im.shape
    y_start = 0
    y_end = y;

    for k in range(y):
        for i in range(x):

            for e in range(z):
                if (im[i][k][e] == 1):
                    check = True
                    break
            if (check == True):
                y_start = k
                break

        if (check == True):
            check = False
            break

    # reverse y =======================

    for k in reversed(range(y)):
        for i in range(x):
            for e in range(z):
                if (im[i][k][e] == 1):
                    check = True
                    break
            if (check == True):
                y_end = k
                break
        if (check == True):
            check = False
            break
    im = im[:, y_start:y_end + 1, :]

    # z ============================
    x, y, z = im.shape
    z_start = 0
    z_end = z;

    for e in range(z):
        for i in range(x):

            for k in range(y):
                if (im[i][k][e] == 1):
                    check = True
                    break
            if (check == True):
                z_start = e
                break

        if (check == True):
            check = False
            break

    # reverse z ==============================
    for e in reversed(range(z)):
        for i in range(x):
            for k in range(y):
                if (im[i][k][e] == 1):
                    check = True
                    break
            if (check == True):
                z_end = e
                break
        if (check == True):
            check = False
            break
    im = im[:, :, z_start:z_end + 1]

    return im


def load_model(model_name, size):
    print(model_name)
    with open('my_objs/' + model_name + '.binvox', 'rb') as f:   #with open('binvox_files/' + model_name + '.binvox', 'rb') as f:
        md = binvox_rw.read_as_3d_array(f)
        # print( md.dims)

    data_ds = binvox_rw.dense_to_sparse(md.data)
    _, width = data_ds.shape
    # print(width)

    # create the matrix
    x, y, z = md.dims
    model_matrix = np.zeros((x, y, z))

    for i in range(width):
        x = data_ds[0][i]
        y = data_ds[1][i]
        z = data_ds[2][i]
        # global model_matrix
        model_matrix[x][y][z] = 1

    return model_matrix, md.height


def save_to_vtk(data, filepath):
    """
    save the 3d data to a .vtk file.

    Parameters
    ------------
    data : 3d np.array
        3d matrix that we want to visualize
    filepath : str
        where to save the vtk model, do not include vtk extension, it does automatically
    """
    x = np.arange(data.shape[0] + 1)
    y = np.arange(data.shape[1] + 1)
    z = np.arange(data.shape[2] + 1)
    gridToVTK(filepath, x, y, z, cellData={'data': data.copy()})

    return


def find_base_2():
    global dic

    relations = list(G.edges(data=True))
    for u, v, d in relations:
        if (d['weight'] == 'on' or(d['weight'] == 'in' and v != enviro_name)):
            dic[u].base = (v, d['weight'])
            for n in dic[u].right:
                dic[n].base = (v, d['weight'])
            for n in dic[u].left:
                dic[n].base = (v, d['weight'])
            for n in dic[u].front:
                dic[n].base = (v, d['weight'])
            for n in dic[u].back:
                dic[n].base = (v, d['weight'])

    nodes = G.nodes()
    for ob in nodes:
        if (dic[ob].base == None and (dic[ob].name != enviro_name)):
            dic[ob].base = (enviro_name, 'in')

    return


def read_files_names():
    global files_names

    files_names.clear()
    file_input_text = open("models_names.txt", "r")

    input_text = file_input_text.read()
    content = input_text.split("\n")
    for entry in range(0, len(content)-1):
        ch = content[entry].split(" ")
        files_names[ch[0]] = ch[1]

    file_input_text.close()

    return


def write_output_to_file():
    file_output_text = open("animations/com.txt", "w")
    for ob in sorted_ob_size:
        print(ob.name)
        line =   files_names[ob.name[0]]+' '+ ob.name[0]+' '+ ob.size+' '
        line += str(ob.real_x + ob.model.h_y[5]- dic[enviro_name].model.h_y[5]) + ' ' + str(ob.real_y+ ob.model.h_y[6]- dic[enviro_name].model.h_y[6]) + ' ' + str(ob.real_z+ ob.model.h_y[7]- dic[enviro_name].model.h_y[7]) +' '+str( ob.model.h_y[8])  +' '+str( ob.model.h_y[9])+' '+ str( ob.model.h_y[10]) +'\n'
        file_output_text.write(line)
    file_output_text.close()
    
    file_output_text_2 = open("models.txt", "w")
    for ob in sorted_ob_size:
        line = ob.name[1]+' '
        line += str(ob.real_x + ob.model.h_y[5]- dic[enviro_name].model.h_y[5]) + ' ' + str(ob.real_y+ ob.model.h_y[6]- dic[enviro_name].model.h_y[6]) + ' ' + str(ob.real_z+ ob.model.h_y[7]- dic[enviro_name].model.h_y[7]) +' '+str( ob.model.h_y[8])  +' '+str( ob.model.h_y[9])+' '+ str( ob.model.h_y[10]) +'\n'
        file_output_text_2.write(line)
    file_output_text_2.close()


    return


if __name__ == "__main__":
    static_positioning()


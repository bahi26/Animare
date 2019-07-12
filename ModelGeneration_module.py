import numpy
import functions
from matplotlib import colors

def model_generation():
    input=open("models_char.txt","r")
    output=open("humans.txt","w")
    output2=open("objects.txt","w")
    output3=open("environments.txt","w")
    lines=input.readlines()
    check=False
    for temp in lines:
        line=temp.split()
        human,color,scale=functions.human_path(line[0],line[1],line[2])
        if human!=None:
            if(color=='none'):
                color='NA'
            else:
                color=colors.to_rgba(color)
                color = '_'.join(str(e) for e in color)
            scale3=1
            if(line[3]==0):
                scale3=0.9
            elif line[3]==2:
                scale3=1.2
            scale=str(scale*5)+'_'+str(scale3*scale*5)+'_'+str(scale*5)
            output.write(human+' '+color+' '+scale+' '+str(line[4])+' 0 1\n')
        else :
            if functions.exists(line[0],True):
                size=1
                print(line[2])
                if (line[2]==2):
                    size=size*1.5
                elif line[2]==0:
                    size = size * .75
                if line[1]=='none':
                    color='NA'
                else:
                    color=colors.to_rgba(line[1])
                    color='_'.join(str(e) for e in color)
                size2=size3=size
                if line[0]=='chair' and size2==1.5:
                    size=1
                    size3=1
                    size2=1.2
                output2.write(line[0]+' '+color+' '+str(size2)+'_'+str(size)+'_'+str(+size3)+' '+str(line[3])+' '+str(functions.inv_math[functions.models.index(line[0])])+' '+
                str(functions.e[functions.models.index(line[0])])+'\n')
            elif functions.exists(line[0],False):
                check=True
                output3.write(str(line[0])+' '+str(line[3])+' 0 1')
            else :
                size = 1
                print(line[2])
                if (line[2] == 2):
                    size = size * 1.15
                elif line[2] == 0:
                    size = size * .75
                if line[1] == 'none':
                    color = 'NA'
                else:
                    color = colors.to_rgba(line[1])
                    color = '_'.join(str(e) for e in color)
                output2.write('box' + ' ' + color + ' ' + str(size) + str(line[3]) + ' 0.1 0.1\n')
    if check ==False:
        output3.write('Room 0 0 1\n')
    output.close()
    output2.close()
    output3.close()
    input.close()

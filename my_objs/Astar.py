from __future__ import print_function
import matplotlib.pyplot as plt
import math
import numpy
import numpy as np

class AStarGraph(object):
    # Define a class board like grid with two barriers

    def __init__(self,matrix,id):
        self.id=id
        self.matrix = matrix

    def heuristic(self, start, goal):

        dx = abs(start[0] - goal[0])
        dy = abs(start[1] - goal[1])
        distnace= (dx*dx)+(dy*dy)
        distnace=math.sqrt(distnace)
        #print("distance is ",distnace,"from ",start,"to ",goal)
        return distnace

    def get_vertex_neighbours(self, pos):
        n = []
        # Moves allow link a chess king
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
            x2 = pos[0] + dx
            y2 = pos[1] + dy
            if x2 < 0 or x2 > len(self.matrix) or y2 < 0 or y2 > len(self.matrix[0]):
                continue
            n.append((x2, y2))
        return n

    def move_cost(self, a, b,x,y,c):
        minX=-x+b[0]
        maxX=x+b[0]
        minY=-y+b[1]
        maxY=y+b[1]
        i=minY
        d=1
        while i< maxY:
            j = minX
            while j <maxX:
                try:
                    if self.matrix[j][i]!=self.id and self.matrix[j][i]!='0':
                        #print(self.matrix[i][j])
                        d+= 10000
                        if b[0]==j and b[1]==i:
                            d+=10000000
                except IndexError:
                    d+= 1000000000000
                j+=1
            i+=1

        return d  # Normal movement cost


def AStarSearch(start, end, graph,x,y):
    G = {}  # Actual movement cost to each position from the start position
    F = {}  # Estimated movement cost of start to end going via this position

    # Initialize starting values
    G[start] = 0
    F[start] = graph.heuristic(start, end)

    closedVertices = set()
    openVertices = set([start])
    cameFrom = {}

    while len(openVertices) > 0:
        # Get the vertex in the open list with the lowest F score
        current = None
        currentFscore = None
        for pos in openVertices:
            if current is None or F[pos] < currentFscore:
                currentFscore = F[pos]
                current = pos

        # Check if we have reached the goal
        if current == end:
            # Retrace our route backward
            path = [current]
            while current in cameFrom:
                current = cameFrom[current]
                path.append(current)
            path.reverse()
            return path, F[end],F  # Done!

        # Mark the current vertex as closed
        openVertices.remove(current)
        closedVertices.add(current)

        # Update scores for vertices near the current position
        for neighbour in graph.get_vertex_neighbours(current):
            if neighbour in closedVertices:
                continue  # We have already processed this node exhaustively
            if current in cameFrom:
                pre=cameFrom[current]
            else :
                pre=None
            candidateG = G[current] + graph.move_cost(current, neighbour,x,y,pre)


            if neighbour not in openVertices:
                openVertices.add(neighbour)  # Discovered a new vertex
            elif candidateG >= G[neighbour] or candidateG>10000:
                continue  # This G score is worse than previously found

            # Adopt this G score
            cameFrom[neighbour] = current
            G[neighbour] = candidateG
            H = graph.heuristic(neighbour, end)
            F[neighbour] = G[neighbour] + H

    raise RuntimeError("A* failed to find a solution")

def Search(matrix,id,start,end,global_x,global_y,x,y):
    x=math.ceil(x/2)
    y=math.ceil(y/2)
    graph = AStarGraph(matrix,id)
    print(start,end)
    start = (math.ceil(start[0] - global_x), math.ceil(start[1] - global_y))
    end = (math.ceil(end[0] - global_x), math.ceil(end[1] - global_y))
    print("startt is",start)
    print("end is ",end)
    result, cost,F = AStarSearch(start, end, graph,x,y)
    print("route", cost)
    if cost>1000000000:
        return 0
    deletedPaths=[]
    for i in range(len(result)):
        if matrix[result[i][0]][result[i][1]]!=id and matrix[result[i][0]][result[i][1]]!='0':
            deletedPaths.append(i)
        print("result is ", matrix[result[i][0]][result[i][1]], 'at ', result[i][0], ' ', result[i][1])
        result[i] = [result[i][0] + global_x, result[i][1] + global_y]

    unique, counts = numpy.unique(matrix, return_counts=True)
    #print("area is ",dict(zip(unique, counts)))

    # plt.plot([v[0] for v in result], [v[1] for v in result])
    # plt.xlim(-10, 8)
    # plt.ylim(-10, 8)
    # plt.show()
    return  result
    return  result
    return  result
    return  result
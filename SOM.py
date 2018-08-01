
import numpy as np
from tqdm import tqdm 


def alph(T,t): # Learning Rate, Deacrease as we move through the iterations
    try:
        return((T-t)/T)
    except ZeroDivisionError:
        return 0

def neihborhood(bmu_location,node_location): # Neighborhood function, dictates the maganitude of the update as we move away from the BMU
 
    dist = np.linalg.norm(bmu_location-node_location)
    return np.exp(-1.0*(dist/2))



def SOM(inp, map_size,iterations, mapp = 'None'):

    if mapp == 'None':
        mapp = np.random.rand(map_size,map_size,inp.shape[1]) # Generate a 24x24 node feature of color data

    else: mapp = mapp


    for iters in tqdm(range(iterations)): 

        rand_num = np.random.randint(inp.shape[0])
        current_vector = inp[rand_num,:] # Select a Random Document Vector From the training data
        

       # Traverse the map and calculating Euclidian Distance from each node to find best matching unit (BMU)
        bmu = np.inf
        bmu_loc = (0,0)

        for i in range(mapp.shape[0]):
            for j in range(mapp.shape[1]):
                dist = np.linalg.norm(current_vector-mapp[i][j])
                if dist < bmu:
                    bmu = dist
                    bmu_loc = (i,j)

       # Update BMU and Neighbours in the map: 

        try:
            for x in range(-12,12):
                for y in range(-12,12):                
                    mapp[bmu_loc[0]+x][bmu_loc[1]+y] = mapp[bmu_loc[0]+x][bmu_loc[1]+y]+ (alph(iterations,iters)) * neihborhood(np.array(bmu_loc),np.array([bmu_loc[0]+x,bmu_loc[1]+y]))*(current_vector-mapp[bmu_loc[0]+x][bmu_loc[1]+y])
        except IndexError:
            pass
        
    return mapp
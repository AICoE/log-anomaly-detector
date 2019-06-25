"""Compute values for Self Organizing Map."""
import numpy as np
import matplotlib.pyplot as plt


def alph(T, t):
    """Learning Rate, Decrease as we move through the iterations."""
    try:
        return (T-t)/T
    except ZeroDivisionError:
        return 0


def neihborhood(bmu_location, node_location):
    """Neighborhood function, dictates the maganitude of the update as we move away from the BMU."""
    dist = np.linalg.norm(bmu_location - node_location)
    return np.exp(-1.0*(dist/2))


def SOM(inp, map_size, iterations, mapp='None', exp=0):
    """Main function for training the Self-Organizing Map."""
    if mapp == 'None':
        mapp_1 = np.random.rand(map_size, map_size, inp.shape[1])  # Generate a 24x24 node feature of color data

    else:
        mapp_1 = mapp.copy()

    training_animation = []

    for iters in range(iterations):

        # rand_num = np.random.randint(inp.shape[0])
        current_vector = inp[iters, :]  # Select a Random Document Vector From the training data

        # Traverse the map and calculating Euclidean Distance from each node to find best matching unit (BMU)
        bmu = np.inf
        bmu_loc = (0, 0)

        for i in range(mapp_1.shape[0]):
            for j in range(mapp_1.shape[1]):
                dist = np.linalg.norm(current_vector-mapp_1[i][j])
                if dist < bmu:
                    bmu = dist
                    bmu_loc = (i, j)

        # Update BMU and Neighbours in the map:

        for x in range(-24, 24):
            for y in range(-24, 24):
                current_x = bmu_loc[0] + x
                current_y = bmu_loc[1] + y
                if 0 <= current_x < 24 and 0 <= current_y < 24:
                    mapp_1[current_x][current_y] = mapp_1[current_x][current_y]\
                                                           + (alph(iterations, iters)) \
                                                           * neihborhood(np.array(bmu_loc),
                                                                         np.array([current_x, current_y])) \
                                                           * (current_vector - mapp_1[current_x][current_y])

        if exp is not None:
            plt.imsave("images"+str(exp)+"/"+str(iters)+".png", mapp_1)

    return mapp_1, training_animation


def save_visualisation(mapp):
    """Create and save a png image of the SOM."""
    # Since Data is no longer representable in 2 or 3 dimensions
    # we will display a matrix of distances from adjecent vectors
    new = np.zeros((24, 24))

    for x in range(mapp.shape[0]):
        for y in range(mapp.shape[1]):
            spot = mapp[x][y]
            try:
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        new[x][y] += np.linalg.norm(spot - mapp[x+i][y+j])
            except IndexError:
                pass

    fig = plt.figure()
    ax = fig.add_subplot(111)
    cax = ax.matshow(new, interpolation='nearest')
    fig.colorbar(cax)
    plt.show()


def get_anomaly_score(log, mapp):
    """Compute a distance of a log entry to elements of SOM."""
    # convert log into vector using same word2vec model (here just going to grab from existing)
    dist_smallest = np.inf
    for x in range(mapp.shape[0]):
        for y in range(mapp.shape[1]):
            dist = np.linalg.norm(mapp[x][y] - log)  # cosine(som[x][y],log)#np.linalg.norm(som[x][y]-log)
            if dist < dist_smallest:
                dist_smallest = dist

    return dist_smallest

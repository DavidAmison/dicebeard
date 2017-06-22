import random
from shapely.geometry import Polygon
from shapely import affinity
import math
import numpy as np


def random_shape_placement(n, box, shape):
    '''
    Fit n of shape in box placed randomly. Return the centroids.

    Box and shape should both be of type shapely.geometry.Polygon
    '''
    # Generate the initial shapes
    shape = affinity.scale(shape, 1.1, 1.1)
    shapes = []
    centres = []
    for i in range(n):
        dx = random.randint(box.bounds[0], box.bounds[2])
        dy = random.randint(box.bounds[1], box.bounds[3])
        rotate = random.randint(0, 360)
        new_shape = affinity.rotate(shape, rotate)
        new_shape = affinity.translate(new_shape, dx, dy)
        shapes.append(new_shape)
        centres.append([dx, dy, rotate])

    shapes = _push_to_nearest(shapes, box)
    for i, item in enumerate(shapes):
        centres[i] = [
                (item.bounds[0]+item.bounds[2])/2,
                (item.bounds[1]+item.bounds[3])/2,
                centres[i][2]]
    return centres


def _push_to_nearest(shapes, frame):
    '''
    Moves Polygons until they don't intercept

    Any overlapping shapes are translated in a spiral pattern until they
    find a space
    '''
    for i, shape_1 in enumerate(shapes):
        shapes_upto_1 = shapes[:i]
        if not frame.contains(shape_1):
            shapes[i] = _move_shape(shape_1, shapes_upto_1, frame)
        for shape_2 in shapes_upto_1:
            if shape_1.intersects(shape_2):
                shapes[i] = _move_shape(shape_1, shapes_upto_1, frame)

    return shapes


def _move_shape(shape, shapes, frame):
    '''Moves shape_1 until it doesn't intersect any of the shapes in shapes'''
    theta = 0
    shape_1 = shape
    # Move the shape then check for overlap
    while _does_shape_intersect(shape_1, shapes, frame):
        theta += 0.5
        dx = theta*math.cos(theta)
        dy = theta*math.sin(theta)
        shape_1 = affinity.translate(shape, dx, dy)

    return shape_1


def _does_shape_intersect(shape_1, shapes, frame):
    '''
    Check if a shape type object intersects with
    '''
    for shape_2 in shapes:
        if shape_1.intersects(shape_2):
            return True

    if not frame.contains(shape_1):
        return True

    return False


def rand_points_with_push(n, box, sep):
    '''
    Generate a set of n random points within a box.

    Box should be a tuple containing the minimum and maximum co-ordinates
    desired in the form (xmin, xmax, ymin, ymax)
    '''

    # Generate the initial set of points
    x_coord = np.random.randint(box[0], box[1], (1, n)).astype(float)
    y_coord = np.random.randint(box[2], box[3], (1, n)).astype(float)

    return _push_points(x_coord, y_coord, box, sep)


def _push_points(x_coord, y_coord, box, sep):
    n = len(x_coord[0])
    force_const = sep * 2
    found_solution = False
    for foo in range(1, 1000):
        found_solution = True
        vel_x = np.zeros((n, n))
        vel_y = np.zeros((n, n))
        vel_walls = np.zeros((n, 4))

        one_array = np.ones((n, 1))
        X = (one_array * x_coord)
        Y = (one_array * y_coord)
        dX = X.T - X
        dY = Y.T - Y
        # Find the force between the points
        force_x = np.zeros((n, n))
        force_y = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                D = math.sqrt(dX[i][j]*dX[i][j] + dY[i][j]*dY[i][j])
                if D < sep and i != j:
                    found_solution = False
                if i != j and D != 0:
                    force_x[i][j] = force_const*dX[i][j]/(D*D*D)
                    force_y[i][j] = force_const*dY[i][j]/(D*D*D)
                elif i != j and D == 0:
                    force_x[i][j] = force_const

        # Find the new velocity (based on push from all other points)
        vel_x = vel_x + force_x
        vel_y = vel_y + force_y
        # Adjust the velocity based on push from the walls
        for i, vel_all in enumerate(vel_walls):
            for j, vel in enumerate(vel_all):
                coord = x_coord[0][i] if j < 2 else y_coord[0][i]
                D = coord - box[j]
                if abs(D) < sep:
                    found_solution = False
                vel_walls[i][j] += force_const*abs(D)/(D*D*D)

        # Check if the current points are a solution
        if found_solution:
            return np.append(x_coord, y_coord, axis=0).astype(int).T.tolist()

        # Move the points based on their current velocity
        for i in range(n):
            t = (box[1]+box[3]-box[0]-box[2])/15
            x_coord[0][i] += (sum(vel_x[i])+sum(vel_walls[i][:2]))*t
            y_coord[0][i] += (sum(vel_y[i])+sum(vel_walls[i][2:]))*t

            # If the dice is out of bounds centre it on that axis
            if x_coord[0][i] < box[0] or x_coord[0][i] > box[1]:
                x_coord[0][i] = (box[0]+box[1])/2
            if y_coord[0][i] < box[2] or y_coord[0][i] > box[3]:
                y_coord[0][i] = (box[2]+box[3])/2

    return np.append(x_coord, y_coord, axis=0).astype(int).T.tolist()


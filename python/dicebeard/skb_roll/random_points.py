import random
from shapely.geometry import Polygon
from shapely import affinity
import math


def random_shape_placement(n, box, shape):
    '''
    Fit n of shape in box placed randomly. Return the centroids.

    Box and shape should both be of type shapely.geometry.Polygon
    '''
    # Generate the initial shapes
    shape = affinity.scale(shape, 1.1, 1.1)
    shapes = []
    centres = []
    for i in range(0, n):
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
        shapes_excluding_1 = [shape for k, shape in enumerate(shapes) if k != i]
        if not frame.contains(shape_1):
            shapes[i] = _move_shape(shape_1, shapes_excluding_1, frame)
        for shape_2 in shapes_excluding_1:
            if shape_1.intersects(shape_2):
                shapes[i] = _move_shape(shape_1, shapes_excluding_1, frame)

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

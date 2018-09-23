
import math
import random

from sc2simulator import constants as c


################################################################################
def defineLocs(locP1, locP2, d, dim):
    """ensure both player locations are defined as map location tuples"""
    if not any([locP1, locP2]): # neither location is defined
        locP1 = pickValidMapLoc(dim)
        locP2 = pickBoundMapLoc(locP1, d, dim)
    elif locP1:
        locP1 = convertStrToPoint(locP1, dim)
        locP2 = pickBoundMapLoc(locP1, d, dim)
    elif options.player2.loc:
        locP2 = convertStrToPoint(locP2, dim)
        locP1 = pickBoundMapLoc(locP2, d, dim)
    else: # both player locs are defined already
        locP1 = convertStrToPoint(locP1, dim)
        locP2 = convertStrToPoint(locP2, dim)
    return (locP1, locP2)


################################################################################
def convertStrToPoint(value, dim=None):
    ret = [float(v) for v in value.split(",")]
    ret = ret[:3] # contain at most 3 dimensions
    ret += [0.0] * (3 - len(ret)) # always adjust to at least three dimensions
    if dim: # when dimensions are provided, also validate that the specified location is valid
        if not isValidLoc(ret, dim):
            raise ValueError("provided location %s is not within %s"%(
                str(ret),  str(dim)))
    return ret
    

################################################################################
def pickValidMapLoc(dimensions):
    """determine any location which is placeable on the map"""
    x, y = dimensions[:2]
    return (random.random() * x, random.random() * y, 0.0)


################################################################################
def isValidLoc(loc, dimensions):
    """whether loc is valid given map's dimensions"""
    x, y, z = loc
    maxX, maxY, maxZ  = dimensions
    return x >= 0 and x <= maxX and y >= 0 and y <= maxY


################################################################################
def pickBoundMapLoc(center, radius, dimensions, numAttempts=0):
    """pick a specific point 'radius' distance away from center, so long as """\
    """the point remains within the map's allowed dimensions"""
    maxX, maxY, dummy = dimensions
    angle = 2 * math.pi * random.random() # determine the position on the circle 
    r = radius
    circleX, circleY, dummy = center
    x = r * math.cos(angle) + circleX # calculate coordinates
    y = r * math.sin(angle) + circleY
    newLoc = (x, y, 0.0)
    if not isValidLoc(newLoc, dimensions):
        if numAttempts >= c.MAX_MAP_PICK_TRIES:
            raise Exception(("could not successfully pick a map location "\
             "after %d attempts given r=%s c=%s")%(numAttempts, r, str(center)))
        return pickBoundMapLoc(center, r, dimensions, numAttempts - 1) # another attempt is allowed
    return newLoc # return as map coordinates


################################################################################
def setLocation(scenario, techUnit, location, mapData):
    """determine the (valid) location for techUnit to be placed, accounting """\
    """for all previously placed units"""
    if mapData: # closed source package
        pass # TODO -- assign each unit's map location
    else:
        raise NotImplementedError("TODO -- assign each unit's map location")


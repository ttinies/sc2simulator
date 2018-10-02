
import itertools
import math
import random

from sc2simulator import constants as c

mapDimensions = None


################################################################################
def defineLocs(locP1, locP2, d):
    """ensure both player locations are defined as map location tuples"""
    global mapDimensions
    dim = mapDimensions
    if not any([locP1, locP2]): # neither location is defined
        locP1 = pickValidMapLoc()
        locP2 = pickBoundMapLoc(locP1, d)
    elif locP1:
        locP1 = convertStrToPoint(locP1, dim)
        locP2 = pickBoundMapLoc(locP1, d)
    elif locP2:
        locP2 = convertStrToPoint(locP2, dim)
        locP1 = pickBoundMapLoc(locP2, d)
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
def pickValidMapLoc(pad=30):
    """determine any location which is placeable on the map"""
    global mapDimensions
    x, y = mapDimensions[:2]
    w = x - (pad * 2)
    l = y - (pad * 2)
    return (pad + random.random() * (w),
            pad + random.random() * (l),
            0.0)


################################################################################
def isValidLoc(loc, dimensions, pad=30):
    """whether loc is valid given map's dimensions"""
    x, y, z = loc
    maxX, maxY, maxZ  = dimensions
    maxX -= pad
    maxY -= pad
    maxZ -= pad
    return x >= pad and x <= maxX and y >= pad and y <= maxY


################################################################################
def pickBoundMapLoc(center, radius, numAttempts=0):
    """pick a specific point 'radius' distance away from center, so long as """\
    """the point remains within the map's allowed dimensions"""
    global mapDimensions
    maxX, maxY, dummy = mapDimensions
    angle = 2 * math.pi * random.random() # determine the position on the circle 
    r = radius
    circleX, circleY, dummy = center
    x = r * math.cos(angle) + circleX # calculate coordinates
    y = r * math.sin(angle) + circleY
    newLoc = (x, y, 0.0)
    if not isValidLoc(newLoc, mapDimensions):
        if numAttempts >= c.MAX_MAP_PICK_TRIES:
            raise Exception(("could not successfully pick a map location "\
             "after %d attempts given r=%s c=%s")%(numAttempts, r, str(center)))
        else: numAttempts += 1
        return pickBoundMapLoc(center, r, numAttempts) # another attempt is allowed
    return newLoc # return as map coordinates


################################################################################
def setLocation(otherUnits, techUnit, location, field):
    """determine the (valid) location for techUnit to be placed, accounting """\
    """for all previously placed units"""
    if field: # object from Versentiedge closed source package
        ########################################################################
        def progressiveSquares(pt, idx=1):
            """locate a point as close as possible to idx"""
            validLocs = []
            uRad = techUnit.radius # assumed sc2techTree is available if sc2maps is as well
            cx, cy = pt
            minX = cx - idx # create bounding box outline
            maxX = cx + idx
            minY = cy - idx
            maxY = cy + idx
            for x in range(minX, maxX+1):
                pt1 = (x, minY, 0) # bottom row
                pt2 = (x, maxY, 0) # top row
                if field.canSet(pt1, uRad, goodVal=1): validLocs.append(pt1)
                if field.canSet(pt2, uRad, goodVal=1): validLocs.append(pt2)
            for y in range(minY+1, maxY+2): # exclude bottom/top rows
                pt1 = (minX, y, 0) # left side
                pt2 = (maxX, y, 0) # right side
                if field.canSet(pt1, uRad, goodVal=1): validLocs.append(pt1)
                if field.canSet(pt2, uRad, goodVal=1): validLocs.append(pt2)
            if validLocs: # found at least one valid location; pick one
                  pick = random.choice(validLocs)
                  newPt = [term / 2.0 for term in pick] # convert from 2x grid size field (for half points) back to normal grid coordinates
                  field.setValues(pick[:2], radius=[uRad]*2, newVal=0,
                      shape=c.cs.SQUARE) # don't overlap these coordinates anymore
                  #field.display()
                  return newPt
            else: return progressiveSquares(pt, idx=idx+1) # consider next square
        ########################################################################
        if techUnit.isAir: # air units can stack on top of each other without issue
            return location
        halfPt = [2 * term for term in location] # account for half grid
        halfLoc = c.cu.MapPoint(*halfPt)
        halfLoc = c.cf.gridSnap(halfLoc) # align to even grid since the field has even indexes
        return progressiveSquares((int(halfLoc.x), int(halfLoc.y)))
    else: # similar; can't guarentee that the placement is valid without field
        # TODO -- use otherUnits as the available locations
        raise NotImplementedError("TODO -- assign each unit's map location")


################################################################################
def pickCloserLoc(location, length):
    """picks a location 'length' distance toward the center from 'location'"""
    global mapDimensions
    dims = mapDimensions[:2]
    x, y = location[:2]
    if length == 0: # no need to calculate delta from location
        return (x, y)
    xMid, yMid = [i / 2.0 for i in dims]
    theta = math.atan2(yMid - y, xMid - x)
    newX = x + math.cos(theta) * length
    newY = y + math.sin(theta) * length
    return (newX, newY)


################################################################################
def pickFurtherLoc(location, length):
    """picks a location 'length' distance toward the center from 'location'"""
    global mapDimensions
    dims = mapDimensions[:2]
    x, y = location[:2]
    if length == 0: # no need to calculate delta from location
        return (x, y)
    xMid, yMid = [i / 2.0 for i in dims]
    theta = math.atan2(yMid - y, xMid - x)
    newX = x - math.cos(theta) * length
    newY = y - math.sin(theta) * length
    return (newX, newY)


#! python3
# Plays Minesweeper

import minesweeperBoardInterface
import random
from itertools import permutations

def runAlgorithm():
    board = minesweeperBoardInterface.initialBoardFind()
    allTileCoords = minesweeperBoardInterface.getAllTileCoords(board)

    # Pick a random start point
    boardHeight = len(allTileCoords)
    boardWidth = len(allTileCoords[0])
    startPos = allTileCoords[random.randint(0,boardHeight-1)][random.randint(0,boardWidth-1)]
    minesweeperBoardInterface.clickTiles([startPos])

    unresolvedCoords = [(x,y) for x in range(boardWidth) for y in range(boardHeight)]
    boardState = minesweeperBoardInterface.readBoard(board)

    while True:
        if gameFinished(boardState):
            return
        
        clickableBoardCoords = calculateSafeClicks(boardState, unresolvedCoords)
        if len(clickableBoardCoords) == 0:
            return
        clickablePixelCoords = convertBoardToPixel(clickableBoardCoords, allTileCoords)

        minesweeperBoardInterface.clickTiles(clickablePixelCoords)

        updateBoardState(boardState, board)

def updateBoardState(boardState, board):
    currentBoardState = minesweeperBoardInterface.readBoard(board)
    for y in range(len(boardState)):
        for x in range(len(boardState[y])):
            if boardState[y][x] in ["Unclicked", "Safe"]:
                boardState[y][x] = currentBoardState[y][x]

def gameFinished(boardState):
    for row in boardState:
        for item in row:
            if item == 'Unclicked':
                return False
    return True

def convertBoardToPixel(boardCoords, allTileCoords):
    return [allTileCoords[bc[1]][bc[0]] for bc in boardCoords ]

def calculateSafeClicks(boardState, unresolvedCoords):
    resolvedCoords = []
    for coord in unresolvedCoords:
        currentTile = getTileValue(coord, boardState)
        if currentTile in ["Unclicked", "Mine", "Safe"]:
            # No clue - nothing to deduce
            continue
        currentTileValue = int(currentTile)

        neighbourhood = getNeighbourhood(coord, boardState)
        deductions = getNeighbourhoodDeductions(boardState, neighbourhood, currentTileValue)
        applyDeductionsToBoardState(boardState, neighbourhood, deductions)
        if deductionsComplete(deductions):
            resolvedCoords.append(coord)
    unresolvedCoords = [x for x in unresolvedCoords if x not in resolvedCoords]
    clickableCoords = [(x,y) for x in range(len(boardState[0])) for y in range(len(boardState)) if boardState[y][x] == "Safe"]
    return clickableCoords

def getNeighbourhood(coord, boardState):
    neighbourhoodCandidates = [(coord[0] + i, coord[1] + j) for i in range(-1,2) for j in range(-1,2) if (i!=0 or j!=0)]
    validX = range(0, len(boardState[0]))
    validY = range(0, len(boardState))
    output = [neighbour for neighbour in neighbourhoodCandidates if neighbour[0] in validX and neighbour[1] in validY]
    return output

def getNeighbourhoodDeductions(boardState, neighbourhood, tileValue):
    # Find every possible way of populating the boardState in this neighbourhood
    unclickedTiles = [xy for xy in neighbourhood if getTileValue(xy, boardState) == "Unclicked"]
    if len(unclickedTiles) == 0:
        return [getTileValue(coordinate, boardState) for coordinate in neighbourhood]
    knownMineCount = len([xy for xy in neighbourhood if getTileValue(xy, boardState) == "Mine"])
    minesRemaining = tileValue - knownMineCount
    minePermutations = generateMinePermutations(len(unclickedTiles), minesRemaining)
    # Test each one for potential legality
    permLegalities = []
    for perm in minePermutations:
        testBoardState = generateTestBoardState(boardState, unclickedTiles, perm)
        legal = validBoardstate(testBoardState)
        permLegalities.append(legal)
    # Collect all legal possibilities to find common factors
    validPerms = [minePermutations[i] for i in range(len(minePermutations)) if permLegalities[i] == True]
    # Return common factors - this is what has been deduced 
    common = extractCommonalities(validPerms)
    unclickedTileDeductions = extractCommonalities(validPerms)
    neighbourhoodDeductions = list(range(len(neighbourhood)))
    for i in range(len(neighbourhoodDeductions)):
        neighbour = neighbourhood[i]
        if neighbour in unclickedTiles:
            unclickedIndex = unclickedTiles.index(neighbour)
            neighbourhoodDeductions[i] = unclickedTileDeductions[unclickedIndex]
        else:
            neighbourhoodDeductions[i] = getTileValue(neighbour, boardState)
    return  neighbourhoodDeductions

def extractCommonalities(perms):
    output = perms[0]
    for perm in perms:
        for i in range(len(output)):
            if output[i] != perm[i]:
                output[i] = "Unknown"
    return output

def generateTestBoardState(boardState, alteredTileCoords, alteredTileValues):
    newBoardState = [list(row) for row in boardState]
    for i in range(len(alteredTileCoords)):
        coord = alteredTileCoords[i]
        newValue = alteredTileValues[i]
        if newValue in ["Mine", "Safe"]:
            newBoardState[coord[1]][coord[0]] = alteredTileValues[i]
    return newBoardState

def generateMinePermutations(n,r):
    items = ["Safe" for x in range(n)]
    items[:r] = ["Mine" for x in range(r)]
    perms = set(permutations(items))
    output=[]
    for j in perms:
        output.append(list(j))
    return output

def applyDeductionsToBoardState(boardState, neighbourhood, deductions):
    for i in range(len(neighbourhood)):
        coords = neighbourhood[i]
        if deductions[i] != "Unknown":
            boardState[coords[1]][coords[0]] = deductions[i]

def deductionsComplete(deductions):
    return len([x for x in deductions for x in ['Unknown']]) == 0

def validBoardstate(boardState):
    for y in range(len(boardState)):
        for x in range(len(boardState[y])):
            if not validForCoord((x,y), boardState):
                return False
    return True

def validForCoord(coord, boardState):
    currentTile = getTileValue(coord, boardState)
    if currentTile in ["Unclicked", "Mine", "Safe"]:
        return True

    neighbourhood = getNeighbourhood(coord, boardState)
    knownMineCount = len([xy for xy in neighbourhood if getTileValue(xy, boardState) == "Mine"])
    unclickedCount = len([xy for xy in neighbourhood if getTileValue(xy, boardState) == "Unclicked"])
    tileValue = int(currentTile)

    return knownMineCount <= tileValue and tileValue <= unclickedCount + knownMineCount 

def getTileValue(coord, boardState): 
    return boardState[coord[1]][coord[0]]

runAlgorithm()

# Further ideas:
#   Have the board interface constantly poll the screen in another thread (and make clicks as you go)
#   Keep track of total mines somehow and factor into logic
#   Grab easy win deductions first
#   Place flags
#   More light-weight screen-reading code
#   Guess when there are no more moves to make
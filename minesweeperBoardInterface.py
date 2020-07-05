#! python3
# Provides functionality for reading a Minesweeper board (at 150% res), etc.

import pyautogui, math

pyautogui.PAUSE = 0.1

scriptDir = 'your dir here'
tiles = {
    'Unclicked':r'Unclicked.png',
    '0':r'0.png',
    '1':r'1.png',
    '2':r'2.png',
    '3':r'3.png',
    '4':r'4.png',
    '5':r'5.png',
    '6':r'6.png',
    '7':r'7.png',
    '8':r'8.png'
}

def getAllXTiles(tile, region=None):
    areas = pyautogui.locateAllOnScreen(scriptDir + tiles[tile], region=region)
    centres = [pyautogui.center(area) for area in areas]
    return centres

def readBoard(board):
    imageLocations = {k: getAllXTiles(k, region=board) for k in tiles.keys()}
    return [[determineTile(coord, imageLocations) for coord in row] for row in getAllTileCoords(board)]

def determineTile(tileCoord, imageLocations):
    for tile in imageLocations.keys():
        for location in imageLocations[tile]:
            if location[0] == tileCoord[0] and location[1] == tileCoord[1]:
                imageLocations[tile].remove(location)
                return tile
    return None

def initialBoardFind():
    allUnclickedTiles = getAllXTiles('Unclicked')
    minX = -12 + min([t[0] for t in allUnclickedTiles])
    maxX = 12 + max([t[0] for t in allUnclickedTiles])
    minY = -12 + min([t[1] for t in allUnclickedTiles])
    maxY = 12 + max([t[1] for t in allUnclickedTiles])
    return (minX, minY, maxX, maxY)

def getAllTileCoords(board):
    horizontalTileCount = int((board[2] -board[0]) // 24)
    verticalTileCount = int((board[3] - board[1]) // 24)
    tileCoords = []
    for j in range(verticalTileCount):
        row = []
        for i in range(horizontalTileCount):
            x = int(board[0] + 24*i + 12)
            y = int(board[1] + 24*j + 12)
            row.append((x,y))
        tileCoords.append(row)
    return tileCoords

def clickTiles(coords):
    for coord in coords:
        pyautogui.doubleClick(coord)

# Idea for performance improvement
#   Figure out a way to just sample pixels from a tile to determine its value
#   Use this approach to do <N checks rather than use the hefty locateAllOnScreen on each read

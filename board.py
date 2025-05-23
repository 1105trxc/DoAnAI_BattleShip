import pygame
from constants import WHITE 

def createGameGrid(rows, cols, cellsize, pos):
    """Creates a 2D list of coordinates for the top-left corner of each grid cell."""
    startX, startY = pos
    coordGrid = []
    for row in range(rows):
        rowX = []
        current_startX = startX # Reset startX for each row
        for col in range(cols):
            rowX.append((current_startX, startY))
            current_startX += cellsize
        coordGrid.append(rowX)
        startY += cellsize
    return coordGrid


def showGridOnScreen(window, cellsize, playerGridCoords, computerGridCoords):
    """Draws the grid lines on the screen by drawing individual cell rectangles (like original code)."""
    gamegrids_coords = [playerGridCoords, computerGridCoords]
    for grid_coords in gamegrids_coords:
        if not grid_coords: continue # Skip if grid data is empty

        for row in grid_coords:
            for col_coord in row:
                # Draw the white rectangle for each cell
                pygame.draw.rect(window, WHITE, (col_coord[0], col_coord[1], cellsize, cellsize), 1)
       
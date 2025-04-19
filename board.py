import pygame
from constants import CELLSIZE, WHITE # Import constants needed

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

# Trong file board.py

def showGridOnScreen(window, cellsize, playerGridCoords, computerGridCoords):
    """Draws the grid lines on the screen by drawing individual cell rectangles (like original code)."""
    gamegrids_coords = [playerGridCoords, computerGridCoords]
    for grid_coords in gamegrids_coords:
        if not grid_coords: continue # Skip if grid data is empty

        # === HOÀN TÁC LẠI LOGIC VẼ LƯỚI GỐC ===
        for row in grid_coords:
            for col_coord in row:
                # Vẽ hình chữ nhật trắng cho mỗi ô
                pygame.draw.rect(window, WHITE, (col_coord[0], col_coord[1], cellsize, cellsize), 1)
        # === KẾT THÚC HOÀN TÁC ===

        # Original code drew individual rects, this draws lines which is usually cleaner
        # for row in grid_coords:
        #     for col_coord in row:
        #         pygame.draw.rect(window, WHITE, (col_coord[0], col_coord[1], cellsize, cellsize), 1)
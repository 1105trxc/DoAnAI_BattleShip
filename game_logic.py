import pygame
import random
from constants import CELLSIZE # Import constants
from game_objects import MessageBox 

# --- Grid Logic Functions ---

def createGameLogic(rows, cols):
    """Creates a 2D list representing the logical state of the grid."""
    gamelogic = []
    for _ in range(rows):
        gamelogic.append([' '] * cols) # ' ' = Empty, 'O' = Occupied, 'T' = Hit, 'X' = Miss
    return gamelogic

def updateGameLogic(coordGrid, shiplist, gamelogic):
    """Updates the logical grid based on current ship positions."""
    rows = len(gamelogic)
    cols = len(gamelogic[0])

    # Reset non-hit/miss cells to empty first
    for r in range(rows):
        for c in range(cols):
            if gamelogic[r][c] not in ('T', 'X'):
                gamelogic[r][c] = ' '

    # Mark cells occupied by ships
    for ship in shiplist:
        # Iterate through grid cells and check for collision with the ship's rect
        for r in range(rows):
            for c in range(cols):
                # Create a rect for the current cell
                cell_rect = pygame.Rect(coordGrid[r][c][0], coordGrid[r][c][1], CELLSIZE, CELLSIZE)
                if ship.rect.colliderect(cell_rect):
                    if gamelogic[r][c] == ' ':
                        gamelogic[r][c] = 'O'


def printGameLogic(pGameLogic, cGameLogic):
    """Prints the logical grids to the console for debugging."""
    print('Player Grid'.center(50, '#'))
    for row in pGameLogic:
        print(row)
    print('Computer Grid'.center(50, '#'))
    for row in cGameLogic:
        print(row)

# --- Ship Placement and Management ---

def sortFleet(ship, shiplist):
    """Moves the selected ship to the end of the list for drawing priority."""
    if ship in shiplist:
        shiplist.remove(ship)
        shiplist.append(ship)

def randomizeShipPositions(shiplist, gamegrid_coords):
    """Places ships randomly on the grid without overlapping, applying centering."""
    placedShipsRects = [] 
    if not gamegrid_coords: return 
    rows = len(gamegrid_coords)
    if rows == 0: return
    cols = len(gamegrid_coords[0])
    if cols == 0: return

    for ship in shiplist:
        validPosition = False
        attempts = 0
        max_attempts = 100 # Prevent infinite loops

        while not validPosition and attempts < max_attempts:
            attempts += 1
            if ship.rotation:
                ship.rotateShip(True) 

            # Choose rotation randomly
            rotateShip = random.choice([True, False])
            temp_rect = None

            if rotateShip: # Try horizontal placement
                 ship.rotateShip(True) # Rotate to horizontal for size check
                 ship_width_cells = (ship.hImageWidth + CELLSIZE - 1) // CELLSIZE # Cells needed horizontally
                 max_row = rows - 1
                 max_col = cols - ship_width_cells
                 if max_col < 0 : max_col = 0 # Ensure index isn't negative

                 if max_row >= 0 and max_col >= 0:
                     yAxis = random.randint(0, max_row)
                     xAxis = random.randint(0, max_col)
                     potential_pos = gamegrid_coords[yAxis][xAxis] # Top-left of starting cell

                     # === ÁP DỤNG CĂN CHỈNH NGANG ===
                     final_left = potential_pos[0]
                     final_top = potential_pos[1] + (CELLSIZE - ship.hImageHeight) // 2
                     # === KẾT THÚC ÁP DỤNG ===

                     temp_rect = ship.hImageRect.copy()
                     temp_rect.topleft = (final_left, final_top) # Gán tọa độ đã căn chỉnh
                 else:
                      ship.rotateShip(True) # Rotate back if placement impossible
                      continue # Try again

            else: 
                 ship_height_cells = (ship.vImageHeight + CELLSIZE - 1) // CELLSIZE # Cells needed vertically
                 max_row = rows - ship_height_cells
                 max_col = cols - 1
                 if max_row < 0 : max_row = 0
                 if max_col < 0 : max_col = 0

                 if max_row >= 0 and max_col >= 0:
                     yAxis = random.randint(0, max_row)
                     xAxis = random.randint(0, max_col)
                     potential_pos = gamegrid_coords[yAxis][xAxis] # Top-left of starting cell

                     # === ÁP DỤNG CĂN CHỈNH DỌC ===
                     final_left = potential_pos[0] + (CELLSIZE - ship.vImageWidth) // 2
                     final_top = potential_pos[1]
                     # === KẾT THÚC ÁP DỤNG ===

                     temp_rect = ship.vImageRect.copy()
                     temp_rect.topleft = (final_left, final_top) # Gán tọa độ đã căn chỉnh
                 else:
                      continue # Try again

            # Check collision with already placed ships
            collision = False
            if temp_rect:
                 for placed_rect in placedShipsRects:
                      # Add a small buffer to collision check if needed? (Optional)
                      # inflated_rect = placed_rect.inflate(2, 2) # Example buffer
                      # if temp_rect.colliderect(inflated_rect):
                      if temp_rect.colliderect(placed_rect):
                           collision = True
                           break
            else:
                 collision = True # No valid position generated

            if not collision and temp_rect:
                 validPosition = True
                 ship.rect = temp_rect
                 ship.vImageRect.center = ship.hImageRect.center = ship.rect.center # Sync rects
                 placedShipsRects.append(ship.rect) # Add current ship's rect
                 ship.rotation = rotateShip
                 ship.switchImageAndRect() # Update image based on final rotation              
            else:
                 if ship.rotation != rotateShip: # If rotation was attempted but failed
                     ship.rotateShip(True) # Toggle back to vertical (default)

        if not validPosition:
             print(f"Warning: Could not place ship {ship.name} after {max_attempts} attempts.")
             ship.returnToDefaultPosition() # Place at default as fallback
             placedShipsRects.append(ship.rect)


# Trong game_logic.py
def resetShips(shiplist, reset_position=True): # Thêm tham số, mặc định là True
    """Resets ships in the list. Optionally resets position."""
    for ship in shiplist:
        if reset_position: # Chỉ gọi returnToDefaultPosition nếu reset_position là True
            ship.returnToDefaultPosition()
        ship.is_sunk = False # Luôn reset trạng thái is_sunk


def areShipsPlacedCorrectly(shiplist, gridCoords):
    """Checks if all ships are fully within the grid boundaries."""
    if not gridCoords: return False # No grid defined
    grid_left = gridCoords[0][0][0]
    grid_top = gridCoords[0][0][1]
    grid_right = gridCoords[0][-1][0] + CELLSIZE
    grid_bottom = gridCoords[-1][0][1] + CELLSIZE

    for ship in shiplist:
        # Check if any part of the ship is outside the grid
        if ship.rect.left < grid_left or \
           ship.rect.right > grid_right or \
           ship.rect.top < grid_top or \
           ship.rect.bottom > grid_bottom:
            return False # Found a ship outside boundaries
    return True 


# --- Game Turn and Win Condition Logic ---

def deploymentPhase(current_deployment_status):
    """Toggles the deployment status."""
    return not current_deployment_status

def takeTurns(player1, computer, pGameLogic, pGameGrid, pFleet, cGameLogic, cGameGrid, cFleet, tokens_list, message_boxes_list, sounds, current_time, last_computer_attack_time):
    """Manages the turn switching and computer's attack execution."""
    new_last_attack_time = last_computer_attack_time

    if not player1.turn and computer.turn:
        # It's computer's turn to potentially attack
        attack_made, turn_continues = computer.makeAttack(
            pGameLogic, pGameGrid, pFleet, tokens_list, message_boxes_list, sounds, current_time, last_computer_attack_time
        )
        if attack_made:
            new_last_attack_time = current_time # Update time only if attack happened
            if not turn_continues: # If computer's turn ended (missed)
                player1.turn = True
                computer.turn = False
        # If attack wasn't made (timer delay), turns don't switch yet
    # elif player1.turn and not computer.turn:
        # Player's turn is handled by mouse clicks in main loop
        # If player misses, main loop should set player1.turn = False, computer.turn = True
        pass

    return new_last_attack_time # Return the updated time

def checkForWinners(logic_grid):
    """Checks if all 'O' (occupied) cells have been turned to 'T' (hit)."""
    for row in logic_grid:
        if 'O' in row:
            return False # Found an intact ship part, game not over
    return True # No 'O' left, all ships hit

# --- Hit and Sink Logic ---

def checkAndNotifyDestroyedShip(grid_coords, logicGrid, shiplist, message_boxes_list):
    """Checks if any ship has been sunk and adds notification."""
    newly_destroyed_ship = None # Track if a ship was just destroyed in this check

    for ship in shiplist:
        if ship.is_sunk: continue # Skip already sunk ships

        is_ship_hit_everywhere = True
        ship_cells_found = False
        rows = len(grid_coords)
        cols = len(grid_coords[0])

        # Find all grid cells occupied by this ship
        for r in range(rows):
            for c in range(cols):
                cell_rect = pygame.Rect(grid_coords[r][c][0], grid_coords[r][c][1], CELLSIZE, CELLSIZE)
                if ship.rect.colliderect(cell_rect):
                    ship_cells_found = True
                    # Check the logic grid state for this cell
                    if logicGrid[r][c] != 'T':
                        is_ship_hit_everywhere = False
                        break # No need to check further cells for this ship
            if not is_ship_hit_everywhere:
                break # Stop checking rows for this ship

        # If all found cells are 'T' and we actually found cells belonging to the ship
        if ship_cells_found and is_ship_hit_everywhere:
            ship.is_sunk = True
            newly_destroyed_ship = ship # Store the ship that was just sunk
            # Add message using the MessageBox class
            # Always use hImage for consistency in message box display?
            message_boxes_list.append(MessageBox(f"{ship.name.upper()} DESTROYED!", ship.hImage, duration=3000)) # Longer duration
            # Play sink sound? (Should be handled where hit occurs)

    return newly_destroyed_ship # Return the ship object if one was newly sunk


def get_ship_at_coord(grid_coords, fleet, row, col, gamelogic=None, sunk_check=False):
    """
    Finds the ship object at a given grid coordinate.
    If sunk_check is True, returns the cells only if the ship is fully sunk ('T').
    If gamelogic is provided, uses it to verify sunk status.
    Returns a list of (r, c) tuples for the ship's cells, or empty list.
    """
    if not (0 <= row < len(grid_coords) and 0 <= col < len(grid_coords[0])):
         return [] # Invalid coords

    target_rect = pygame.Rect(grid_coords[row][col][0], grid_coords[row][col][1], CELLSIZE, CELLSIZE)
    found_ship = None
    for ship in fleet:
        # Check collision and also ensure the ship isn't already marked as sunk internally
        # if ship.rect.colliderect(target_rect) and (not sunk_check or not ship.is_sunk):
        # Simpler: just check collision first
        if ship.rect.colliderect(target_rect):
            found_ship = ship
            break

    if found_ship:
        ship_cells = []
        rows, cols = len(grid_coords), len(grid_coords[0])
        # Find all cells for this specific ship
        for r in range(rows):
            for c in range(cols):
                cell_rect = pygame.Rect(grid_coords[r][c][0], grid_coords[r][c][1], CELLSIZE, CELLSIZE)
                if found_ship.rect.colliderect(cell_rect):
                    ship_cells.append((r, c))

        # If checking for sunk status, verify using gamelogic if provided
        if sunk_check and gamelogic:
            is_truly_sunk = all(gamelogic[r][c] == 'T' for r, c in ship_cells) if ship_cells else False
            return ship_cells if is_truly_sunk else []
        elif sunk_check and not gamelogic:
             # Rely on internal ship.is_sunk flag if logic grid not available
             return ship_cells if found_ship.is_sunk else []
        else:
            # Just return all cells if not checking sunk status
            return ship_cells

    return [] # No ship found at the coordinate
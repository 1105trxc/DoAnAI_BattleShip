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

def get_ship_placement_rect(ship, row, col, orientation, grid_coords, CELLSIZE):
    """Calculates the placement rectangle for a ship based on its position and orientation."""
    if orientation == "horizontal":
        left = grid_coords[row][col][0]
        top = grid_coords[row][col][1] + (CELLSIZE - ship.hImageHeight) // 2
        return pygame.Rect(left, top, ship.hImageWidth, ship.hImageHeight)
    elif orientation == "vertical":
        left = grid_coords[row][col][0] + (CELLSIZE - ship.vImageWidth) // 2
        top = grid_coords[row][col][1]
        return pygame.Rect(left, top, ship.vImageWidth, ship.vImageHeight)
    return None

def randomizeShipPositions(shiplist, gamegrid_coords):
    """Places ships on the grid using a randomized recursive Backtracking algorithm."""
    if not gamegrid_coords or not shiplist:
        return False  # Invalid input

    rows = len(gamegrid_coords)
    cols = len(gamegrid_coords[0])
    placed_ship_rects = []  # Store pygame.Rect objects for collision checking

    def is_valid_position(ship_rect):
        """Checks if a ship's placement is valid within the grid and does not overlap with other ships."""
        # Check if the rectangle is within grid boundaries
        if ship_rect.left < gamegrid_coords[0][0][0] or \
           ship_rect.right > gamegrid_coords[0][-1][0] + CELLSIZE or \
           ship_rect.top < gamegrid_coords[0][0][1] or \
           ship_rect.bottom > gamegrid_coords[-1][0][1] + CELLSIZE:
            return False

        # Check for collisions with already placed ships
        for placed_rect in placed_ship_rects:
            if ship_rect.colliderect(placed_rect):
                return False

        return True

    def place_ship(ship_index):
        """Recursive function to place ships using Backtracking."""
        if ship_index == len(shiplist):
            return True  # All ships placed successfully

        ship = shiplist[ship_index]
        # Generate all possible positions and orientations for the current ship
        positions = [(row, col, orientation) for row in range(rows) for col in range(cols) for orientation in ["horizontal", "vertical"]]
        random.shuffle(positions)  # Shuffle positions to randomize placement order

        for row, col, orientation in positions:
            # Calculate the ship's placement rectangle
            ship_rect = get_ship_placement_rect(ship, row, col, orientation, gamegrid_coords, CELLSIZE)

            if ship_rect and is_valid_position(ship_rect):
                # Temporarily place the ship
                ship.rect = ship_rect
                ship.rotation = (orientation == "horizontal")
                ship.switchImageAndRect()
                placed_ship_rects.append(ship.rect)

                # Recurse to place the next ship
                if place_ship(ship_index + 1):
                    return True

                # Backtrack: Remove the ship from the placed list
                placed_ship_rects.pop()

        return False

    # Shuffle the shiplist to ensure different placement orders
    random.shuffle(shiplist)

    # Start the Backtracking process
    if not place_ship(0):
        print("Warning: Could not place all ships.")
        for ship in shiplist:
            ship.returnToDefaultPosition()  # Reset ships if placement fails
        return False

    # Update the game logic grid
    updateGameLogic(gamegrid_coords, shiplist, createGameLogic(rows, cols))
    return True



def resetShips(shiplist, reset_position=True): 
    """Resets ships in the list. Optionally resets position."""
    for ship in shiplist:
        if reset_position: # Chỉ gọi returnToDefaultPosition nếu reset_position là True
            ship.returnToDefaultPosition()
        ship.is_sunk = False # Alway reset sunk status


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
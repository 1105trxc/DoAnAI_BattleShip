import pygame
import random
from constants import CELLSIZE, SCREENWIDTH, ROWS, COLS # Assuming these are defined in constants.py
class Player:
    def __init__(self):
        self.turn = True # Player usually starts

    def makeAttack(self, grid_coords, logic_grid, enemy_fleet, tokens_list, message_boxes_list, sounds):
        posX, posY = pygame.mouse.get_pos()
        grid_start_x = grid_coords[0][0][0]
        grid_end_x = grid_coords[0][-1][0] + CELLSIZE
        grid_start_y = grid_coords[0][0][1]
        grid_end_y = grid_coords[-1][0][1] + CELLSIZE

        if grid_start_x <= posX < grid_end_x and grid_start_y <= posY < grid_end_y:
            # Calculate grid indices from mouse position
            col = (posX - grid_start_x) // CELLSIZE
            row = (posY - grid_start_y) // CELLSIZE

            # Ensure calculated indices are within bounds
            if 0 <= row < len(logic_grid) and 0 <= col < len(logic_grid[0]):
                cell_state = logic_grid[row][col]

                if cell_state == 'O': # Hit an occupied cell
                    logic_grid[row][col] = 'T' # Mark as Target Hit
                    # Add Hit Token (Need Red Token image - should be loaded in main and passed)
                    from main import REDTOKEN, FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST # Assuming loaded in main
                    tokens_list.append(Tokens(REDTOKEN, grid_coords[row][col], 'Hit', FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST))

                    if sounds.get('shot'): sounds['shot'].play()
                    if sounds.get('hit'): sounds['hit'].play()

                elif cell_state == ' ': # Miss an empty cell
                    logic_grid[row][col] = 'X' # Mark as Miss
                    # Add Miss Token (Need Green Token image)
                    from main import GREENTOKEN # Assuming loaded in main
                    tokens_list.append(Tokens(GREENTOKEN, grid_coords[row][col], 'Miss'))

                    if sounds.get('shot'): sounds['shot'].play()
                    if sounds.get('miss'): sounds['miss'].play()

                    self.turn = False # Player loses turn after a miss

                # If cell_state is 'T' or 'X', do nothing (already attacked)
                return True # Attack was made (or attempted on already attacked cell)

        return False # Click was outside the grid


class EasyComputer:
    def __init__(self):
        self.turn = False
        self.status_font = pygame.font.SysFont('Stencil', 22) # Load font once
        self.status_text = 'Thinking'
        self.name = 'Easy Computer'

    def computerStatus(self, msg):
        # Renders the status message
        message = self.status_font.render(msg, 1, (0, 0, 0)) # Black text
        return message

    def makeAttack(self, gamelogic, grid_coords, enemy_fleet, tokens_list, message_boxes_list, sounds, current_time, last_attack_time):
        attack_delay = 1000 # 1 second delay

        if current_time - last_attack_time >= attack_delay:
            rows = len(gamelogic)
            cols = len(gamelogic[0])
            validChoice = False
            attempts = 0 # Prevent infinite loop if grid is full
            max_attempts = rows * cols * 2

            while not validChoice and attempts < max_attempts:
                rowX = random.randint(0, rows - 1)
                colX = random.randint(0, cols - 1)
                if gamelogic[rowX][colX] in [' ', 'O']: # Can attack empty or ship cells
                    validChoice = True
                attempts += 1

            if validChoice:
                cell_state = gamelogic[rowX][colX]
                cell_pos = grid_coords[rowX][colX]

                if cell_state == 'O': # Hit
                    gamelogic[rowX][colX] = 'T'
                    from main import REDTOKEN, FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST # Loaded in main
                    tokens_list.append(Tokens(REDTOKEN, cell_pos, 'Hit', FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST))
                    if sounds.get('shot'): sounds['shot'].play()
                    if sounds.get('hit'): sounds['hit'].play()

            else:
                 # Could not find a valid cell (should only happen if grid full of T/X)
                 self.turn = False
                 return False, False # No attack made, turn ends (failsafe)


        return False, self.turn # No attack made yet (due to timer), return current turn status

    def draw(self, window, grid_coords):
        if self.turn:
            status_surface = self.computerStatus(self.status_text)
            from constants import SCREENWIDTH, ROWS, CELLSIZE # Get grid position info
            comp_grid_start_x = SCREENWIDTH - (ROWS * CELLSIZE)
            comp_grid_end_y = 50 + (ROWS * CELLSIZE) # Assuming start y=50
            status_pos = (comp_grid_start_x - CELLSIZE, comp_grid_end_y + 10) # Below grid
            window.blit(status_surface, status_pos)


class MediumComputer(EasyComputer):
    def __init__(self):
        super().__init__()
        self.name = 'Medium Computer'
        self.hits = [] # List of (row, col) tuples of successful hits on *unsunk* ships

    def makeAttack(self, gamelogic, grid_coords, enemy_fleet, tokens_list, message_boxes_list, sounds, current_time, last_attack_time):
        attack_delay = 1000 # 1 second delay

        if current_time - last_attack_time >= attack_delay:
            rows = len(gamelogic)
            cols = len(gamelogic[0])

            # ** Hunting Mode **
            potential_targets = []
            if self.hits:
                # Find adjacent cells to existing hits that haven't been attacked yet
                for r, c in self.hits:
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]: # N, S, W, E
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols and gamelogic[nr][nc] in [' ', 'O']:
                            if (nr, nc) not in potential_targets:
                                potential_targets.append((nr, nc))

            target_coord = None
            if potential_targets:
                # Prioritize adjacent cells
                target_coord = random.choice(potential_targets)
            else:
                self.hits.clear()
                validChoice = False
                attempts = 0
                max_attempts = rows * cols * 2
                while not validChoice and attempts < max_attempts:
                    rowX = random.randint(0, rows - 1)
                    colX = random.randint(0, cols - 1)
                    if gamelogic[rowX][colX] in [' ', 'O']:
                        validChoice = True
                        target_coord = (rowX, colX)
                    attempts += 1

            if target_coord:
                rowX, colX = target_coord
                cell_state = gamelogic[rowX][colX]
                cell_pos = grid_coords[rowX][colX]

                if cell_state == 'O': # Hit
                    gamelogic[rowX][colX] = 'T'
                    from main import REDTOKEN, FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST
                    tokens_list.append(Tokens(REDTOKEN, cell_pos, 'Hit', FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST))
                    if sounds.get('shot'): sounds['shot'].play()
                    if sounds.get('hit'): sounds['hit'].play()

                    # Add to hits list FOR NEXT TURN's targeting
                    if (rowX, colX) not in self.hits:
                        self.hits.append((rowX, colX))


                elif cell_state == ' ': # Miss
                    gamelogic[rowX][colX] = 'X'
                    from main import BLUETOKEN
                    tokens_list.append(Tokens(BLUETOKEN, cell_pos, 'Miss'))
                    if sounds.get('shot'): sounds['shot'].play()
                    if sounds.get('miss'): sounds['miss'].play()

                    # Remove this potential target if it was adjacent to a hit
                    if (rowX, colX) in potential_targets:
                         pass # No need to remove, just missed

                    self.turn = False # End turn
                    return True, False # Attack made, turn ends
            else:
                 # No valid cell found
                 self.turn = False
                 return False, False

        return False, self.turn # Timer delay


class HardComputer(EasyComputer):
    def __init__(self):
        super().__init__()
        self.name = 'Hard Computer'
        self.target_list = [] # List of coordinates to attack (priority) [(r,c), ...]
        self.hunting_mode = False # Are we currently focused on sinking a found ship?
        self.last_hit = None # Coordinates of the most recent successful hit (r, c)
        self.attack_pattern = [] # Stores pattern (e.g., 'horizontal', 'vertical') if detected

    def makeAttack(self, gamelogic, grid_coords, enemy_fleet, tokens_list, message_boxes_list, sounds, current_time, last_attack_time):
        attack_delay = 800 # Harder AI attacks slightly faster

        if current_time - last_attack_time >= attack_delay:
            rows = len(gamelogic)
            cols = len(gamelogic[0])

            target_coord = None

            # ** Priority 1: Attack from Target List (Hunting Mode) **
            if self.target_list:
                target_coord = self.target_list.pop(0) # Get the next priority target
                # Sanity check if the target is still valid
                if not (0 <= target_coord[0] < rows and 0 <= target_coord[1] < cols and gamelogic[target_coord[0]][target_coord[1]] in [' ', 'O']):
                    target_coord = None # Invalid target, try next logic
                    self.hunting_mode = bool(self.target_list) # Stay hunting if list not empty

            # ** Priority 2: Random Attack (Searching Mode) **
            if not target_coord:
                self.hunting_mode = False # Switch off hunting mode if target list exhausted or empty
                self.last_hit = None
                self.attack_pattern = []
                validChoice = False
                attempts = 0
                max_attempts = rows * cols * 2
                while not validChoice and attempts < max_attempts:
                    rowX = random.randint(0, rows - 1)
                    colX = random.randint(0, cols - 1)
                    if gamelogic[rowX][colX] in [' ', 'O']:
                        validChoice = True # Simpler random for now
                        target_coord = (rowX, colX)

                    attempts += 1


            # ** Process the chosen target_coord **
            if target_coord:
                rowX, colX = target_coord
                cell_state = gamelogic[rowX][colX]
                cell_pos = grid_coords[rowX][colX]

                if cell_state == 'O': # --- HIT ---
                    gamelogic[rowX][colX] = 'T'
                    from main import REDTOKEN, FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST
                    tokens_list.append(Tokens(REDTOKEN, cell_pos, 'Hit', FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST))
                    if sounds.get('shot'): sounds['shot'].play()
                    if sounds.get('hit'): sounds['hit'].play()

                    current_hit = (rowX, colX)

                    # --- Update Targeting Logic ---
                    if not self.hunting_mode: # First hit on a new ship
                        self.hunting_mode = True
                        self.last_hit = current_hit
                        # Add adjacent cells to target list
                        self.add_adjacent_targets(current_hit, gamelogic)
                    else: # Subsequent hit while hunting
                         # Try to determine pattern (horizontal/vertical)
                         if self.last_hit:
                             dr = current_hit[0] - self.last_hit[0]
                             dc = current_hit[1] - self.last_hit[1]
                             if dr != 0 and dc == 0 and 'vertical' not in self.attack_pattern:
                                 self.attack_pattern.append('vertical')
                                 # Remove horizontal targets if pattern confirmed vertical
                                 self.target_list = [(r,c) for r,c in self.target_list if c == self.last_hit[1]]
                             elif dc != 0 and dr == 0 and 'horizontal' not in self.attack_pattern:
                                 self.attack_pattern.append('horizontal')
                                 # Remove vertical targets if pattern confirmed horizontal
                                 self.target_list = [(r,c) for r,c in self.target_list if r == self.last_hit[0]]

                         self.last_hit = current_hit
                         # Add *new* adjacent targets based on the *current* hit and pattern
                         self.add_adjacent_targets(current_hit, gamelogic, self.attack_pattern)


                    # --- Check for Sunk Ship ---

                elif cell_state == ' ': # --- MISS ---
                    gamelogic[rowX][colX] = 'X'
                    from main import BLUETOKEN
                    tokens_list.append(Tokens(BLUETOKEN, cell_pos, 'Miss'))
                    if sounds.get('shot'): sounds['shot'].play()
                    if sounds.get('miss'): sounds['miss'].play()

                    # If miss occurred while hunting, might help refine pattern or remove dead ends
                    # (Target was already removed from list at the start)

                    self.turn = False # End turn
                    return True, False # Attack made, turn ends
            else:
                 # No valid cell found / No target generated
                 self.turn = False
                 return False, False

        return False, self.turn # Timer delay

    def add_adjacent_targets(self, hit_coord, gamelogic, pattern=None):
        """Adds valid adjacent cells to the target list based on pattern."""
        r, c = hit_coord
        rows, cols = len(gamelogic), len(gamelogic[0])
        potential_dirs = []

        if not pattern: # No pattern yet, check all 4 directions
            potential_dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        elif 'vertical' in pattern:
             potential_dirs = [(-1, 0), (1, 0)] # Only check North/South
        elif 'horizontal' in pattern:
             potential_dirs = [(0, -1), (0, 1)] # Only check West/East

        for dr, dc in potential_dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and gamelogic[nr][nc] in [' ', 'O']:
                new_target = (nr, nc)
                if new_target not in self.target_list:
                    # Add new targets to the FRONT of the list for depth-first like search
                    self.target_list.insert(0, new_target)

    # Override draw to potentially show targeting state? (Optional)
    def draw(self, window, grid_coords):
         super().draw(window, grid_coords) # Draw basic status
import pygame
import random
from constants import CELLSIZE
from game_objects import Tokens 

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

                    from game_logic import checkAndNotifyDestroyedShip
                    checkAndNotifyDestroyedShip(grid_coords, logic_grid, enemy_fleet, message_boxes_list)

                    self.turn = True # Player gets another turn after a hit

                elif cell_state == ' ': # Miss an empty cell
                    logic_grid[row][col] = 'X' # Mark as Miss
                    # Add Miss Token (Need Green Token image)
                    from main import GREENTOKEN # Assuming loaded in main
                    tokens_list.append(Tokens(GREENTOKEN, grid_coords[row][col], 'Miss'))

                    if sounds.get('shot'): sounds['shot'].play()
                    if sounds.get('miss'): sounds['miss'].play()

                    self.turn = False # Player loses turn after a miss

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
                    from game_logic import checkAndNotifyDestroyedShip
                    checkAndNotifyDestroyedShip(grid_coords, gamelogic, enemy_fleet, message_boxes_list)

                    self.turn = True # Computer gets another turn after hit
                    return True, True # Attack made, turn continues

                elif cell_state == ' ': # Miss
                    gamelogic[rowX][colX] = 'X'
                    from main import BLUETOKEN # Loaded in main
                    tokens_list.append(Tokens(BLUETOKEN, cell_pos, 'Miss'))
                    if sounds.get('shot'): sounds['shot'].play()
                    if sounds.get('miss'): sounds['miss'].play()

                    self.turn = False 
                    return True, False 

            else:
                 self.turn = False
                 return False, False 


        return False, self.turn 

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
        self.hits = []  # các ô đã trúng nhưng tàu chưa chìm

    def score_cell(self, r, c, gamelogic, rows, cols):
        """Tính điểm Greedy cho một ô (ưu tiên gần các ô trúng)"""
        if gamelogic[r][c] not in [' ', 'O']:
            return -1  # đã đánh rồi

        score = 0

        # Tăng điểm nếu ô này gần ô đã trúng
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if gamelogic[nr][nc] == 'T':
                    score += 3  # càng gần ô trúng càng tốt
                elif gamelogic[nr][nc] in [' ', 'O']:
                    score += 1  # lân cận ô chưa đánh

        return score

    def makeAttack(self, gamelogic, grid_coords, enemy_fleet, tokens_list, message_boxes_list, sounds, current_time, last_attack_time):
        import random
        from main import REDTOKEN, BLUETOKEN, FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST
        from game_logic import checkAndNotifyDestroyedShip, get_ship_at_coord

        attack_delay = 1000
        if current_time - last_attack_time < attack_delay:
            return False, self.turn

        rows, cols = len(gamelogic), len(gamelogic[0])

        # Tính điểm cho tất cả các ô
        scored_cells = []
        for r in range(rows):
            for c in range(cols):
                score = self.score_cell(r, c, gamelogic, rows, cols)
                if score > 0:
                    scored_cells.append(((r, c), score))

        if not scored_cells:
            self.turn = False
            return False, False

        # Chọn ô có điểm cao nhất
        max_score = max(score for (_, score) in scored_cells)
        best_choices = [coord for coord, score in scored_cells if score == max_score]
        target_coord = random.choice(best_choices)

        rowX, colX = target_coord
        cell_state = gamelogic[rowX][colX]
        cell_pos = grid_coords[rowX][colX]

        if cell_state == 'O':  # Hit
            gamelogic[rowX][colX] = 'T'
            tokens_list.append(Tokens(REDTOKEN, cell_pos, 'Hit', FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST))
            if sounds.get('shot'): sounds['shot'].play()
            if sounds.get('hit'): sounds['hit'].play()
            self.hits.append((rowX, colX))

            destroyed_ship = checkAndNotifyDestroyedShip(grid_coords, gamelogic, enemy_fleet, message_boxes_list)
            if destroyed_ship:
                ship_cells = get_ship_at_coord(grid_coords, enemy_fleet, rowX, colX, gamelogic)
                if ship_cells:
                    self.hits = [(r, c) for r, c in self.hits if (r, c) not in ship_cells]

            self.turn = True
            return True, True

        elif cell_state == ' ':
            gamelogic[rowX][colX] = 'X'
            tokens_list.append(Tokens(BLUETOKEN, cell_pos, 'Miss'))
            if sounds.get('shot'): sounds['shot'].play()
            if sounds.get('miss'): sounds['miss'].play()
            self.turn = False
            return True, False

        # Không thể đánh vào ô này
        self.turn = False
        return False, False


class HardComputer(EasyComputer):
    def __init__(self):
        super().__init__()
        self.name = 'Hard Computer'
        self.target_list = [] # List of coordinates to attack (priority) [(r,c), ...]
        self.hunting_mode = False # Are we currently focused on sinking a found ship?
        self.last_hit = None # Coordinates of the most recent successful hit (r, c)
        self.attack_pattern = [] # Stores pattern (e.g., 'horizontal', 'vertical') if detected

    def makeAttack(self, gamelogic, grid_coords, enemy_fleet, tokens_list, message_boxes_list, sounds, current_time, last_attack_time):
        attack_delay = 1000 # Harder AI attacks slightly faster

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

                from game_logic import checkAndNotifyDestroyedShip, get_ship_at_coord
                destroyed_ship = checkAndNotifyDestroyedShip(grid_coords, gamelogic, enemy_fleet, message_boxes_list)

                if destroyed_ship:
                    # Ship sunk! Clear hunting state and remove its cells from target list
                    self.hunting_mode = False
                    self.last_hit = None
                    self.attack_pattern = []
                    # Find all cells of the sunk ship
                    ship_cells = get_ship_at_coord(grid_coords, enemy_fleet, rowX, colX, gamelogic, sunk_check=True)
                    if ship_cells:
                        self.target_list = [(r, c) for r, c in self.target_list if (r, c) not in ship_cells]

                    self.turn = True # Continue turn
                    return True, True # Attack made, turn continues

                elif cell_state == ' ': # --- MISS ---
                    gamelogic[rowX][colX] = 'X'
                    from main import BLUETOKEN
                    tokens_list.append(Tokens(BLUETOKEN, cell_pos, 'Miss'))
                    if sounds.get('shot'): sounds['shot'].play()
                    if sounds.get('miss'): sounds['miss'].play()

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
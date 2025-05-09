import pygame
import random
from constants import CELLSIZE
from game_objects import Tokens 

class Player:
    def __init__(self):
        self.turn = True  # Player usually starts

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

                if cell_state == 'O':  # Hit an occupied cell
                    logic_grid[row][col] = 'T'  # Mark as Target Hit
                    from main import REDTOKEN, FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST
                    tokens_list.append(Tokens(REDTOKEN, grid_coords[row][col], 'Hit', FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST))

                    if sounds.get('shot'): sounds['shot'].play()
                    if sounds.get('hit'): sounds['hit'].play()

                    from game_logic import checkAndNotifyDestroyedShip
                    checkAndNotifyDestroyedShip(grid_coords, logic_grid, enemy_fleet, message_boxes_list)

                    self.turn = True  # Player gets another turn after a hit

                elif cell_state == ' ':  # Miss an empty cell
                    logic_grid[row][col] = 'X'  # Mark as Miss
                    from main import GREENTOKEN
                    tokens_list.append(Tokens(GREENTOKEN, grid_coords[row][col], 'Miss'))

                    if sounds.get('shot'): sounds['shot'].play()
                    if sounds.get('miss'): sounds['miss'].play()

                    self.turn = False  # Player loses turn after a miss

                return True  # Attack was made (or attempted on already attacked cell)

        return False  # Click was outside the grid


class EasyComputer:
    def __init__(self):
        super().__init__()
        self.name = 'Easy Computer'
        self.status_text = "THINKING"  
        self.destroyed_ship_cells = set()  
        self.current_search_start = None 
        self.hit_cells = []  

    def computerStatus(self, status_text):
        """Generates a surface displaying the computer's status."""
        font = pygame.font.Font(None, 36)  # Use a default font
        status_surface = font.render(status_text, True, (255, 255, 255))  # White text
        return status_surface

    def update_destroyed_ship_cells(self, ship_cells):
        """Updates the set of destroyed ship cells."""
        self.destroyed_ship_cells.update(ship_cells)
        self.hit_cells = [(r, c) for r, c in self.hit_cells if (r, c) not in ship_cells]

    def score_cell(self, r, c, gamelogic, rows, cols):
        """Improved heuristic for scoring a cell."""
        if not (0 <= r < rows and 0 <= c < cols):
            return -1  # Out of bounds
        if gamelogic[r][c] not in [' ', 'O']:
            return -1 
        if (r, c) in self.destroyed_ship_cells:
            return -1  

        score = 0
        # Prioritize cells near hits ('T')
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if gamelogic[nr][nc] == 'T':
                    score += 5  # High score for proximity to hits
                elif gamelogic[nr][nc] in [' ', 'O']:
                    score += 1  # Low score for unexplored cells

        return score

    def makeAttack(self, gamelogic, grid_coords, enemy_fleet, tokens_list, message_boxes_list, sounds, current_time, last_attack_time):
        attack_delay = 1000  # Delay between attacks
        if current_time - last_attack_time < attack_delay:
            return False, self.turn  

        rows, cols = len(gamelogic), len(gamelogic[0])
        target_coord = None 

        if self.hit_cells:
            start_coord = self.hit_cells[-1]  
   
            max_climbing_steps_per_turn = 50 
            steps_taken = 0
            start_score = self.score_cell(start_coord[0], start_coord[1], gamelogic, rows, cols)

            if start_score >= 0: 
                current_score = start_score

                while True: 
                    if steps_taken >= max_climbing_steps_per_turn:
                        break 
                    r, c = current_coord 
                    neighbors = [] 
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = r + dr, c + dc
                        neighbor_score = self.score_cell(nr, nc, gamelogic, rows, cols)
                        if neighbor_score >= 0: 
                            neighbors.append(((nr, nc), neighbor_score))
                    if not neighbors:
                        break  # Dừng leo đồi
                    best_neighbor = max(neighbors, key=lambda x: x[1])
                    if best_neighbor[1] > current_score:

                        current_coord = best_neighbor[0] # Cập nhật vị trí hiện tại
                        current_score = best_neighbor[1] # Cập nhật điểm hiện tại
                        steps_taken += 1
                    else:
                        break 
                target_coord_from_climbing = current_coord
            else:
                    target_coord_from_climbing = None
                    
        if target_coord is None: 
            valid_cells_for_random = [(r, c) for r in range(rows) for c in range(cols) if gamelogic[r][c] in [' ', 'O'] and (r, c) not in self.destroyed_ship_cells]
            
            if valid_cells_for_random:
                target_coord = random.choice(valid_cells_for_random)

            else:
                self.turn = False
                return False, False  

        if target_coord is None and 'target_coord_from_climbing' in locals() and target_coord_from_climbing is not None:
                target_coord = target_coord_from_climbing

        if target_coord is None: 
                print("EasyComputer: Final target_coord is None after all attempts.") 
                self.turn = False
                return False, False
        rowX, colX = target_coord
        cell_state = gamelogic[rowX][colX] 
        cell_pos = grid_coords[rowX][colX]

        if cell_state == 'O':  # Hit
            
            gamelogic[rowX][colX] = 'T'
            from main import REDTOKEN, FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST
            tokens_list.append(Tokens(REDTOKEN, cell_pos, 'Hit', FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST))
            if sounds.get('shot'): sounds['shot'].play()
            if sounds.get('hit'): sounds['hit'].play()
            self.hit_cells.append((rowX, colX))
            from game_logic import checkAndNotifyDestroyedShip, get_ship_at_coord
            destroyed_ship = checkAndNotifyDestroyedShip(grid_coords, gamelogic, enemy_fleet, message_boxes_list)
            if destroyed_ship:
                ship_cells = get_ship_at_coord(grid_coords, enemy_fleet, rowX, colX, gamelogic)
                if ship_cells:
                    self.update_destroyed_ship_cells(ship_cells) # Removes sunk cells from hit_cells too
            self.turn = True
            return True, True

        elif cell_state == ' ':  # Miss
            gamelogic[rowX][colX] = 'X'
            from main import BLUETOKEN
            tokens_list.append(Tokens(BLUETOKEN, cell_pos, 'Miss'))
            if sounds.get('shot'): sounds['shot'].play()
            if sounds.get('miss'): sounds['miss'].play()
            self.turn = False
            return True, False
        else: 
            self.turn = False 
            return False, False 

    def draw(self, window, grid_coords):
        """Draws the computer's status on the screen."""
        if self.turn:
            status_surface = self.computerStatus(self.status_text)
            from constants import SCREENWIDTH, ROWS, CELLSIZE
            comp_grid_start_x = SCREENWIDTH - (ROWS * CELLSIZE)
            comp_grid_end_y = 50 + (ROWS * CELLSIZE)
            status_pos = (comp_grid_start_x - CELLSIZE, comp_grid_end_y + 10)
            window.blit(status_surface, status_pos)

class MediumComputer(EasyComputer):
    def __init__(self):
        super().__init__()
        self.name = 'Medium Computer'
        self.hits = [] 
        self.destroyed_ship_cells = set()  

    def score_cell(self, r, c, gamelogic, rows, cols):
        if gamelogic[r][c] not in [' ', 'O'] or (r, c) in self.destroyed_ship_cells:
            return -1  

        score = 0

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if gamelogic[nr][nc] == 'T':
                    score += 3
                elif gamelogic[nr][nc] in [' ', 'O']:
                    score += 1

        return score

    def makeAttack(self, gamelogic, grid_coords, enemy_fleet, tokens_list, message_boxes_list, sounds, current_time, last_attack_time):
        attack_delay = 1000
        if current_time - last_attack_time < attack_delay:
            return False, self.turn

        rows, cols = len(gamelogic), len(gamelogic[0])

        scored_cells = []
        for r in range(rows):
            for c in range(cols):
                score = self.score_cell(r, c, gamelogic, rows, cols)
                if score > 0:
                    scored_cells.append(((r, c), score))

        if not scored_cells:
            self.turn = False
            return False, False

        max_score = max(score for (_, score) in scored_cells)
        best_choices = [coord for coord, score in scored_cells if score == max_score]
        target_coord = random.choice(best_choices)

        rowX, colX = target_coord
        cell_state = gamelogic[rowX][colX]
        cell_pos = grid_coords[rowX][colX]

        if cell_state == 'O':  # Hit
            gamelogic[rowX][colX] = 'T'
            from main import REDTOKEN, FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST
            tokens_list.append(Tokens(REDTOKEN, cell_pos, 'Hit', FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST))
            if sounds.get('shot'): sounds['shot'].play()
            if sounds.get('hit'): sounds['hit'].play()
            self.hits.append((rowX, colX))

            from game_logic import checkAndNotifyDestroyedShip, get_ship_at_coord
            destroyed_ship = checkAndNotifyDestroyedShip(grid_coords, gamelogic, enemy_fleet, message_boxes_list)
            if destroyed_ship:
                ship_cells = get_ship_at_coord(grid_coords, enemy_fleet, rowX, colX, gamelogic)
                if ship_cells:
                    self.update_destroyed_ship_cells(ship_cells)
                    self.hits = [(r, c) for r, c in self.hits if (r, c) not in ship_cells]

            self.turn = True
            return True, True

        elif cell_state == ' ':
            gamelogic[rowX][colX] = 'X'
            from main import BLUETOKEN
            tokens_list.append(Tokens(BLUETOKEN, cell_pos, 'Miss'))
            if sounds.get('shot'): sounds['shot'].play()
            if sounds.get('miss'): sounds['miss'].play()
            self.turn = False
            return True, False

        self.turn = False
        return False, False



class HardComputer(EasyComputer):
    def __init__(self):
        super().__init__()
        self.name = 'Hard Computer'
        self.moves = []

    def generateMoves(self, coords, gamelogic, rows, cols):
        r_start, c_start = coords
        self.moves.clear()
        queue = [(r_start, c_start)]
        visited = {(r_start, c_start)}

        while queue:
            curr_r, curr_c = queue.pop(0)
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = curr_r + dr, curr_c + dc
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    if gamelogic[nr][nc] == 'O':
                        self.moves.append((nr, nc))
                        queue.append((nr, nc))
                    elif gamelogic[nr][nc] == 'T':
                        queue.append((nr, nc))

    def makeAttack(self, gamelogic, grid_coords, enemy_fleet, tokens_list, message_boxes_list, sounds, current_time, last_attack_time):
        attack_delay_hunt = 1000
        attack_delay_target = 500

        current_attack_delay = attack_delay_target if self.moves else attack_delay_hunt
        if current_time - last_attack_time < current_attack_delay:
            return False, self.turn

        rows = len(gamelogic)
        cols = len(gamelogic[0])
        target_coord = None

        if self.moves:
            self.moves = [(r, c) for r, c in self.moves if gamelogic[r][c] in [' ', 'O']]
            if self.moves:
                target_coord = self.moves.pop(0)

        if not target_coord:
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

            if not validChoice:
                self.turn = False
                return False, False

        rowX, colX = target_coord
        cell_state = gamelogic[rowX][colX]
        cell_pos = grid_coords[rowX][colX]

        if cell_state == 'O':
            gamelogic[rowX][colX] = 'T'
            from main import REDTOKEN, FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST
            tokens_list.append(Tokens(REDTOKEN, cell_pos, 'Hit', FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST))
            if sounds.get('shot'): sounds['shot'].play()
            if sounds.get('hit'): sounds['hit'].play()

            self.generateMoves(target_coord, gamelogic, rows, cols)

            from game_logic import checkAndNotifyDestroyedShip
            destroyed_ship = checkAndNotifyDestroyedShip(grid_coords, gamelogic, enemy_fleet, message_boxes_list)

            self.turn = True
            return True, True

        elif cell_state == ' ':
            gamelogic[rowX][colX] = 'X'
            from main import BLUETOKEN
            tokens_list.append(Tokens(BLUETOKEN, cell_pos, 'Miss'))
            if sounds.get('shot'): sounds['shot'].play()
            if sounds.get('miss'): sounds['miss'].play()

            self.turn = False
            return True, False

        else:
            self.turn = False
            return False, False
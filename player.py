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
        self.turn = False
        self.status_font = pygame.font.SysFont('Stencil', 22)
        self.status_text = 'Thinking'
        self.name = 'Easy Computer'
        self.destroyed_ship_cells = set() 

    def computerStatus(self, msg):
        message = self.status_font.render(msg, 1, (0, 0, 0))
        return message

    def update_destroyed_ship_cells(self, destroyed_ship_cells):
        self.destroyed_ship_cells.update(destroyed_ship_cells)

    def makeAttack(self, gamelogic, grid_coords, enemy_fleet, tokens_list, message_boxes_list, sounds, current_time, last_attack_time):
        attack_delay = 1000

        if current_time - last_attack_time >= attack_delay:
            rows = len(gamelogic)
            cols = len(gamelogic[0])
            validChoice = False
            attempts = 0
            max_attempts = rows * cols * 2

            while not validChoice and attempts < max_attempts:
                rowX = random.randint(0, rows - 1)
                colX = random.randint(0, cols - 1)
                if gamelogic[rowX][colX] in [' ', 'O'] and (rowX, colX) not in self.destroyed_ship_cells:
                    validChoice = True
                attempts += 1

            if validChoice:
                cell_state = gamelogic[rowX][colX]
                cell_pos = grid_coords[rowX][colX]

                if cell_state == 'O':  # Hit
                    gamelogic[rowX][colX] = 'T'
                    from main import REDTOKEN, FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST
                    tokens_list.append(Tokens(REDTOKEN, cell_pos, 'Hit', FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST))
                    if sounds.get('shot'): sounds['shot'].play()
                    if sounds.get('hit'): sounds['hit'].play()
                    from game_logic import checkAndNotifyDestroyedShip, get_ship_at_coord
                    destroyed_ship = checkAndNotifyDestroyedShip(grid_coords, gamelogic, enemy_fleet, message_boxes_list)

                    if destroyed_ship:
                        ship_cells = get_ship_at_coord(grid_coords, enemy_fleet, rowX, colX, gamelogic)
                        if ship_cells:
                            self.update_destroyed_ship_cells(ship_cells)

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

        return False, self.turn

    def draw(self, window, grid_coords):
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
        self.target_list = []
        self.hunting_mode = False
        self.last_hit_coords = None
        self.initial_hit_coords = None
        self.determined_pattern = None

    def makeAttack(self, gamelogic, grid_coords, enemy_fleet, tokens_list, message_boxes_list, sounds, current_time, last_attack_time):
        attack_delay = 800

        if current_time - last_attack_time < attack_delay:
            return False, self.turn

        rows = len(gamelogic)
        cols = len(gamelogic[0])
        target_coord = None

        self.target_list = [
            (r, c) for r, c in self.target_list
            if 0 <= r < rows and 0 <= c < cols and gamelogic[r][c] in [' ', 'O']
        ]

        if self.target_list:
            target_coord = self.target_list.pop(0)
            self.hunting_mode = True

        if not target_coord:
            self.hunting_mode = False
            self.last_hit_coords = None
            self.initial_hit_coords = None
            self.determined_pattern = None

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

            current_hit = (rowX, colX)

            if not self.hunting_mode:
                self.hunting_mode = True
                self.initial_hit_coords = current_hit
                self.last_hit_coords = current_hit
                self.determined_pattern = None
                self.add_potential_targets(current_hit, gamelogic, mode='adjacent')
            else:
                if self.determined_pattern is None and self.initial_hit_coords:
                    if current_hit[0] == self.initial_hit_coords[0]:
                        self.determined_pattern = 'horizontal'
                    elif current_hit[1] == self.initial_hit_coords[1]:
                        self.determined_pattern = 'vertical'

                self.last_hit_coords = current_hit

                if self.determined_pattern:
                    self.add_potential_targets(current_hit, gamelogic, mode=self.determined_pattern, initial_hit=self.initial_hit_coords)
                else:
                     self.add_potential_targets(current_hit, gamelogic, mode='adjacent')

            from game_logic import checkAndNotifyDestroyedShip, get_ship_at_coord
            destroyed_ship = checkAndNotifyDestroyedShip(grid_coords, gamelogic, enemy_fleet, message_boxes_list)

            if destroyed_ship:
                self.hunting_mode = False
                self.last_hit_coords = None
                self.initial_hit_coords = None
                self.determined_pattern = None
                self.target_list.clear()

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


    def add_potential_targets(self, hit_coord, gamelogic, mode='adjacent', initial_hit=None):
        r, c = hit_coord
        rows, cols = len(gamelogic), len(gamelogic[0])
        new_targets_to_add = []

        if mode == 'adjacent':
            potential_dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dr, dc in potential_dirs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and gamelogic[nr][nc] in [' ', 'O']:
                    new_target = (nr, nc)
                    if new_target not in self.target_list and new_target not in new_targets_to_add:
                        new_targets_to_add.append(new_target)

        elif mode == 'horizontal' and initial_hit:
            all_hits_on_row = sorted([h for h in self.get_all_current_hits(gamelogic) if h[0] == r])

            if all_hits_on_row:
                min_c = all_hits_on_row[0][1]
                max_c = all_hits_on_row[-1][1]

                nl, nc = r, min_c - 1
                if 0 <= nc < cols and gamelogic[nl][nc] in [' ', 'O']:
                    new_target = (nl, nc)
                    if new_target not in self.target_list and new_target not in new_targets_to_add:
                        new_targets_to_add.append(new_target)

                nr, nc = r, max_c + 1
                if 0 <= nc < cols and gamelogic[nr][nc] in [' ', 'O']:
                    new_target = (nr, nc)
                    if new_target not in self.target_list and new_target not in new_targets_to_add:
                        new_targets_to_add.append(new_target)

        elif mode == 'vertical' and initial_hit:
            all_hits_on_col = sorted([h for h in self.get_all_current_hits(gamelogic) if h[1] == c])

            if all_hits_on_col:
                min_r = all_hits_on_col[0][0]
                max_r = all_hits_on_col[-1][0]

                nr, nc = min_r - 1, c
                if 0 <= nr < rows and gamelogic[nr][nc] in [' ', 'O']:
                    new_target = (nr, nc)
                    if new_target not in self.target_list and new_target not in new_targets_to_add:
                        new_targets_to_add.append(new_target)

                nr, nc = max_r + 1, c
                if 0 <= nr < rows and gamelogic[nr][nc] in [' ', 'O']:
                    new_target = (nr, nc)
                    if new_target not in self.target_list and new_target not in new_targets_to_add:
                        new_targets_to_add.append(new_target)

        for target in reversed(new_targets_to_add):
            self.target_list.insert(0, target)

    def get_all_current_hits(self, gamelogic):
        hits = []
        rows, cols = len(gamelogic), len(gamelogic[0])
        for r in range(rows):
            for c in range(cols):
                if gamelogic[r][c] == 'T':
                    hits.append((r, c))
        return hits
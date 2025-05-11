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
        self.hit_cells = []

    def computerStatus(self, status_text):
        font = pygame.font.Font(None, 36)
        return font.render(status_text, True, (255, 255, 255))

    def update_destroyed_ship_cells(self, ship_cells):
        self.destroyed_ship_cells.update(ship_cells)
        self.hit_cells = [(r, c) for r, c in self.hit_cells if (r, c) not in ship_cells]

    def score_cell(self, r, c, gamelogic, rows, cols):
        if not (0 <= r < rows and 0 <= c < cols):
            return -1
        if gamelogic[r][c] not in [' ', 'O'] or (r, c) in self.destroyed_ship_cells:
            return -1

        score = 0
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if gamelogic[nr][nc] == 'T':
                    score += 5
                elif gamelogic[nr][nc] in [' ', 'O']:
                    score += 1
        return score

    def makeAttack(self, gamelogic, grid_coords, enemy_fleet, tokens_list, message_boxes_list, sounds, current_time, last_attack_time):
        attack_delay = 1000
        if current_time - last_attack_time < attack_delay:
            return False, self.turn

        rows, cols = len(gamelogic), len(gamelogic[0])
        target_coord = None

        # Stochastic Hill Climbing
        valid_starts = [(r, c) for r in range(rows) for c in range(cols) if gamelogic[r][c] in [' ', 'O']]
        if valid_starts:
            import random
            current = random.choice(valid_starts)
            current_score = self.score_cell(current[0], current[1], gamelogic, rows, cols)
            max_steps = 30
            for _ in range(max_steps):
                neighbors = []
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = current[0] + dr, current[1] + dc
                    score = self.score_cell(nr, nc, gamelogic, rows, cols)
                    if score > current_score:
                        neighbors.append(((nr, nc), score))
                if not neighbors:
                    break
                current, current_score = random.choice(neighbors)
            target_coord = current

        if target_coord is None:
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
            self.hit_cells.append((rowX, colX))
            from game_logic import checkAndNotifyDestroyedShip, get_ship_at_coord
            destroyed_ship = checkAndNotifyDestroyedShip(grid_coords, gamelogic, enemy_fleet, message_boxes_list)
            if destroyed_ship:
                ship_cells = get_ship_at_coord(grid_coords, enemy_fleet, rowX, colX, gamelogic)
                if ship_cells:
                    self.update_destroyed_ship_cells(ship_cells)
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
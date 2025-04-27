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



class HardComputer(EasyComputer): # Kế thừa từ EasyComputer
    def __init__(self):
        super().__init__()
        self.name = 'Hard Computer'
        self.moves = []
        self.target_list = [] 
        self.hunting_mode = False
        self.last_hit_coords = None
        self.initial_hit_coords = None
        self.determined_pattern = None

    def generateMoves(self, coords, gamelogic, rows, cols):
        r_start, c_start = coords
        
        stack = [(r_start, c_start)]
        visited = {(r_start, c_start)} 

        self.moves.clear() 
        
        potential_targets = []
        queue = [(r_start, c_start)] # Bắt đầu tìm kiếm từ điểm trúng ban đầu (T)
        visited_search = {(r_start, c_start)} # Theo dõi các ô đã dùng để tìm kiếm lân cận

        while queue:
            curr_r, curr_c = queue.pop(0) # Lấy điểm hiện tại (có thể là 'T' hoặc 'O' đã được tìm thấy)

            # Kiểm tra 4 hướng từ điểm hiện tại
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = curr_r + dr, curr_c + dc

                # Kiểm tra nếu ô lân cận nằm trong biên và chưa được thăm trong quá trình tìm kiếm này
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited_search:
                     visited_search.add((nr, nc)) # Đánh dấu đã thăm

                     # Nếu ô lân cận là 'O' (chưa bắn nhưng có tàu)
                     if gamelogic[nr][nc] == 'O':
                          # Thêm ô 'O' này vào danh sách moves cần bắn
                          if (nr, nc) not in self.moves: # Kiểm tra trùng lặp
                              self.moves.append((nr, nc))
                              # Thêm ô 'O' này vào queue để tìm kiếm các ô 'O' lân cận của nó (mở rộng vùng tìm kiếm trên tàu)
                              queue.append((nr, nc))
                     # Nếu ô lân cận là 'T' (điểm trúng khác của cùng tàu)
                     elif gamelogic[nr][nc] == 'T':
                          # Thêm ô 'T' này vào queue để tìm kiếm các ô 'O' lân cận của nó
                          queue.append((nr, nc))
                     # Nếu là ' ' hoặc 'X', dừng theo hướng này

    def makeAttack(self, gamelogic, grid_coords, enemy_fleet, tokens_list, message_boxes_list, sounds, current_time, last_attack_time):
        
        attack_delay_hunt = 1000 # Độ trễ khi săn lùng (chưa có moves)
        attack_delay_target = 500 # Độ trễ khi xả đạn vào moves đã có

        current_attack_delay = attack_delay_target if self.moves else attack_delay_hunt
        if current_time - last_attack_time < current_attack_delay:
            return False, self.turn # Chưa đủ thời gian chờ

        rows = len(gamelogic)
        cols = len(gamelogic[0])
        target_coord = None # Tọa độ mục tiêu cuối cùng AI sẽ bắn (row, col)

        if self.moves:
            self.moves = [(r, c) for r, c in self.moves if 0 <= r < rows and 0 <= c < cols and gamelogic[r][c] in [' ', 'O']]

            if self.moves:
                # Lấy mục tiêu đầu tiên trong danh sách moves
                target_coord = self.moves.pop(0)

        if not target_coord:
            validChoice = False
            attempts = 0
            max_attempts = rows * cols * 2 # Failsafe limit
            while not validChoice and attempts < max_attempts:
                rowX = random.randint(0, rows - 1)
                colX = random.randint(0, cols - 1)
                if gamelogic[rowX][colX] in [' ', 'O']: # Chỉ bắn vào ô chưa bị bắn
                    validChoice = True
                    target_coord = (rowX, colX)
                attempts += 1

            if not validChoice:
                 # print("Expert AI: Random search failed - No target selected.") # Debugging
                 self.turn = False
                 return False, False # Không tấn công được, kết thúc lượt
            
        rowX, colX = target_coord
        cell_state = gamelogic[rowX][colX] # Lấy trạng thái hiện tại của ô
        cell_pos = grid_coords[rowX][colX] # Lấy vị trí hình ảnh của ô

        if cell_state == 'O': # Trúng tàu! (Hit) - Bao gồm cả khi bắn từ moves list
            # print(f"Expert AI: HIT at ({rowX},{colX})!") # Debugging
            gamelogic[rowX][colX] = 'T' # Cập nhật trạng thái ô trên lưới logic
            # Tạo hiệu ứng và phát âm thanh trúng (sử dụng tham số)
            from main import REDTOKEN, FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST # Ensure imports are correct
            tokens_list.append(Tokens(REDTOKEN, cell_pos, 'Hit', FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST))
            if sounds.get('shot'): sounds['shot'].play()
            if sounds.get('hit'): sounds['hit'].play()

            self.generateMoves(target_coord, gamelogic, rows, cols)

            # Kiểm tra tàu chìm sau khi xử lý hit
            from game_logic import checkAndNotifyDestroyedShip, get_ship_at_coord # Ensure import is correct
            destroyed_ship = checkAndNotifyDestroyedShip(grid_coords, gamelogic, enemy_fleet, message_boxes_list)

            if destroyed_ship:
                # Ship sunk! Reset hunting state related to *this* ship.
                self.hunting_mode = False
                self.last_hit_coords = None
                self.initial_hit_coords = None
                self.determined_pattern = None

                sunk_ship_cells = []
               
                all_cells_of_sunk_ship = get_ship_at_coord(grid_coords, enemy_fleet, rowX, colX, gamelogic) # get_ship_at_coord trả về cells của ship tại (r,c) dựa trên rect

                if all_cells_of_sunk_ship:

                    self.target_list = [(r, c) for r, c in self.target_list if (r, c) not in all_cells_of_sunk_ship]

            self.turn = True # Continue turn
            return True, True # Attack made, turn continues

        elif cell_state == ' ': # Bắn trượt! (Miss)
            gamelogic[rowX][colX] = 'X' # Cập nhật trạng thái ô trên lưới logic
            # Tạo hiệu ứng và phát âm thanh trượt (sử dụng tham số)
            from main import BLUETOKEN # Ensure import is correct
            tokens_list.append(Tokens(BLUETOKEN, cell_pos, 'Miss'))
            if sounds.get('shot'): sounds['shot'].play()
            if sounds.get('miss'): sounds['miss'].play()

            self.turn = False
            return True, False # Đã tấn công, lượt kết thúc

        else: 
             self.turn = False # Kết thúc lượt (failsafe)
             return False, False # Không tấn công được, kết thúc lượt (failsafe)

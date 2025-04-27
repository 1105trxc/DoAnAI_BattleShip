import pygame


# Import Modules and specific names needed
import constants as C
import utils
# Import classes/functions directly for original calling style
from game_objects import Ship, MessageBox, Button
from player import Player, EasyComputer, MediumComputer, HardComputer
from board import createGameGrid # Chỉ cần createGameGrid từ board
from game_logic import (
    createGameLogic, updateGameLogic, printGameLogic, sortFleet,
    randomizeShipPositions, resetShips, areShipsPlacedCorrectly,
    deploymentPhase, takeTurns, checkForWinners, get_ship_at_coord # Thêm get_ship_at_coord nếu cần
)
from screens import updateGameScreen

# --- Pygame Initialization ---
pygame.init()
pygame.mixer.init()
pygame.font.init()

# --- Screen Setup ---
GAMESCREEN = pygame.display.set_mode((C.SCREENWIDTH, C.SCREENHEIGHT))
pygame.display.set_caption('Battle Ship')
clock = pygame.time.Clock()

# --- Load Assets ---
MAINMENUIMAGE = utils.loadImage(C.MAINMENUIMAGE_PATH, (C.SCREENWIDTH, C.SCREENHEIGHT), alpha=False)
ENDSCREENIMAGE = utils.loadImage(C.ENDSCREENIMAGE_PATH, (C.SCREENWIDTH, C.SCREENHEIGHT), alpha=False)
BACKGROUND = utils.loadImage(C.BACKGROUND_PATH, (C.SCREENWIDTH, C.SCREENHEIGHT), alpha=False)
PGAMEGRIDIMG = utils.loadImage(C.PGAMEGRIDIMG_PATH, ((C.ROWS + 1) * C.CELLSIZE, (C.COLS + 1) * C.CELLSIZE))
CGAMEGRIDIMG = utils.loadImage(C.CGAMEGRIDIMG_PATH, ((C.ROWS + 1) * C.CELLSIZE, (C.COLS + 1) * C.CELLSIZE))
BUTTONIMAGE = utils.loadImage(C.BUTTONIMAGE_PATH, (150, 50))
BUTTONIMAGE1 = utils.loadImage(C.BUTTONIMAGE_PATH, (250, 100)) # Assuming path reuse ok
BUTTONIMAGE_LG = pygame.transform.scale(BUTTONIMAGE, (150 + 10, 50 + 10))
BUTTONIMAGE1_LG = pygame.transform.scale(BUTTONIMAGE1, (250 + 10, 100 + 10))
REDTOKEN = utils.loadImage(C.REDTOKEN_PATH, (C.CELLSIZE, C.CELLSIZE))
GREENTOKEN = utils.loadImage(C.GREENTOKEN_PATH, (C.CELLSIZE, C.CELLSIZE))
BLUETOKEN = utils.loadImage(C.BLUETOKEN_PATH, (C.CELLSIZE, C.CELLSIZE))
RADARGRID = utils.loadImage(C.RADARGRID_PATH, (C.ROWS * C.CELLSIZE, C.COLS * C.CELLSIZE))
# Animations
FIRETOKENIMAGELIST = utils.loadAnimationImages(C.FIRETOKEN_ANIM_PATH, 13, (C.CELLSIZE, C.CELLSIZE))
try:
    EXPLOSIONSPRITESHEET = pygame.image.load(C.EXPLOSIONSPRITESHEET_PATH).convert_alpha()
    EXPLOSIONIMAGELIST = []
    sheet_rows, sheet_cols = 8, 8; sprite_width, sprite_height = 128, 128
    for row in range(sheet_rows):
        for col in range(sheet_cols):
            EXPLOSIONIMAGELIST.append(utils.loadSpriteSheetImages(EXPLOSIONSPRITESHEET, col, row, (C.CELLSIZE, C.CELLSIZE), (sprite_width, sprite_height)))
except pygame.error as e: print(f"Error loading explosion spritesheet: {e}"); EXPLOSIONIMAGELIST = []
# Sounds
HITSOUND = utils.loadSound(C.HITSOUND_PATH, 0.05)
SHOTSOUND = utils.loadSound(C.SHOTSOUND_PATH, 0.05)
MISSSOUND = utils.loadSound(C.MISSSOUND_PATH, 0.05)
SOUNDS = {'hit': HITSOUND, 'shot': SHOTSOUND, 'miss': MISSSOUND}

# --- Game Object Initialization ---
# Grids
pGameGridCoords = createGameGrid(C.ROWS, C.COLS, C.CELLSIZE, (50, 50))
pGameLogic = createGameLogic(C.ROWS, C.COLS)
cGameGridCoords = createGameGrid(C.ROWS, C.COLS, C.CELLSIZE, (C.SCREENWIDTH - (C.COLS * C.CELLSIZE) - 50, 50)) # Adjusted X
cGameLogic = createGameLogic(C.ROWS, C.COLS)

# Fleets
def createFleet(fleet_config, ship_class): # Helper stays same
    fleet = []
    for name, config in fleet_config.items():
        fleet.append(ship_class(name, config[1], config[2], config[3], config[4], config[5], config[6], config[7]))
    return fleet
pFleet = createFleet(C.FLEET, Ship)
cFleet = createFleet(C.FLEET, Ship)
randomizeShipPositions(cFleet, cGameGridCoords)
resetShips(cFleet, reset_position=False) # Use modified resetShips

# Players
player1 = Player()
computer = EasyComputer()

# Buttons
BUTTONS = [
    Button(BUTTONIMAGE, (150, 50), (25, 900), 'Randomize', BUTTONIMAGE_LG),
    Button(BUTTONIMAGE, (150, 50), (200, 900), 'Reset', BUTTONIMAGE_LG),
    Button(BUTTONIMAGE, (150, 50), (375, 900), 'Deploy', BUTTONIMAGE_LG),
    Button(BUTTONIMAGE, (150, 50), (550, 900), 'Back to Main', BUTTONIMAGE_LG),  # Nút sẽ đổi thành "Quit" ở trạng thái GAME_OVER
    Button(BUTTONIMAGE1, (250, 100), (C.SCREENWIDTH - 300, C.SCREENHEIGHT // 2 - 150), 'Easy Computer', BUTTONIMAGE1_LG),
    Button(BUTTONIMAGE1, (250, 100), (C.SCREENWIDTH - 300, C.SCREENHEIGHT // 2), 'Medium Computer', BUTTONIMAGE1_LG),
    Button(BUTTONIMAGE1, (250, 100), (C.SCREENWIDTH - 300, C.SCREENHEIGHT // 2 + 150), 'Hard Computer', BUTTONIMAGE1_LG),
]

# Game State Variables
GAMESTATE = C.MAIN_MENU
DEPLOYMENT = True
lastComputerAttackTime = 0
gameOverMessageShown = False
winnerMessage = None
TOKENS = []
MESSAGE_BOXES = []
active_ship = None
STAGES = C.STAGE
ROWS = C.ROWS
COLS = C.COLS

# --- Helper Function for Resetting Game ---
def reset_game_for_new_round():
    global pFleet, cFleet, pGameLogic, cGameLogic, player1, computer, TOKENS, MESSAGE_BOXES
    global DEPLOYMENT, GAMESTATE, gameOverMessageShown, winnerMessage, active_ship, lastComputerAttackTime

    TOKENS.clear()
    MESSAGE_BOXES.clear()

    resetShips(pFleet, reset_position=True)
    randomizeShipPositions(cFleet, cGameGridCoords)
    resetShips(cFleet, reset_position=False)

    pGameLogic = createGameLogic(ROWS, COLS)
    cGameLogic = createGameLogic(ROWS, COLS)
    updateGameLogic(pGameGridCoords, pFleet, pGameLogic)
    updateGameLogic(cGameGridCoords, cFleet, cGameLogic)

    player1.turn = True
    computer.turn = False

    DEPLOYMENT = True
    GAMESTATE = C.DEPLOYMENT_STATE
    gameOverMessageShown = False
    winnerMessage = None
    active_ship = None
    lastComputerAttackTime = pygame.time.get_ticks()

# --- Main Game Loop ---
RUNGAME = True
previous_game_state = None  # Biến để theo dõi trạng thái trước đó

while RUNGAME:
    currentTime = pygame.time.get_ticks()

    # --- Cập nhật trạng thái active của các nút dựa trên GAMESTATE ---
    for button in BUTTONS:
        # Đặt active dựa trên trạng thái game
        if button.name == 'Randomize' or button.name == 'Reset' or button.name == 'Deploy':
            button.active = (GAMESTATE == C.DEPLOYMENT_STATE and DEPLOYMENT)  # Chỉ hiển thị trong Deployment
        elif button.name in ['Easy Computer', 'Medium Computer', 'Hard Computer']:
            button.active = (GAMESTATE == C.MAIN_MENU or GAMESTATE == C.GAME_OVER)  # Hiển thị ở Main Menu và Game Over
        elif button.name in ['Back to Main', 'Quit']:
            button.active = (GAMESTATE in [C.DEPLOYMENT_STATE, C.GAME_OVER])  # Hiển thị ở Deployment, Attack, và Game Over

        # Đổi tên nút "Back to Main" thành "Quit" trong trạng thái GAME_OVER
        if button.name in ['Back to Main', 'Quit']:
            if GAMESTATE == C.GAME_OVER:
                button.name = 'Quit'
            else:
                button.name = 'Back to Main'

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUNGAME = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if event.button == 1:  # Left Click
                # --- Handle Ship Drag / Attack ---
                if DEPLOYMENT == True:
                    clicked_on_ship = False
                    for ship in reversed(pFleet):
                        if ship.rect.collidepoint(mouse_pos):
                            ship.active = True
                            active_ship = ship
                            sortFleet(ship, pFleet)
                            clicked_on_ship = True
                            break
                else:
                    if player1.turn == True:
                        is_button_click = False
                        for button in BUTTONS:
                            if button.active and button.rect.collidepoint(mouse_pos):
                                is_button_click = True
                                break
                        if not is_button_click:
                            attack_successful = player1.makeAttack(
                                cGameGridCoords, cGameLogic, cFleet, TOKENS, MESSAGE_BOXES, SOUNDS
                            )
                            if attack_successful and not player1.turn:
                                computer.turn = True
                                lastComputerAttackTime = currentTime

                # --- Handle Buttons ---
                button_action_handled_this_click = False
                for button in BUTTONS:
                    if button.active and button.rect.collidepoint(mouse_pos) and not button_action_handled_this_click:
                        action = button.name
                        if not DEPLOYMENT and action == 'Randomize': 
                            action = 'Quit'
                        elif DEPLOYMENT and action == 'Quit': 
                            action = 'Randomize'

                        print(f"Button Clicked: {action}")

                        # --- Handle Specific Button Actions ---
                        if action == 'Deploy':
                            if areShipsPlacedCorrectly(pFleet, pGameGridCoords):
                                status = deploymentPhase(DEPLOYMENT)
                                DEPLOYMENT = status
                                player1.turn = True
                                computer.turn = False
                                lastComputerAttackTime = currentTime
                                updateGameLogic(pGameGridCoords, pFleet, pGameLogic)
                                updateGameLogic(cGameGridCoords, cFleet, cGameLogic)
                                print("--- Deployment Complete ---")
                                printGameLogic(pGameLogic, cGameLogic)
                                button_action_handled_this_click = True
                            else:
                                button_action_handled_this_click = True

                        elif action == 'Redeploy':
                            print("Handling Redeploy (Resetting Game)...")
                            reset_game_for_new_round()
                            button_action_handled_this_click = True

                        elif action == 'Quit' and GAMESTATE != C.GAME_OVER:  # "Quit" khi không ở trạng thái GAME_OVER
                            print("Handling Quit...")
                            RUNGAME = False
                            button_action_handled_this_click = True

                        elif action == 'Quit' and GAMESTATE == C.GAME_OVER:  # "Quit" ở trạng thái GAME_OVER
                            print("Handling Quit in Game Over...")
                            RUNGAME = False  # Thoát game hoàn toàn
                            button_action_handled_this_click = True

                        elif action in ['Easy Computer', 'Medium Computer', 'Hard Computer']:
                            if GAMESTATE == C.MAIN_MENU or GAMESTATE == C.GAME_OVER:
                                if action == 'Easy Computer': computer = EasyComputer()
                                elif action == 'Medium Computer': computer = MediumComputer()
                                elif action == 'Hard Computer': computer = HardComputer()
                                print(f"Selected AI: {computer.name}")
                                reset_game_for_new_round()
                                button_action_handled_this_click = True

                        if not button_action_handled_this_click:
                            print(f"Calling actionOnPress for: {action}")
                            if action == 'Randomize':
                                if DEPLOYMENT:
                                    randomizeShipPositions(pFleet, pGameGridCoords)
                                    updateGameLogic(pGameGridCoords, pFleet, pGameLogic)
                                    button_action_handled_this_click = True
                            elif action == 'Reset':
                                if DEPLOYMENT:
                                    resetShips(pFleet, reset_position=True)
                                    updateGameLogic(pGameGridCoords, pFleet, pGameLogic)
                                    button_action_handled_this_click = True
                            elif action == 'Back to Main':
                                if GAMESTATE != C.GAME_OVER:  # Chỉ hoạt động khi không ở trạng thái GAME_OVER
                                    GAMESTATE = C.MAIN_MENU
                                    DEPLOYMENT = True
                                    reset_game_for_new_round()
                                    GAMESTATE = C.MAIN_MENU
                                    button_action_handled_this_click = True

                        if button_action_handled_this_click:
                            break

            elif event.button == 2:
                printGameLogic(pGameLogic, cGameLogic)

            elif event.button == 3:
                if DEPLOYMENT == True:
                    for ship in pFleet:
                        if ship.rect.collidepoint(mouse_pos):
                            if not ship.checkForRotateCollisions([s for s in pFleet if s is not ship]):
                                ship.rotateShip(True)
                            else:
                                MESSAGE_BOXES.append(MessageBox("Cannot rotate: Collision!", duration=1500))
                            break

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and DEPLOYMENT == True:
                if active_ship:
                    collision = active_ship.checkForCollisions([s for s in pFleet if s is not active_ship])
                    if not collision:
                        active_ship.snapToGrid(pGameGridCoords)
                        active_ship.active = False
                        updateGameLogic(pGameGridCoords, pFleet, pGameLogic)
                    else:
                        active_ship.active = False
                        MESSAGE_BOXES.append(MessageBox("Ships cannot overlap!", duration=2000))
                        active_ship.returnToDefaultPosition()
                    active_ship = None

    # --- Game Logic Updates ---
    if DEPLOYMENT == True:
        if active_ship and active_ship.active:
            active_ship.selectShipAndMove()
            active_ship.snapToGridEdge(pGameGridCoords)

    # --- Drawing ---
    assets_dict = {
        'backgrounds': {'main_menu': MAINMENUIMAGE, 'game': BACKGROUND, 'end_screen': ENDSCREENIMAGE},
        'grid_images': {'player': PGAMEGRIDIMG, 'computer': CGAMEGRIDIMG, 'radar': RADARGRID},
        'buttons': BUTTONS,
        'sounds': SOUNDS,
        'tokens': {'red': REDTOKEN, 'green': GREENTOKEN, 'blue': BLUETOKEN}
    }
    game_data_dict = {
        'pFleet': pFleet, 'cFleet': cFleet,
        'pGameGridCoords': pGameGridCoords, 'cGameGridCoords': cGameGridCoords,
        'pGameLogic': pGameLogic, 'cGameLogic': cGameLogic,
        'player1': player1, 'computer': computer,
        'tokens_list': TOKENS, 'message_boxes_list': MESSAGE_BOXES,
        'deployment_status': DEPLOYMENT, 'winner_message': winnerMessage
    }
    updateGameScreen(GAMESCREEN, GAMESTATE, assets_dict, game_data_dict)

    # --- Attack Phase Turn Logic & AI ---
    if not DEPLOYMENT and GAMESTATE == C.DEPLOYMENT_STATE:
        player1Wins = checkForWinners(cGameLogic)
        computerWins = checkForWinners(pGameLogic)

        if player1Wins or computerWins:
            GAMESTATE = C.GAME_OVER
            if player1Wins:
                winnerMessage = "PLAYER 1 WINS!"
            else:
                winnerMessage = f"{computer.name.upper()} WINS!"
            if not gameOverMessageShown:
                MESSAGE_BOXES.append(MessageBox(winnerMessage, duration=4000))
                gameOverMessageShown = True
        else:
            if computer.turn:
                lastComputerAttackTime = takeTurns(
                    player1, computer,
                    pGameLogic, pGameGridCoords, pFleet,
                    cGameLogic, cGameGridCoords, cFleet,
                    TOKENS, MESSAGE_BOXES, SOUNDS,
                    currentTime, lastComputerAttackTime
                )

    # --- Frame Rate Control ---
    clock.tick(60)

# --- Quit Pygame ---
pygame.quit()
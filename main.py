import pygame
import random
import time

# Import Modules and specific names needed
import constants as C
import utils
# Import classes/functions directly for original calling style
from game_objects import Ship, Guns, Tokens, MessageBox, Button
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
    Button(BUTTONIMAGE, (150, 50), (550, 900), 'Back to Main', BUTTONIMAGE_LG),
    Button(BUTTONIMAGE1, (250, 100), (C.SCREENWIDTH - 300, C.SCREENHEIGHT // 2 - 150), 'Easy Computer', BUTTONIMAGE1_LG),
    Button(BUTTONIMAGE1, (250, 100), (C.SCREENWIDTH - 300, C.SCREENHEIGHT // 2), 'Medium Computer', BUTTONIMAGE1_LG),
    Button(BUTTONIMAGE1, (250, 100), (C.SCREENWIDTH - 300, C.SCREENHEIGHT // 2 + 150), 'Hard Computer', BUTTONIMAGE1_LG),
    # No separate Quit button in original structure, it's Randomize changing name
]

# Game State Variables
GAMESTATE = C.MAIN_MENU
DEPLOYMENT = True
# TURNTIMER is not explicitly used in the modular takeTurns, using lastComputerAttackTime
lastComputerAttackTime = 0
gameOverMessageShown = False
winnerMessage = None
TOKENS = []
MESSAGE_BOXES = []
active_ship = None
STAGES = C.STAGE # Use STAGE from constants
# Make ROWS/COLS available if original button logic needs them directly
ROWS = C.ROWS
COLS = C.COLS

# --- Helper Function for Resetting Game ---
def reset_game_for_new_round():
    

    global pFleet, cFleet, pGameLogic, cGameLogic, player1, computer, TOKENS, MESSAGE_BOXES
    global DEPLOYMENT, GAMESTATE, gameOverMessageShown, winnerMessage, active_ship, lastComputerAttackTime

    # print("Resetting game for new round...") # Bỏ print thừa
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

    # <<< CHỈ ĐẶT STATE MỘT LẦN >>>
    DEPLOYMENT = True
    GAMESTATE = C.DEPLOYMENT_STATE # Luôn đặt về Deployment khi reset để chơi mới
    # <<< KẾT THÚC THAY ĐỔI >>>

    gameOverMessageShown = False
    winnerMessage = None
    active_ship = None
    lastComputerAttackTime = pygame.time.get_ticks()


# --- Main Game Loop (Following Original Structure) ---
RUNGAME = True
while RUNGAME:
    currentTime = pygame.time.get_ticks() # Get current time for AI logic

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUNGAME = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if event.button == 1: # Left Click
                # --- Original Logic: Handle Ship Drag / Attack FIRST ---
                if DEPLOYMENT == True:
                    clicked_on_ship = False # Reset flag
                    for ship in reversed(pFleet):
                        if ship.rect.collidepoint(mouse_pos):
                            # Original didn't check areShipsPlacedCorrectly here
                            ship.active = True
                            active_ship = ship
                            sortFleet(ship, pFleet) # Direct call
                            clicked_on_ship = True
                            break

                else: # Not Deployment (Attack Phase)
                    if player1.turn == True:
                        # Check if click is NOT on a button before attacking
                        is_button_click = False
                        for button in BUTTONS:
                             if button.active and button.rect.collidepoint(mouse_pos):
                                 is_button_click = True
                                 break
                        if not is_button_click:
                            attack_successful = player1.makeAttack( # Call MODULAR makeAttack
                                cGameGridCoords, cGameLogic, cFleet, TOKENS, MESSAGE_BOXES, SOUNDS
                            )
                            if attack_successful and not player1.turn: # If player missed
                                computer.turn = True
                                lastComputerAttackTime = currentTime # Update timer

                # --- Original Logic: ALWAYS Check Buttons AFTER ship/attack logic ---
                button_action_handled_this_click = False # Prevent multiple button actions
                for button in BUTTONS:
                    if button.active and button.rect.collidepoint(mouse_pos) and not button_action_handled_this_click:
                        # Determine actual action name based on state (Randomize/Quit)
                        action = button.name
                        if not DEPLOYMENT and action == 'Randomize': action = 'Quit'
                        elif DEPLOYMENT and action == 'Quit': action = 'Randomize'

                        print(f"Button Clicked: {action}") # DEBUG using determined action

                        # --- Handle Specific Button Actions Directly (like original) ---
                        if action == 'Deploy': # Only active when DEPLOYMENT is True
                            if areShipsPlacedCorrectly(pFleet, pGameGridCoords):
                                status = deploymentPhase(DEPLOYMENT) # False
                                DEPLOYMENT = status
                                player1.turn = True; computer.turn = False
                                lastComputerAttackTime = currentTime
                                updateGameLogic(pGameGridCoords, pFleet, pGameLogic)
                                updateGameLogic(cGameGridCoords, cFleet, cGameLogic)
                                print("--- Deployment Complete ---")
                                printGameLogic(pGameLogic, cGameLogic)
                                button_action_handled_this_click = True
                            else:
                                MESSAGE_BOXES.append(MessageBox("Please set up ship's position!", duration=2000))
                                button_action_handled_this_click = True # Action attempted

                        elif action == 'Redeploy': # Only active when DEPLOYMENT is False
                            print("Handling Redeploy (Resetting Game)...")
                            reset_game_for_new_round() # Reset the whole game
                            # reset_game_for_new_round sets GAMESTATE to DEPLOYMENT_STATE
                            button_action_handled_this_click = True

                        elif action == 'Quit': # Only active when DEPLOYMENT is False
                            print("Handling Quit...")
                            RUNGAME = False
                            button_action_handled_this_click = True

                        elif action in ['Easy Computer', 'Medium Computer', 'Hard Computer']:
                            # Only truly matters in Main Menu or Game Over state
                            if GAMESTATE == C.MAIN_MENU or GAMESTATE == C.GAME_OVER:
                                if action == 'Easy Computer': computer = EasyComputer()
                                elif action == 'Medium Computer': computer = MediumComputer()
                                elif action == 'Hard Computer': computer = HardComputer()
                                print(f"Selected AI: {computer.name}")
                                reset_game_for_new_round() # Start new game
                                button_action_handled_this_click = True
                            # If clicked during Deploy/Attack, do nothing for AI buttons

                        if not button_action_handled_this_click:
                             print(f"Calling actionOnPress for: {action}") # DEBUG
                             if action == 'Randomize': # Only active when DEPLOYMENT is True
                                 if DEPLOYMENT:
                                     randomizeShipPositions(pFleet, pGameGridCoords)
                                     updateGameLogic(pGameGridCoords, pFleet, pGameLogic)
                                     button_action_handled_this_click = True
                             elif action == 'Reset': # Only active when DEPLOYMENT is True
                                 if DEPLOYMENT:
                                     resetShips(pFleet, reset_position=True)
                                     updateGameLogic(pGameGridCoords, pFleet, pGameLogic)
                                     button_action_handled_this_click = True
                             elif action == 'Back to Main':
                                 # Should work in Deployment, Attack, Game Over
                                 GAMESTATE = C.MAIN_MENU
                                 DEPLOYMENT = True
                                 reset_game_for_new_round() # Reset game state fully
                                 GAMESTATE = C.MAIN_MENU      # Ensure state is Main Menu
                                 button_action_handled_this_click = True

                        # Break from button loop once one is handled
                        if button_action_handled_this_click:
                             break


            elif event.button == 2: # Middle Click
                printGameLogic(pGameLogic, cGameLogic) # Direct call

            elif event.button == 3: # Right Click
                if DEPLOYMENT == True: # Only rotate during deployment
                    for ship in pFleet:
                        if ship.rect.collidepoint(mouse_pos):
                            if not ship.checkForRotateCollisions([s for s in pFleet if s is not ship]):
                                ship.rotateShip(True)
                            else:
                                MESSAGE_BOXES.append(MessageBox("Cannot rotate: Collision!", duration=1500))
                            break # Only rotate one ship

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and DEPLOYMENT == True:
                if active_ship:
                    collision = active_ship.checkForCollisions([s for s in pFleet if s is not active_ship])
                    if not collision:
                        active_ship.snapToGrid(pGameGridCoords)  # Gọi snapToGrid để căn chỉnh
                        active_ship.active = False
                        updateGameLogic(pGameGridCoords, pFleet, pGameLogic)  # Cập nhật lưới logic
                    else:
                        active_ship.active = False
                        MESSAGE_BOXES.append(MessageBox("Ships cannot overlap!", duration=2000))
                        active_ship.returnToDefaultPosition()  # Trả về vị trí mặc định nếu va chạm
                    active_ship = None


    # --- Game Logic Updates (Outside Event Loop) ---
    # Ship Movement (Dragging) - Only if Deployment is True
    if DEPLOYMENT == True:
        if active_ship and active_ship.active:
            active_ship.selectShipAndMove()
            active_ship.snapToGridEdge(pGameGridCoords) # Original had snap edge during drag

    # --- Drawing --- (BEFORE Attack Phase Logic - like original)
    assets_dict = { 'backgrounds': { 'main_menu': MAINMENUIMAGE, 'game': BACKGROUND, 'end_screen': ENDSCREENIMAGE, }, 'grid_images': { 'player': PGAMEGRIDIMG, 'computer': CGAMEGRIDIMG, 'radar': RADARGRID, }, 'buttons': BUTTONS, 'sounds': SOUNDS, 'tokens': {'red': REDTOKEN, 'green': GREENTOKEN, 'blue': BLUETOKEN} }
    game_data_dict = { 'pFleet': pFleet, 'cFleet': cFleet, 'pGameGridCoords': pGameGridCoords, 'cGameGridCoords': cGameGridCoords, 'pGameLogic': pGameLogic, 'cGameLogic': cGameLogic, 'player1': player1, 'computer': computer, 'tokens_list': TOKENS, 'message_boxes_list': MESSAGE_BOXES, 'deployment_status': DEPLOYMENT, 'winner_message': winnerMessage, }
    updateGameScreen(GAMESCREEN, GAMESTATE, assets_dict, game_data_dict)

    # --- Attack Phase Turn Logic & AI --- (AFTER Drawing - like original)
    if not DEPLOYMENT and GAMESTATE == C.DEPLOYMENT_STATE: # Check if in Attack Phase
        player1Wins = checkForWinners(cGameLogic)
        computerWins = checkForWinners(pGameLogic)

        if player1Wins or computerWins: # Check win condition
            GAMESTATE = C.GAME_OVER # Set state to Game Over
            if player1Wins: winnerMessage = "PLAYER 1 WINS!"
            else: winnerMessage = f"{computer.name.upper()} WINS!"
            if not gameOverMessageShown:
                 MESSAGE_BOXES.append(MessageBox(winnerMessage, duration=4000))
                 gameOverMessageShown = True
        else: # Game continues, handle turns
             if computer.turn:
                 # Call modular takeTurns which handles computer's attack
                 lastComputerAttackTime = takeTurns(
                     player1, computer,
                     pGameLogic, pGameGridCoords, pFleet,
                     cGameLogic, cGameGridCoords, cFleet,
                     TOKENS, MESSAGE_BOXES, SOUNDS,
                     currentTime, lastComputerAttackTime
                 )
             # No need for extra computer.makeAttack call here if takeTurns handles it

    # --- Frame Rate Control ---
    clock.tick(60)

# --- Quit Pygame ---
pygame.quit()
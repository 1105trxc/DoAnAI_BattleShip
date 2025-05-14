# Game Settings and Variables
SCREENWIDTH = 1260
SCREENHEIGHT = 990
ROWS = 10
COLS = 10
CELLSIZE = 50

# Game States
MAIN_MENU = 'Main Menu'
DEPLOYMENT_STATE = 'Deployment'
GAME_OVER = 'Game Over'
STAGE = [MAIN_MENU, DEPLOYMENT_STATE, GAME_OVER]

# Asset Paths and Fleet Configuration
FLEET = {
    'carrier': ['carrier', 'assets/images/ships/carrier/carrier.png', (50, 600), (45, 245),
                0, '', None, None],
    'battleship': ['battleship', 'assets/images/ships/battleship/battleship.png', (125, 600), (40, 195),
                   4, 'assets/images/ships/battleship/battleshipgun.png', (0.4, 0.125), [-0.525, -0.34, 0.67, 0.49]],
    'destroyer': ['destroyer', 'assets/images/ships/destroyer/destroyer.png', (200, 600), (30, 145),
                  2, 'assets/images/ships/destroyer/destroyergun.png', (0.5, 0.15), [-0.52, 0.71]],
    'submarine': ['submarine', 'assets/images/ships/submarine/submarine.png', (275, 600), (30, 145),
                  1, 'assets/images/ships/submarine/submarinegun.png', (0.25, 0.125), [-0.45]],
    'patrol boat': ['patrol boat', 'assets/images/ships/patrol boat/patrol boat.png', (350, 600), (20, 95),
                    0, '', None, None]
}

# Image Paths
MAINMENUIMAGE_PATH = 'assets/images/background/bg2.jpg'
ENDSCREENIMAGE_PATH = 'assets/images/background/bg1.jpg'
BACKGROUND_PATH = 'assets/images/background/gamebg.png'
PGAMEGRIDIMG_PATH = 'assets/images/grids/player_grid.png'
CGAMEGRIDIMG_PATH = 'assets/images/grids/comp_grid.png'
BUTTONIMAGE_PATH = 'assets/images/buttons/button.png'
REDTOKEN_PATH = 'assets/images/tokens/redtoken.png'
GREENTOKEN_PATH = 'assets/images/tokens/greentoken.png'
BLUETOKEN_PATH = 'assets/images/tokens/bluetoken.png'
FIRETOKEN_ANIM_PATH = 'assets/images/tokens/fireloop/fire1_ '
EXPLOSIONSPRITESHEET_PATH = 'assets/images/tokens/explosion/explosion.png'
RADARGRID_PATH = 'assets/images/grids/grid_faint.png'

# Sound Paths
HITSOUND_PATH = 'assets/sounds/explosion.wav'
SHOTSOUND_PATH = 'assets/sounds/gunshot.wav'
MISSSOUND_PATH = 'assets/sounds/splash.wav'

# Colors 
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
BLUE = (0, 17, 167)
MESSAGE_BG_COLOR = (50, 50, 50, 200)
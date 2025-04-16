#  Module Imports
import pygame


#  Module Initialization
pygame.init()


#  Game Assets and Objects
class Ship:
    def __init__(self, name, img, pos, size, numGuns=0, gunPath=None, gunsize=None, gunCoordsOffset=None):
        self.name = name
        self.pos = pos
        #  Load the Vertical image
        self.vImage = loadImage(img, size)
        self.vImageWidth = self.vImage.get_width()
        self.vImageHeight = self.vImage.get_height()
        self.vImageRect = self.vImage.get_rect()
        self.vImageRect.topleft = pos
        #  Load the Horizontal image
        self.hImage = pygame.transform.rotate(self.vImage, -90)
        self.hImageWidth = self.hImage.get_width()
        self.hImageHeight = self.hImage.get_height()
        self.hImageRect = self.hImage.get_rect()
        self.hImageRect.topleft = pos
        #  Image and Rectangle
        self.image = self.vImage
        self.rect = self.vImageRect
        self.rotation = False
        #  Ship is current selection
        self.active = False
        #  Load gun Images
        self.gunslist = []
        if numGuns > 0:
            self.gunCoordsOffset = gunCoordsOffset
            for num in range(numGuns):
                self.gunslist.append(
                    Guns(gunPath,
                         self.rect.center,
                         (size[0] * gunsize[0],
                          size[1] * gunsize[1]),
                         self.gunCoordsOffset[num])
                )


    def draw(self, window):
        """Draw the ship to the screen"""
        window.blit(self.image, self.rect)
        for guns in self.gunslist:
            guns.draw(window, self)


class Guns:
    def __init__(self, imgPath, pos, size, offset):
        self.orig_image = loadImage(imgPath, size, True)
        self.image = self.orig_image
        self.offset = offset
        self.rect = self.image.get_rect(center=pos)


    def update(self, ship):
        """Updating the Guns Positions on the ship"""
        self.rect.center = (ship.rect.centerx, ship.rect.centery + (ship.image.get_height()//2 * self.offset))


    def draw(self, window, ship):
        self.update(ship)
        window.blit(self.image, self.rect)


#  Game Utility Functions
def createGameGrid(rows, cols, cellsize, pos):
    """Creates a game grid with coordinates for each cell"""
    startX = pos[0]
    startY = pos[1]
    coordGrid = []
    for row in range(rows):
        rowX = []
        for col in range(cols):
            rowX.append((startX, startY))
            startX += cellsize
        coordGrid.append(rowX)
        startX = pos[0]
        startY += cellsize
    return coordGrid


def createGameLogic(rows, cols):
    """Updates the game grid with logic, ie - spaces and X for ships"""
    gamelogic = []
    for row in range(rows):
        rowX = []
        for col in range(cols):
            rowX.append(' ')
        gamelogic.append(rowX)
    return gamelogic


def showGridOnScreen(window, cellsize, playerGrid, computerGrid):
    """Draws the player and computer grids to the screen"""
    gamegrids = [playerGrid, computerGrid]
    for grid in gamegrids:
        for row in grid:
            for col in row:
                pygame.draw.rect(window, (255, 255, 255), (col[0], col[1], cellsize, cellsize), 1)


def printGameLogic():
    """prints to the terminal the game logic"""
    print('Player Grid'.center(50, '#'))
    for _ in pGameLogic:
        print(_)
    print('Computer Grid'.center(50, '#'))
    for _ in cGameLogic:
        print(_)


def loadImage(path, size, rotate=False):
    """A function to import the images into memory"""
    img = pygame.image.load(path).convert_alpha()
    img = pygame.transform.scale(img, size)
    if rotate == True:
        img = pygame.transform.rotate(img, -90)
    return img


def createFleet():
    """Creates the fleet of ships"""
    fleet = []
    for name in FLEET.keys():
        fleet.append(
            Ship(name,
                 FLEET[name][1],
                 FLEET[name][2],
                 FLEET[name][3],
                 FLEET[name][4],
                 FLEET[name][5],
                 FLEET[name][6],
                 FLEET[name][7])
        )
    return fleet


def updateGameScreen(window):
    window.fill((0, 0, 0))

    #  Draws the player and computer grids to the screen
    showGridOnScreen(window, CELLSIZE, pGameGrid, cGameGrid)

    #  Draw ships to screen
    for ship in pFleet:
        ship.draw(window)

    pygame.display.update()


#  Game Settings and Variables
SCREENWIDTH = 1260
SCREENHEIGHT = 960
ROWS = 10
COLS = 10
CELLSIZE = 50


#  Colors


#  Pygame Display Initialization
GAMESCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption('Battle Ship')


#  Game Lists/DIctionaries
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

#  Loading Game Variables
pGameGrid = createGameGrid(ROWS, COLS, CELLSIZE, (50, 50))
pGameLogic = createGameLogic(ROWS, COLS)
pFleet = createFleet()

cGameGrid = createGameGrid(ROWS, COLS, CELLSIZE, (SCREENWIDTH - (ROWS * CELLSIZE), 50))
cGameLogic = createGameLogic(ROWS, COLS)
cFleet = None

printGameLogic()
#  Loading Game Sounds and Images


#  Initialize Players


#  Main Game Loop
RUNGAME = True
while RUNGAME:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUNGAME = False

    updateGameScreen(GAMESCREEN)

pygame.quit()


# Khởi tạo font một lần để tối ưu
pygame.font.init() # Cần thiết nếu dùng font trước pygame.init() chính
STENCIL_FONT_22 = pygame.font.SysFont('Stencil', 22)
STENCIL_FONT_30 = pygame.font.SysFont('Stencil', 30)

# Khởi tạo màu sắc
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
BLUE = (0, 17, 167)
MESSAGE_BG_COLOR = (50, 50, 50, 200)

class Button:
    def __init__(self, image, size, pos, msg, button_image_larger=None): # Allow passing larger image
        self.name = msg
        self.image = image # Should be the loaded pygame.Surface
        # Create larger image if not provided
        if button_image_larger:
             self.imageLarger = button_image_larger
        elif self.image:
             self.imageLarger = pygame.transform.scale(self.image, (size[0] + 10, size[1] + 10))
        else:
             self.imageLarger = None # Handle case where image is None

        if self.image:
            self.rect = self.image.get_rect(topleft=pos)
        else:
            # Fallback rect if no image
            self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])

        self.active = False # Whether the button is currently enabled/clickable
        self.msg = self.addText(msg)
        self.msgRect = self.msg.get_rect(center=self.rect.center)


    def addText(self, msg):
        # Use the pre-loaded font
        message = STENCIL_FONT_22.render(msg, 1, WHITE)
        return message


    def focusOnButton(self, window):
        # Highlight button on mouse hover if active
        if self.active and self.image and self.imageLarger: # Check images exist
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                # Center the larger image relative to the original rect's center
                larger_rect = self.imageLarger.get_rect(center=self.rect.center)
                window.blit(self.imageLarger, larger_rect)
            else:
                window.blit(self.image, self.rect)
        elif self.active and self.image: # Draw normal image if no larger one
             window.blit(self.image, self.rect)
        # Optionally draw a simple rect if no image but active?
        # elif self.active:
        #     pygame.draw.rect(window, (100, 100, 100), self.rect) # Example grey rect


    # actionOnPress now needs arguments or needs main loop to handle actions
    # Option 1: Return action name (preferred)
    def get_action_on_press(self):
         if self.active and self.rect.collidepoint(pygame.mouse.get_pos()):
              # Return the name/action identifier
              return self.name
         return None


    def updateButtons(self, current_deployment_status):
        # Updates button text based on deployment status
        original_name = self.name # Store original if needed for logic
        updated = False
        if original_name == 'Deploy' and not current_deployment_status:
            self.name = 'Redeploy'
            updated = True
        elif original_name == 'Redeploy' and current_deployment_status:
            self.name = 'Deploy'
            updated = True

        if original_name == 'Randomize' and not current_deployment_status:
            self.name = 'Quit' # Or maybe 'Main Menu'? Quit seems drastic here.
            updated = True
        elif original_name == 'Quit' and current_deployment_status:
             self.name = 'Randomize'
             updated = True

        if updated: # Only update text if name changed
            self.msg = self.addText(self.name)
            self.msgRect = self.msg.get_rect(center=self.rect.center)


    def draw(self, window, current_deployment_status):
         # Update button state/text if needed (e.g., Deploy/Redeploy)
         self.updateButtons(current_deployment_status)
         # Draw the button visual (handling hover)
         self.focusOnButton(window)
         # Draw the text on top
         window.blit(self.msg, self.msgRect)



class Tokens:
    def __init__(self, image_surface, pos, action, imageList=None, explosionList=None, soundFile=None):
        self.image = image_surface # Expecting a loaded pygame.Surface
        self.rect = self.image.get_rect(topleft=pos) if self.image else pygame.Rect(pos[0],pos[1],0,0)
        self.pos = pos # Store original top-left for reference
        self.imageList = imageList if imageList else [] # Fire animation
        self.explosionList = explosionList if explosionList else [] # Explosion animation
        self.action = action # 'Hit', 'Miss'
        # self.soundFile = soundFile # Sound handled in main loop now
        self.timer = pygame.time.get_ticks()
        self.imageIndex = 0 # Index for fire animation
        self.explosionIndex = 0 # Index for explosion animation
        self.explosion_finished = False # Flag if explosion animation is done


    def animate_Explosion(self):
        # Plays explosion animation once, then switches to fire
        if not self.explosion_finished and self.explosionIndex < len(self.explosionList):
             # Advance frame (consider timing)
             # Simple frame-by-frame for now
             img = self.explosionList[self.explosionIndex]
             self.explosionIndex += 1
             return img
        else:
             self.explosion_finished = True
             return self.animate_fire()


    def animate_fire(self):
        # Loops the fire animation
        if not self.imageList: # If no fire animation, return current static image
            return self.image

        # Update frame based on timer
        now = pygame.time.get_ticks()
        if now - self.timer >= 100: # 100ms per frame
            self.timer = now
            self.imageIndex = (self.imageIndex + 1) % len(self.imageList) # Loop index

        return self.imageList[self.imageIndex]


    def draw(self, window):
        if not self.image: return # Don't draw if no image

        display_image = None
        if self.action == 'Hit':
             if self.explosionList and not self.explosion_finished:
                  display_image = self.animate_Explosion()
             elif self.imageList:
                  display_image = self.animate_fire()
             else:
                  display_image = self.image # Fallback to static hit token
        else: # Miss or other actions
            display_image = self.image

        if display_image:
             # Adjust position slightly for animations (like the original code)
             temp_rect = display_image.get_rect(topleft=self.pos)
             if self.action == 'Hit' and (self.imageList or self.explosionList):
                  temp_rect.top = self.pos[1] - 10 # Move up slightly for fire/explosion
             window.blit(display_image, temp_rect)

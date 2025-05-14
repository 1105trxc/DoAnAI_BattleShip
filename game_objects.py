import pygame
from constants import CELLSIZE, MESSAGE_BG_COLOR, RED, WHITE
from utils import loadImage, STENCIL_FONT_22, STENCIL_FONT_30 

class MessageBox:
    def __init__(self, message, ship_image=None, duration=2000):
        self.font = STENCIL_FONT_30 
        self.message = self.font.render(message, True, WHITE)
        self.bg_color = MESSAGE_BG_COLOR
        self.border_color = RED
        self.duration = duration
        self.start_time = pygame.time.get_ticks()

        self.ship_image = ship_image

        self.padding = 20
        self.text_width = self.message.get_width()
        self.text_height = self.message.get_height()

        if self.ship_image:
            self.image_width = self.ship_image.get_width()
            self.image_height = self.ship_image.get_height()
            self.width = max(self.text_width, self.image_width) + self.padding * 2
            self.height = self.text_height + self.image_height + self.padding * 3
        else:
            self.width = self.text_width + self.padding * 2
            self.height = self.text_height + self.padding * 2

        # Center based on constants 
        from constants import SCREENWIDTH, SCREENHEIGHT
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (SCREENWIDTH // 2, SCREENHEIGHT // 2)

    def draw(self, window):
        if pygame.time.get_ticks() - self.start_time < self.duration:
            surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            surface.fill(self.bg_color)
            window.blit(surface, self.rect)

            pygame.draw.rect(window, self.border_color, self.rect, 2)

            message_rect = self.message.get_rect()
            message_rect.center = (self.rect.centerx, self.rect.top + self.padding + self.text_height // 2)
            window.blit(self.message, message_rect)

            if self.ship_image:
                image_rect = self.ship_image.get_rect()
                image_rect.center = (self.rect.centerx, message_rect.bottom + self.padding + self.image_height // 2)
                window.blit(self.ship_image, image_rect)

            return True
        return False


class Guns:
    def __init__(self, imgPath, pos, size, offset):
        self.orig_image = loadImage(imgPath, size, True) if imgPath else None
        self.image = self.orig_image
        self.offset = offset
        if self.image:
            self.rect = self.image.get_rect(center=pos)
        else:
            self.rect = pygame.Rect(pos[0], pos[1], 0, 0)


    def update(self, ship):
        if not self.orig_image: return

        self.rotateGuns(ship)
        if not ship.rotation: # Vertical
            self.rect.center = (ship.rect.centerx, ship.rect.centery + (ship.vImageHeight // 2 * self.offset))
        else: # Horizontal
             self.rect.center = (ship.rect.centerx + (ship.hImageWidth // 2 * -self.offset), ship.rect.centery)


    def _update_image(self, angle):
       if not self.orig_image: return
       self.image = pygame.transform.rotate(self.orig_image, -angle)
       self.rect = self.image.get_rect(center=self.rect.center)


    def rotateGuns(self, ship):
        if not self.orig_image: return
        direction = pygame.math.Vector2(pygame.mouse.get_pos()) - pygame.math.Vector2(self.rect.center)
        if direction.length() == 0: return
        radius, angle = direction.as_polar()

        if not ship.rotation:
            self._update_image(angle)
        else:
             self._update_image(angle)


    def draw(self, window, ship):
       if not self.orig_image: return
       self.update(ship)
       window.blit(self.image, self.rect)


class Ship:
    def __init__(self, name, img_path, pos, size, numGuns=0, gunPath=None, gunsize=None, gunCoordsOffset=None):
        self.name = name
        self.pos = pos
        # Load images using the utility function
        self.vImage = loadImage(img_path, size)
        self.vImageWidth = self.vImage.get_width()
        self.vImageHeight = self.vImage.get_height()
        self.vImageRect = self.vImage.get_rect(topleft=pos)

        self.hImage = pygame.transform.rotate(self.vImage, -90)
        self.hImageWidth = self.hImage.get_width()
        self.hImageHeight = self.hImage.get_height()
        self.hImageRect = self.hImage.get_rect(topleft=pos) # Initial rect same pos

        # Current state
        self.image = self.vImage
        self.rect = self.vImageRect.copy() # Use copy to avoid modifying original
        self.rotation = False # False = Vertical, True = Horizontal
        self.active = False # Is the ship currently being dragged?
        self.is_sunk = False

        # Initialize guns
        self.gunslist = []
        if numGuns > 0 and gunPath and gunsize and gunCoordsOffset:
            self.gunCoordsOffset = gunCoordsOffset
            for i in range(numGuns):
                # Calculate initial gun position based on ship center and offset
                # This needs careful calculation based on whether ship starts vertical/horizontal
                # Assuming starts vertical:
                initial_center_x = self.vImageRect.centerx
                initial_center_y = self.vImageRect.centery + (self.vImageHeight // 2 * self.gunCoordsOffset[i])
                gun_pos = (initial_center_x, initial_center_y)
                gun_actual_size = (size[0] * gunsize[0], size[1] * gunsize[1])

                self.gunslist.append(
                    Guns(gunPath, gun_pos, gun_actual_size, self.gunCoordsOffset[i])
                )
        else:
             self.gunCoordsOffset = [] # Ensure it exists even if no guns


    def selectShipAndMove(self):
        # Moves the center of the ship's current rect to the mouse position
        self.rect.center = pygame.mouse.get_pos()
        # Update both potential rects to stay synchronized with the current center
        self.vImageRect.center = self.rect.center
        self.hImageRect.center = self.rect.center


    def rotateShip(self, doRotation=False):
        # Rotates the ship if it's active or forced
        if self.active or doRotation:
            self.rotation = not self.rotation
            self.switchImageAndRect()


    def switchImageAndRect(self):
        # Switches the active image and rect based on rotation state
        current_center = self.rect.center # Preserve the center point
        if self.rotation: # Switch to Horizontal
            self.image = self.hImage
            self.rect = self.hImageRect
        else: # Switch to Vertical
            self.image = self.vImage
            self.rect = self.vImageRect
        # Re-center the new rect
        self.rect.center = current_center
        # Keep the inactive rect centered as well
        if self.rotation:
            self.vImageRect.center = current_center
        else:
            self.hImageRect.center = current_center


    def checkForCollisions(self, shiplist):
        # Checks collision with other ships in the list
        # Make sure shiplist contains other ships, not itself
        for other_ship in shiplist:
            if other_ship is not self and self.rect.colliderect(other_ship.rect):
                return True
        return False


    def checkForRotateCollisions(self, shiplist):
        # Checks if rotating the ship *would* cause a collision
        current_center = self.rect.center
        temp_rect_to_check = None

        if self.rotation: # Currently Horizontal, check Vertical collision
            temp_rect_to_check = self.vImage.get_rect(center=current_center)
        else: # Currently Vertical, check Horizontal collision
            temp_rect_to_check = self.hImage.get_rect(center=current_center)

        for other_ship in shiplist:
            if other_ship is not self and temp_rect_to_check.colliderect(other_ship.rect):
                return True
        return False


    def returnToDefaultPosition(self):
        # Resets rotation to vertical and position to the initial one
        if self.rotation:
            # Need to force rotation back without checking 'active'
            self.rotation = False
            self.switchImageAndRect() # This switches image/rect and centers
        # Now set the position correctly
        self.rect.topleft = self.pos
        # Sync both rects
        self.vImageRect.topleft = self.pos
        self.hImageRect.topleft = self.pos # Adjust center after setting topleft
        self.hImageRect.center = self.vImageRect.center


    def snapToGrid(self, gridCoords):
        """Snaps the ship to the grid using the original centering logic."""
        snapped = False # Flag to check if snapped
        for rowX in gridCoords:
            for cell in rowX:
                # Check if the ship's top-left is within the bounds of this cell
                # We use the current rect's position for checking where it was dropped
                if self.rect.left >= cell[0] and self.rect.left < cell[0] + CELLSIZE \
                   and self.rect.top >= cell[1] and self.rect.top < cell[1] + CELLSIZE:

                    target_cell_coord = cell # The top-left corner of the target cell

                    if not self.rotation: # Vertical ship
                        # Calculate new top-left: Center horizontally, align top vertically
                        new_left = target_cell_coord[0] + (CELLSIZE - self.vImageWidth) // 2
                        new_top = target_cell_coord[1]
                        # Check boundaries to prevent going off grid bottom
                        allowed_rows = len(gridCoords)
                        ship_height_cells = (self.vImageHeight + CELLSIZE - 1) // CELLSIZE
                        current_row_index = gridCoords.index(rowX) # Find current row index
                        if current_row_index > allowed_rows - ship_height_cells:
                             new_top = gridCoords[allowed_rows - ship_height_cells][gridCoords[current_row_index].index(cell)][1]

                        self.rect.topleft = (new_left, new_top)
                        snapped = True
                        break # Stop checking cells once snapped

                    else: # Horizontal ship
                        # Calculate new top-left: Align left horizontally, center vertically
                        new_left = target_cell_coord[0]
                        new_top = target_cell_coord[1] + (CELLSIZE - self.hImageHeight) // 2
                        # Check boundaries to prevent going off grid right
                        allowed_cols = len(gridCoords[0])
                        ship_width_cells = (self.hImageWidth + CELLSIZE - 1) // CELLSIZE
                        current_col_index = rowX.index(cell) # Find current column index
                        if current_col_index > allowed_cols - ship_width_cells:
                             new_left = gridCoords[gridCoords.index(rowX)][allowed_cols - ship_width_cells][0]

                        self.rect.topleft = (new_left, new_top)
                        snapped = True
                        break # Stop checking cells once snapped
            if snapped:
                break # Stop checking rows once snapped

        # Sync the centers of both image rects after snapping
        self.hImageRect.center = self.vImageRect.center = self.rect.center


    def snapToGridEdge(self, gridCoords):
        if self.rect.topleft != self.pos:
            if self.rect.left > gridCoords[0][-1][0] + 50 or \
               self.rect.right < gridCoords[0][0][0] or \
               self.rect.top > gridCoords[-1][0][1] + 50 or \
               self.rect.bottom < gridCoords[0][0][1]:
                self.returnToDefaultPosition()
            elif self.rect.right > gridCoords[0][-1][0]+50:
                self.rect.right = gridCoords[0][-1][0] + 50
            elif self.rect.left < gridCoords[0][0][0]:
                self.rect.left = gridCoords[0][0][0]
            elif self.rect.top < gridCoords[0][0][1]:
                self.rect.top = gridCoords[0][0][1]
            elif self.rect.bottom > gridCoords[-1][0][1] + 50:
                self.rect.bottom = gridCoords[-1][0][1] + 50
            self.vImageRect.center = self.hImageRect.center = self.rect.center


    def draw(self, window, is_computer_grid=False):
        # Draw the ship unless it's the computer's hidden ship
        if not is_computer_grid or self.is_sunk:
            window.blit(self.image, self.rect)
            # Draw guns only if the ship itself is visible
            for gun in self.gunslist:
                gun.draw(window, self)


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

    # Option 2: Keep original calls (requires careful imports or passing objects - less ideal)
    # def actionOnPress(self, pFleet, cFleet, pGameGrid, cGameGrid, pGameLogic, cGameLogic, TOKENS, DEPLOYMENT_STATUS_VAR):
    #     # This version needs many parameters passed in
    #     if self.active:
    #         if self.name == 'Randomize':
    #             # Needs access to randomizeShipPositions function and fleets/grids
    #             from game_logic import randomizeShipPositions # Potential circular import issue?
    #             if DEPLOYMENT_STATUS_VAR: # Check deployment status
    #                randomizeShipPositions(pFleet, pGameGrid)
    #                # randomizeShipPositions(cFleet, cGameGrid) # Don't randomize computer here?
    #         elif self.name == 'Reset':
    #             # Needs access to resetShips function
    #             from game_logic import resetShips
    #             if DEPLOYMENT_STATUS_VAR:
    #                  resetShips(pFleet)
    #         elif self.name == 'Deploy':
    #              # Logic handled in main loop based on return value or state change
    #              pass
    #         elif self.name == 'Quit':
    #              # Logic handled in main loop
    #              pass
    #         elif self.name == 'Redeploy':
    #              # Logic handled in main loop
    #              pass
    #         elif self.name == 'Back to Main':
    #              # Logic handled in main loop
    #              pass


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

        # Add logic for Reset/Radar Scan if re-enabled later
        # if original_name == 'Reset' and not current_deployment_status:
        #    self.name = 'Radar Scan'
        #    updated = True
        # elif original_name == 'Radar Scan' and current_deployment_status:
        #    self.name = 'Reset'
        #    updated = True

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
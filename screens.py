import pygame # Đảm bảo pygame được import
from constants import MAIN_MENU, DEPLOYMENT_STATE, GAME_OVER, WHITE, BLACK, CELLSIZE # Import constants
from utils import displayShipNames # Import utils
from board import showGridOnScreen # Import board functions

def mainMenuScreen(window, background_image, buttons):
    """Draws the Main Menu screen."""
    window.blit(background_image, (0, 0))

     # Draw the game title "Battle Ship"
    font = pygame.font.SysFont('Stencil', 120)  
    title_surface = font.render("BattleShip", True, BLACK)  
    title_rect = title_surface.get_rect(topleft=(300, 170)) 
    window.blit(title_surface, title_rect)

    # Draw only relevant buttons for Main Menu
    for button in buttons:
        # Activate only AI selection buttons in Main Menu
        if button.name in ['Easy Computer', 'Medium Computer', 'Hard Computer']:
            button.active = True
            button.draw(window, True) # Pass True for deployment status (doesn't affect these buttons)
        else:
            button.active = False # Deactivate other buttons like Deploy, Reset etc.

def deploymentScreen(window, background_image, pGameGridImg, cGameGridImg, radarGridImg,
                     pGameGridCoords, cGameGridCoords, pFleet, cFleet, buttons,
                     computer_player, tokens_list, current_deployment_status):
    """Draws the Deployment/Attack screen with correct button activation."""
    window.blit(background_image, (0, 0))

    # --- Vẽ nền lưới và lưới kẻ ---
    if pGameGridImg and pGameGridCoords: window.blit(pGameGridImg, (0, 0))
    if cGameGridImg and cGameGridCoords: window.blit(cGameGridImg, (cGameGridCoords[0][0][0] - 50, cGameGridCoords[0][0][1] - 50))
    if radarGridImg and cGameGridCoords: window.blit(radarGridImg, (cGameGridCoords[0][0][0], cGameGridCoords[0][0][1]))
    if pGameGridCoords or cGameGridCoords:
        showGridOnScreen(window, CELLSIZE, pGameGridCoords, cGameGridCoords)

    # --- Vẽ Tàu ---
    for ship in pFleet: ship.draw(window, is_computer_grid=False)
    for ship in cFleet: ship.draw(window, is_computer_grid=True)

    # --- Vẽ Tên Tàu (Chỉ khi đang Deploy) ---
    if current_deployment_status:
        try:
            from constants import FLEET
            displayShipNames(window, FLEET.keys())
        except ImportError: print("Warning: Could not import FLEET from constants in screens.py")

    # --- Vẽ Nút Bấm (Logic kích hoạt và đổi tên chính xác) ---
    for button in buttons:
        # Xác định tên nút hiệu quả sẽ được hiển thị/kiểm tra
        effective_button_name = button.name
        if not current_deployment_status and button.name == 'Randomize': effective_button_name = 'Quit'
        elif current_deployment_status and button.name == 'Quit': effective_button_name = 'Randomize'
        elif not current_deployment_status and button.name == 'Deploy': effective_button_name = 'Redeploy'
        elif current_deployment_status and button.name == 'Redeploy': effective_button_name = 'Deploy'

        is_button_active_in_this_state = False
        # Kích hoạt nút dựa trên trạng thái VÀ tên HIỆU QUẢ
        if current_deployment_status: # Đang Đặt Tàu
            if effective_button_name in ['Randomize', 'Reset', 'Deploy', 'Back to Main']:
                is_button_active_in_this_state = True
        else: # Đang Tấn Công
            if effective_button_name in ['Redeploy', 'Quit', 'Back to Main']:
                is_button_active_in_this_state = True
        # Các nút chọn AI không bao giờ active trong màn hình này
        if effective_button_name in ['Easy Computer', 'Medium Computer', 'Hard Computer']:
             is_button_active_in_this_state = False

        # Cập nhật trạng thái active của đối tượng nút
        button.active = is_button_active_in_this_state

        # Cập nhật tên và text nếu tên hiệu quả khác tên gốc lưu trong nút
        if button.name != effective_button_name:
            button.name = effective_button_name
            button.msg = button.addText(button.name) # Render lại text
            button.msgRect = button.msg.get_rect(center=button.rect.center) # Cập nhật vị trí text

        # Chỉ VẼ nút nếu nó ACTIVE trong trạng thái này
        if button.active:
            button.draw(window, current_deployment_status)

    # --- Vẽ Trạng Thái Máy Tính (Chỉ khi đang Tấn công?) ---
    if not current_deployment_status and computer_player and cGameGridCoords:
         computer_player.draw(window, cGameGridCoords)

    # --- Vẽ Tokens ---
    for token in tokens_list:
        token.draw(window)

def endScreen(window, background_image, buttons, winner_message):
    """Draws the Game Over screen."""
    window.blit(background_image, (0, 0))
    for button in buttons:
        # Kích hoạt các nút AI và nút "Quit" (đã đổi từ "Back to Main")
        if button.name in ['Easy Computer', 'Medium Computer', 'Hard Computer', 'Quit']:
            button.active = True
            button.draw(window, False)
        else:
            # Jewish font (for "Back to Main") is not properly handled in this state
            button.active = False
    if winner_message:
         font = pygame.font.SysFont('Stencil', 60)
         text_surface = font.render(winner_message, True, WHITE)
         text_rect = text_surface.get_rect(center=(window.get_width() // 2, window.get_height() // 3))
         window.blit(text_surface, text_rect)

def updateGameScreen(window, game_state, assets, game_data):
    """Calls the appropriate drawing function based on the game state."""
    backgrounds = assets['backgrounds']
    grid_images = assets['grid_images']
    buttons = assets['buttons']
    pFleet = game_data['pFleet']
    cFleet = game_data['cFleet']
    pGameGridCoords = game_data['pGameGridCoords']
    cGameGridCoords = game_data['cGameGridCoords']
    computer = game_data['computer']
    tokens_list = game_data['tokens_list']
    message_boxes_list = game_data['message_boxes_list']
    deployment_status = game_data['deployment_status']
    winner_message = game_data.get('winner_message', None)

    if game_state == MAIN_MENU:
        mainMenuScreen(window, backgrounds['main_menu'], buttons)
    elif game_state == DEPLOYMENT_STATE:
        deploymentScreen(window, backgrounds['game'], grid_images['player'], grid_images['computer'], grid_images['radar'],
                         pGameGridCoords, cGameGridCoords, pFleet, cFleet, buttons,
                         computer, tokens_list, deployment_status)
    elif game_state == GAME_OVER:
        endScreen(window, backgrounds['end_screen'], buttons, winner_message)

    # Vẽ message boxes luôn ở trên cùng
    for i in range(len(message_boxes_list) - 1, -1, -1):
         if not message_boxes_list[i].draw(window):
             message_boxes_list.pop(i)

    pygame.display.update()
    
    
    
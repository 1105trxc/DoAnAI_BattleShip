import pygame

# Khởi tạo font một lần để tối ưu
pygame.font.init() # Cần thiết nếu dùng font trước pygame.init() chính
STENCIL_FONT_22 = pygame.font.SysFont('Stencil', 22)
STENCIL_FONT_30 = pygame.font.SysFont('Stencil', 30)

def loadImage(path, size, rotate=False, alpha=True):
    try:
        if alpha:
            img = pygame.image.load(path).convert_alpha()
        else:
            img = pygame.image.load(path).convert()
        img = pygame.transform.scale(img, size)
        if rotate:
            img = pygame.transform.rotate(img, -90)
        return img
    except pygame.error as e:
        print(f"Error loading image: {path} - {e}")
        # Trả về surface trống nếu lỗi để tránh crash
        return pygame.Surface(size, pygame.SRCALPHA)


def loadAnimationImages(path, aniNum, size):
    imageList = []
    for num in range(aniNum):
        filename = ""
        if num < 10:
            filename = f'{path}00{num}.png'
        elif num < 100:
            filename = f'{path}0{num}.png'
        else:
            filename = f'{path}{num}.png'
        imageList.append(loadImage(filename, size))
    return imageList

def loadSpriteSheetImages(spriteSheet, rows, cols, newSize, size):
    # Tạo surface tạm thời với kích thước gốc của một sprite
    image = pygame.Surface(size, pygame.SRCALPHA) # SRCALPHA để giữ độ trong suốt
    # Blit phần cần cắt từ sprite sheet vào surface tạm thời
    image.blit(spriteSheet, (0, 0), (cols * size[0], rows * size[1], size[0], size[1]))
    # Scale về kích thước mới
    image = pygame.transform.scale(image, newSize)
    # Không cần set_colorkey nếu đã load với convert_alpha() và nền trong suốt
    # image.set_colorkey((0, 0, 0)) # Chỉ cần nếu ảnh gốc có nền đen cần xóa
    return image

def loadSound(path, volume):
    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        return sound
    except pygame.error as e:
        print(f"Error loading sound: {path} - {e}")
        return None # Trả về None nếu lỗi

def shipLabelMaker(msg):
    # Sử dụng font đã khởi tạo
    textMessage = STENCIL_FONT_22.render(msg, 1, (0, 17, 167)) # BLUE color from constants
    textMessage = pygame.transform.rotate(textMessage, 90)
    return textMessage

def displayShipNames(window, ship_names, start_x=25, y_pos=600, spacing=75):
    shipLabels = []
    for name in ship_names:
        shipLabels.append(shipLabelMaker(name))
    current_x = start_x
    for item in shipLabels:
        window.blit(item, (current_x, y_pos))
        current_x += spacing
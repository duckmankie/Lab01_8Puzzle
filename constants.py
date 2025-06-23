import os

def lighten_color(color, amount=40):
    r = min(color[0] + amount, 255)
    g = min(color[1] + amount, 255)
    b = min(color[2] + amount, 255)
    return (r, g, b)

def darken_color(color, amount=40):
    r = max(color[0] - amount, 0)
    g = max(color[1] - amount, 0)
    b = max(color[2] - amount, 0)
    return (r, g, b)

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720

BOARD_REGION_WIDTH = 720
BOARD_REGION_HEIGHT = 720
RIGHT_PANEL_X = BOARD_REGION_WIDTH
RIGHT_PANEL_WIDTH = WINDOW_WIDTH - BOARD_REGION_WIDTH
RIGHT_PANEL_HEIGHT = WINDOW_HEIGHT

PUZZLE_PADDING = 20
PUZZLE_SIZE = BOARD_REGION_WIDTH - 2 * PUZZLE_PADDING  
TILE_SIZE = PUZZLE_SIZE // 3                            

PUZZLE_OFFSET_X = PUZZLE_PADDING
PUZZLE_OFFSET_Y = PUZZLE_PADDING

FPS = 90
ANIM_DURATION_MS = 300    
FADE_SPEED = 15           

COLOR_BG = (14,17,23)
COLOR_HIGHLIGHT = (70, 70, 70)
COLOR_TEXT = (220, 220, 220)
COLOR_BUTTON = (19,23,32)
CHECKBOX_BUTTON = (38,39,48)

# Dropdown specific colors

FADE_HOVER_SPEED = 5
COLOR_DROPDOWN_BUTTON = (38,39,48)
COLOR_DROPDOWN_MENU = (14,17,23)
BUTTON_OUTLINE_COLOR = (65, 68, 76)
BUTTON_OUTLINE_THICKNESS = 1
BUTTON_RADIUS = 10
DROPDOWN_RADIUS = 10

TEMPLATE_DIR = "assets/templates"

ALL_TEMPLATE_FILES = [
    os.path.join(TEMPLATE_DIR, fname)
    for fname in sorted(os.listdir(TEMPLATE_DIR))
    if fname.lower().endswith((".png", ".jpg", ".jpeg"))
]  

IMAGE_THUMB_SIZE = 80   
THUMBS_PER_ROW = 5      
THUMBS_SPACING = 10     

CHECKBOX_SIZE = 20
CHECKBOX_X = RIGHT_PANEL_X + 20
CHECKBOX_Y = WINDOW_HEIGHT - 40
LABEL_X = CHECKBOX_X + CHECKBOX_SIZE + 10
LABEL_Y = CHECKBOX_Y - 2

ALGORITHMS = ["BFS", "DFS", "A*", "Dijkstra", "UCS", "IDDFS", "IDA*", "Bi-dir Search"]

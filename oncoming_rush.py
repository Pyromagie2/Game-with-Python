"""
Oncoming Rush - A 2D Top-Down Endless Dodger Game
Built with Pygame for Linux
"""

import pygame
import json
import os
import random
import math
from enum import Enum, auto
from typing import List, Optional

# =============================================================================
# CONFIGURATION
# =============================================================================
class Config:
    # Window settings
    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 800
    FPS = 60
    
    # Road settings
    ROAD_WIDTH = 400
    ROAD_X = (WINDOW_WIDTH - ROAD_WIDTH) // 2  # Center the road
    NUM_LANES = 5  # Configurable lane count
    LANE_WIDTH = ROAD_WIDTH // NUM_LANES
    
    # Colors
    COLOR_GRASS = (34, 139, 34)
    COLOR_ROAD = (50, 50, 50)
    COLOR_LINE_WHITE = (255, 255, 255)
    COLOR_PLAYER = (50, 100, 200)
    COLOR_PLAYER_WINDSHIELD = (150, 200, 255)
    COLOR_PLAYER_WHEEL = (30, 30, 30)
    COLOR_ENEMY_CAR = (200, 50, 50)
    COLOR_ENEMY_TRUCK = (200, 150, 50)
    COLOR_ENEMY_VAN = (150, 100, 200)
    COLOR_ENEMY_TRACTOR = (60, 120, 40)
    COLOR_ENEMY_MOPED = (180, 180, 180)
    COLOR_ENEMY_WINDSHIELD = (100, 100, 100)
    COLOR_HUD_TEXT = (255, 255, 255)
    COLOR_SPEEDOMETER_LOW = (50, 200, 50)
    COLOR_SPEEDOMETER_HIGH = (200, 50, 50)
    COLOR_PAUSE_OVERLAY = (0, 0, 0, 180)
    COLOR_GAMEOVER_BG = (0, 0, 0, 220)
    COLOR_HIGHSCORE_NEW = (255, 215, 0)
    
    # Speed settings
    BASE_SPEED = 200  # px/s
    MAX_SPEED = 1300  # px/s
    SPEED_CURVE_EXPONENT = 1.0  # Linear curve for steady difficulty increase
    SPEED_NORM_TIME = 60  # 1 minute - game reaches ~2x speed at this point
    
    # Player settings
    PLAYER_WIDTH = 50
    PLAYER_HEIGHT = 80
    PLAYER_Y = WINDOW_HEIGHT - 150  # Fixed vertical position
    LANE_CHANGE_DURATION = 0.170  # seconds
    HITBOX_REDUCTION = 0.10  # 10% smaller hitbox
    
    # Enemy settings
    ENEMY_CAR_WIDTH = 50
    ENEMY_CAR_HEIGHT = 80
    ENEMY_TRUCK_WIDTH = 55
    ENEMY_TRUCK_HEIGHT = 120
    ENEMY_VAN_WIDTH = 52
    ENEMY_VAN_HEIGHT = 95
    ENEMY_TRACTOR_WIDTH = 58
    ENEMY_TRACTOR_HEIGHT = 85
    ENEMY_MOPED_WIDTH = 35
    ENEMY_MOPED_HEIGHT = 60
    MIN_SPAWN_DISTANCE_SAME_LANE = 250  # Minimum pixels between enemies on same lane
    MIN_REACTION_TIME = 1.5  # seconds
    TOP_BLOCKED_ZONE_Y = 200  # y < this value must have at least 1 free lane
    
    # Spawn timing (in seconds)
    SPAWN_INTERVAL_BASE = 2.5   # Sekunden zwischen Spawns bei Startgeschwindigkeit
    SPAWN_INTERVAL_MIN = 0.6    # Minimales Intervall bei Maximalgeschwindigkeit
    
    # Spawn probabilities (must sum to 1.0)
    SPAWN_CHANCE_CAR = 0.55     # Wahrscheinlichkeit dass ein Spawn ein PKW ist
    SPAWN_CHANCE_TRUCK = 0.20   # Wahrscheinlichkeit dass ein Spawn ein LKW ist
    SPAWN_CHANCE_VAN = 0.10     # Wahrscheinlichkeit dass ein Spawn ein Van ist
    SPAWN_CHANCE_TRACTOR = 0.10 # Wahrscheinlichkeit dass ein Spawn ein Traktor ist
    SPAWN_CHANCE_MOPED = 0.05   # Wahrscheinlichkeit dass ein Spawn ein Moped ist
    
    # Tank Event Configuration
    TANK_EVENT_CHANCE_PER_MINUTE = 0.25  # Wahrscheinlichkeit pro Minute dass Event startet (0.0–1.0)
    TANK_EVENT_COOLDOWN = 50          # Sekunden Mindestabstand zwischen zwei Tank-Events
    TANK_EVENT_EARLIEST = 20           # Frühester Zeitpunkt in Sekunden ab dem Event möglich ist
    
    # Spieler-Bewegung im Event
    TANK_MOVE_TO_CENTER_DURATION = 1.5   # Sekunden für Fahrt zur Bildschirmmitte
    
    # Tank
    TANK_W = 90                          # Breite des Panzers in Pixeln
    TANK_H = 110                         # Höhe des Panzers in Pixeln
    TANK_SPEED = 80                      # px/s – Panzerbewegung nach oben
    TANK_FIRE_INTERVAL = 1.8             # Sekunden zwischen Schüssen
    TANK_COLOR = (70, 90, 50)            # Olivgrün
    
    # Projektile
    BULLET_SPEED = 400                   # px/s
    BULLET_W = 10                        # Breite
    BULLET_H = 22                        # Höhe
    BULLET_COLOR = (255, 200, 0)         # Gelb
    
    # Mauer
    WALL_DELAY_AFTER_TANK = 20.0         # Sekunden nach Tank-Erscheinen bis Mauer erscheint
    WALL_APPROACH_SPEED_FACTOR = 1.5     # Faktor auf aktuelle Spielgeschwindigkeit für Mauer-Bewegung
    WALL_H = 40                          # Höhe der Mauer in Pixeln
    WALL_COLOR = (140, 140, 150)         # Grau
    RAMP_COLOR = (200, 160, 60)          # Goldgelb für Rampe
    RAMP_W = 80                          # Breite der Rampe in der Mauer
    
    # Sprung
    JUMP_DURATION = 1.2                  # Sekunden
    JUMP_ARC_HEIGHT = 180                # Pixel
    
    # Level thresholds (in seconds)
    LEVEL_THRESHOLDS = [0, 60, 180, 360, 600, 900, 1200, 1500]  # 8 levels
    
    # File paths
    HIGHSCORE_FILE = "highscore.json"
    
    # ── Spawn-Regel ───────────────────────────────
    MAX_SIMULTANEOUS_ENEMIES = NUM_LANES - 2
    
    # ── Tank (Spurwechsel) ────────────────────────
    TANK_LANE_CHANGE_INTERVAL = 2.2      # Sekunden zwischen Spurwechseln
    TANK_LANE_CHANGE_DURATION = 0.4      # Sekunden für die Spurwechsel-Animation
    TANK_LANE_CHANGE_CHANCE = 0.75       # Wahrscheinlichkeit dass er bei Intervall tatsächlich wechselt
    TANK_AIMS_AT_PLAYER = True           # True = wechselt bevorzugt auf Spieler-Spur
    
    # ── Event-System ──────────────────────────────
    EVENT_TRIGGER_CHANCE = 0.70          # 70% Chance dass überhaupt ein Event passiert
    EVENT_GLOBAL_COOLDOWN = 50           # Sekunden Mindestabstand nach jedem Event
    EVENT_EARLIEST = 20                 # Kein Event vor dieser Zeit (Sekunden)
    
    # Gewichtung der einzelnen Events (müssen sich zu 1.0 addieren)
    EVENT_WEIGHT_TANK = 0.25
    EVENT_WEIGHT_FOG = 0.25
    EVENT_WEIGHT_EMP = 0.25
    EVENT_WEIGHT_ASTEROID = 0.25
    
    # ── Nebel-Event ───────────────────────────────
    FOG_DURATION = 18.0                  # Sekunden wie lange der Nebel anhält
    FOG_FADE_IN_DURATION = 2.0           # Sekunden bis Nebel voll da ist
    FOG_FADE_OUT_DURATION = 2.5          # Sekunden bis Nebel wieder weg ist
    FOG_VISIBILITY_RADIUS = 130          # Pixel – sichtbarer Radius um das Spieler-Auto
    FOG_COLOR = (200, 210, 220)
    FOG_ALPHA_MAX = 235                  # 0–255, wie undurchsichtig der Nebel ist
    FOG_SPAWN_RATE_FACTOR = 0.6          # Gegner spawnen während Nebel 40% langsamer
    
    # ── EMP-Event ─────────────────────────────────
    EMP_DURATION = 12.0                  # Sekunden mit invertierten Controls
    EMP_WARNING_DURATION = 2.0           # Sekunden Vorwarnung vor Control-Inversion
    EMP_FLASH_INTERVAL = 0.08            # Sekunden zwischen Screen-Flicker-Frames
    EMP_FLICKER_COUNT = 6                # Anzahl Flicker-Frames beim EMP-Einschlag
    EMP_SCREEN_TINT_COLOR = (0, 180, 255)   # Blauer Tint während EMP aktiv ist
    EMP_SCREEN_TINT_ALPHA = 35           # Sehr leichter Blaustich
    EMP_SPAWN_RATE_FACTOR = 0.8          # Gegner spawnen 20% langsamer
    
    # ── Meteorschauer-Event ───────────────────────
    ASTEROID_EVENT_DURATION = 22.0       # Sekunden Gesamtdauer
    ASTEROID_WARNING_TIME = 1.2          # Sekunden zwischen Warnung und Einschlag
    ASTEROID_SPAWN_INTERVAL = 1.5        # Sekunden zwischen Meteoreinschlägen
    ASTEROID_BLOCK_DURATION = 3.5        # Sekunden wie lange eine Spur nach Einschlag gesperrt ist
    ASTEROID_SHADOW_COLOR = (200, 80, 0, 160)   # Warnsignal-Farbe (Spur-Highlight)
    ASTEROID_CRATER_COLOR = (80, 60, 50)
    ASTEROID_SIZE_MIN = 30               # Minimale Einschlaggröße in Pixeln
    ASTEROID_SIZE_MAX = 65               # Maximale Einschlaggröße in Pixeln
    ASTEROID_NORMAL_SPAWN_FACTOR = 0.5   # Gegenverkehr-Spawn 50% langsamer während Event
    SCREEN_SHAKE_DURATION = 0.3          # Sekunden Shake-Dauer
    SCREEN_SHAKE_MAGNITUDE = 5           # Pixel Shake-Stärke
    
    # ── Tag/Nacht-Zyklus ──────────────────────────
    DAY_NIGHT_CYCLE_DURATION = 120.0     # Sekunden für einen kompletten Tag-Nacht-Zyklus (Tag + Nacht)
    NIGHT_START_RATIO = 0.5              # Bei 50% des Zyklus beginnt die Nacht
    NIGHT_DURATION_RATIO = 0.4           # Nacht dauert 40% des Zyklus (48 Sekunden)
    COLOR_SKY_DAY = (135, 206, 235)      # Hellblau für Tag
    COLOR_SKY_DUSK = (255, 140, 90)      # Orange für Dämmerung
    COLOR_SKY_NIGHT = (25, 25, 50)       # Dunkelblau für Nacht
    HEADLIGHT_RANGE = 160                # Pixel – Reichweite der Scheinwerfer
    HEADLIGHT_ANGLE = 45                 # Grad – Öffnungswinkel des Lichtkegels
    HEADLIGHT_COLOR = (255, 255, 200, 180)  # Gelblich-weißer Lichtkegel
    
    # ── Autonomer Spurwechsel ─────────────────────
    AUTONOMOUS_LANE_CHANGE_ENABLED = True  # Wenn True, können Gegner spurwechseln
    AUTONOMOUS_LANE_CHANGE_DISTANCE = 2.0  # Wie viele Autolängen vor dem Spieler erkannt wird
    AUTONOMOUS_LANE_CHANGE_CHANCE = 0.3    # Chance dass ein Auto tatsächlich wechselt wenn möglich
    AUTONOMOUS_LANE_CHANGE_DURATION = 0.5  # Sekunden für Spurwechsel-Animation
    
    # ── Dekoration ─────────────────────────────────
    DECORATION_TREE_COLOR = (34, 100, 34)
    DECORATION_TREE_TRUNK_COLOR = (101, 67, 33)
    DECORATION_BUSH_COLOR = (50, 150, 50)
    DECORATION_FLOWER_COLORS = [(255, 100, 100), (255, 255, 100), (200, 100, 255), (255, 150, 50)]
    
    # ── Event-Timer ────────────────────────────────
    EVENT_CHECK_INTERVAL = 30            # Sekunden zwischen Event-Prüfungen (alle 30 Sekunden ein Event)


# =============================================================================
# GAME STATES
# =============================================================================
class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAMEOVER = auto()
    TANK_EVENT = auto()  # Special state for tank event
    FOG_EVENT = auto()   # Fog event state
    EMP_EVENT = auto()   # EMP event state
    ASTEROID_EVENT = auto()  # Asteroid event state


# =============================================================================
# TANK EVENT PHASES
# =============================================================================
class TankEventPhase(Enum):
    TRIGGER_ANNOUNCEMENT = auto()   # Phase 1: Trigger & Ankündigung
    MOVE_TO_CENTER = auto()         # Phase 2: Spieler fährt zur Mitte
    TANK_APPEARS = auto()           # Phase 3: Tank erscheint und feuert
    WALL_APPROACHING = auto()       # Phase 4: Mauer erscheint
    JUMP_SEQUENCE = auto()          # Phase 5: Sprung über die Mauer
    RETURN_AND_END = auto()         # Phase 6: Rückkehr & Ende des Events


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================
def format_time(seconds: float) -> str:
    """Format seconds as MM:SS"""
    mins = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{mins:02d}:{secs:02d}"


def load_highscore(filepath: str) -> int:
    """Load highscore from JSON file"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                return data.get("highscore", 0)
    except (json.JSONDecodeError, IOError):
        pass
    return 0


def save_highscore(filepath: str, score: int) -> None:
    """Save highscore to JSON file"""
    try:
        with open(filepath, 'w') as f:
            json.dump({"highscore": score}, f)
    except IOError:
        pass


def get_current_speed(elapsed_seconds: float) -> float:
    """Calculate current speed based on elapsed time using linear formula.
    
    After SPEED_NORM_TIME seconds (60s), speed reaches approximately 2x BASE_SPEED.
    This creates a steady difficulty increase where the game becomes twice as fast
    after 1 minute of play.
    """
    # Linear increase: speed = BASE_SPEED + (BASE_SPEED * elapsed / NORM_TIME)
    # At t=60s: speed = 150 + (150 * 60/60) = 300 px/s (2x base speed)
    speed_increase = Config.BASE_SPEED * (elapsed_seconds / Config.SPEED_NORM_TIME)
    return min(Config.BASE_SPEED + speed_increase, Config.MAX_SPEED)


def get_spawn_interval(speed: float) -> float:
    """Calculate spawn interval based on current speed"""
    speed_ratio = (speed - Config.BASE_SPEED) / (Config.MAX_SPEED - Config.BASE_SPEED)
    return Config.SPAWN_INTERVAL_BASE - speed_ratio * (Config.SPAWN_INTERVAL_BASE - Config.SPAWN_INTERVAL_MIN)


def get_level(elapsed_seconds: float) -> int:
    """Get current level (1-8) based on elapsed time"""
    for i, threshold in enumerate(Config.LEVEL_THRESHOLDS):
        if elapsed_seconds < threshold:
            return max(1, i)
    return len(Config.LEVEL_THRESHOLDS)


# =============================================================================
# ROAD CLASS
# =============================================================================
class Road:
    def __init__(self):
        self.line_offset = 0
        self.post_offset = 0
        self.decorations = []  # Liste für Dekorationselemente (Bäume, Büsche, Blumen)
        self.decoration_offset = 0
        self._generate_decorations()
        
    def _generate_decorations(self):
        """Generiere zufällige Dekorationen für beide Seiten der Straße"""
        self.decorations = []
        # Generiere Dekorationen in Abständen entlang der Straße
        y_pos = -200
        while y_pos < Config.WINDOW_HEIGHT + 200:
            # Linke Seite
            if random.random() < 0.7:  # 70% Chance für Dekoration
                decor_type = random.choice(['tree', 'bush', 'flowers'])
                x_offset = random.randint(20, 80)  # Abstand von der Straße
                if decor_type == 'tree':
                    size = random.randint(20, 35)
                    self.decorations.append({'type': 'tree', 'x': -x_offset, 'y': y_pos, 'size': size})
                elif decor_type == 'bush':
                    size = random.randint(15, 25)
                    self.decorations.append({'type': 'bush', 'x': -x_offset, 'y': y_pos, 'size': size})
                else:  # flowers
                    color = random.choice(Config.DECORATION_FLOWER_COLORS)
                    self.decorations.append({'type': 'flowers', 'x': -x_offset, 'y': y_pos, 'color': color})
            
            # Rechte Seite
            if random.random() < 0.7:  # 70% Chance für Dekoration
                decor_type = random.choice(['tree', 'bush', 'flowers'])
                x_offset = random.randint(20, 80)  # Abstand von der Straße
                road_right = Config.ROAD_X + Config.ROAD_WIDTH
                if decor_type == 'tree':
                    size = random.randint(20, 35)
                    self.decorations.append({'type': 'tree', 'x': road_right + x_offset, 'y': y_pos, 'size': size})
                elif decor_type == 'bush':
                    size = random.randint(15, 25)
                    self.decorations.append({'type': 'bush', 'x': road_right + x_offset, 'y': y_pos, 'size': size})
                else:  # flowers
                    color = random.choice(Config.DECORATION_FLOWER_COLORS)
                    self.decorations.append({'type': 'flowers', 'x': road_right + x_offset, 'y': y_pos, 'color': color})
            
            y_pos += random.randint(40, 80)  # Zufälliger Abstand zwischen Dekorationen
    
    def update(self, dt: float, speed: float) -> None:
        """Update road scrolling based on speed"""
        scroll_amount = speed * dt
        self.line_offset = (self.line_offset + scroll_amount) % 80
        self.post_offset = (self.post_offset + scroll_amount) % 100
        self.decoration_offset = (self.decoration_offset + scroll_amount)
        
        # Update decoration positions und regeneriere wenn nötig
        for decor in self.decorations:
            decor['y'] += scroll_amount
        
        # Regeneriere Dekorationen die aus dem Bild gescrollt sind
        if self.decoration_offset >= 200:
            self.decoration_offset = 0
            # Entferne alte Dekorationen und füge neue hinzu
            self.decorations = [d for d in self.decorations if d['y'] < Config.WINDOW_HEIGHT + 100]
            # Füge neue Dekorationen oben hinzu
            max_y = max([d['y'] for d in self.decorations], default=-200)
            y_pos = max_y - random.randint(40, 80)
            while y_pos > -200:
                # Linke Seite
                if random.random() < 0.7:
                    decor_type = random.choice(['tree', 'bush', 'flowers'])
                    x_offset = random.randint(20, 80)
                    if decor_type == 'tree':
                        size = random.randint(20, 35)
                        self.decorations.append({'type': 'tree', 'x': -x_offset, 'y': y_pos, 'size': size})
                    elif decor_type == 'bush':
                        size = random.randint(15, 25)
                        self.decorations.append({'type': 'bush', 'x': -x_offset, 'y': y_pos, 'size': size})
                    else:
                        color = random.choice(Config.DECORATION_FLOWER_COLORS)
                        self.decorations.append({'type': 'flowers', 'x': -x_offset, 'y': y_pos, 'color': color})
                
                # Rechte Seite
                if random.random() < 0.7:
                    decor_type = random.choice(['tree', 'bush', 'flowers'])
                    x_offset = random.randint(20, 80)
                    road_right = Config.ROAD_X + Config.ROAD_WIDTH
                    if decor_type == 'tree':
                        size = random.randint(20, 35)
                        self.decorations.append({'type': 'tree', 'x': road_right + x_offset, 'y': y_pos, 'size': size})
                    elif decor_type == 'bush':
                        size = random.randint(15, 25)
                        self.decorations.append({'type': 'bush', 'x': road_right + x_offset, 'y': y_pos, 'size': size})
                    else:
                        color = random.choice(Config.DECORATION_FLOWER_COLORS)
                        self.decorations.append({'type': 'flowers', 'x': road_right + x_offset, 'y': y_pos, 'color': color})
                
                y_pos -= random.randint(40, 80)
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the road with all markings"""
        # Draw grass background
        screen.fill(Config.COLOR_GRASS)
        
        # Draw decorations (trees, bushes, flowers) on both sides
        for decor in self.decorations:
            if decor['type'] == 'tree':
                # Draw tree trunk
                trunk_width = decor['size'] // 4
                trunk_height = decor['size'] // 2
                trunk_x = decor['x'] - trunk_width // 2
                trunk_y = decor['y'] + decor['size'] // 2
                pygame.draw.rect(screen, Config.DECORATION_TREE_TRUNK_COLOR, 
                               (trunk_x, trunk_y, trunk_width, trunk_height))
                # Draw tree crown (circle)
                pygame.draw.circle(screen, Config.DECORATION_TREE_COLOR, 
                                 (decor['x'], decor['y']), decor['size'] // 2)
            elif decor['type'] == 'bush':
                # Draw bush (ellipse-like shape using circle)
                pygame.draw.circle(screen, Config.DECORATION_BUSH_COLOR, 
                                 (decor['x'], decor['y']), decor['size'] // 2)
                pygame.draw.circle(screen, Config.DECORATION_BUSH_COLOR, 
                                 (decor['x'] - decor['size'] // 4, decor['y'] + 5), decor['size'] // 3)
                pygame.draw.circle(screen, Config.DECORATION_BUSH_COLOR, 
                                 (decor['x'] + decor['size'] // 4, decor['y'] + 5), decor['size'] // 3)
            elif decor['type'] == 'flowers':
                # Draw flower patch
                flower_radius = 4
                offsets = [(-8, -5), (0, -8), (8, -5), (-6, 5), (6, 5)]
                for ox, oy in offsets:
                    pygame.draw.circle(screen, decor['color'], 
                                     (decor['x'] + ox, decor['y'] + oy), flower_radius)
        
        # Draw road surface
        road_rect = pygame.Rect(Config.ROAD_X, 0, Config.ROAD_WIDTH, Config.WINDOW_HEIGHT)
        pygame.draw.rect(screen, Config.COLOR_ROAD, road_rect)
        
        # Draw left and right borders (solid white lines)
        pygame.draw.line(screen, Config.COLOR_LINE_WHITE, 
                        (Config.ROAD_X, 0), 
                        (Config.ROAD_X, Config.WINDOW_HEIGHT), 4)
        pygame.draw.line(screen, Config.COLOR_LINE_WHITE,
                        (Config.ROAD_X + Config.ROAD_WIDTH, 0),
                        (Config.ROAD_X + Config.ROAD_WIDTH, Config.WINDOW_HEIGHT), 4)
        
        # Draw dashed lane markers
        dash_length = 40
        gap_length = 40
        total_cycle = dash_length + gap_length
        
        for lane in range(1, Config.NUM_LANES):
            x = Config.ROAD_X + lane * Config.LANE_WIDTH
            # Start drawing from above the screen to ensure continuous appearance
            start_y = -total_cycle + self.line_offset
            while start_y < Config.WINDOW_HEIGHT:
                pygame.draw.line(screen, Config.COLOR_LINE_WHITE,
                               (x, start_y),
                               (x, start_y + dash_length), 3)
                start_y += total_cycle
        
        # Draw guide posts on grass strips (optional decoration)
        post_width = 8
        post_height = 30
        post_x_left = Config.ROAD_X - 30
        post_x_right = Config.ROAD_X + Config.ROAD_WIDTH + 22
        
        start_post_y = -post_height + self.post_offset
        while start_post_y < Config.WINDOW_HEIGHT:
            # Left posts (red and white stripes simulated with alternating colors)
            post_color = Config.COLOR_LINE_WHITE if (int(start_post_y / 100) % 2 == 0) else (200, 50, 50)
            pygame.draw.rect(screen, post_color, 
                           (post_x_left, start_post_y, post_width, post_height))
            pygame.draw.rect(screen, post_color,
                           (post_x_right, start_post_y, post_width, post_height))
            start_post_y += 100


# =============================================================================
# PLAYER CLASS
# =============================================================================
class Player:
    def __init__(self):
        self.current_lane = Config.NUM_LANES // 2  # Start in middle lane
        self.target_lane = self.current_lane
        self.lane_change_progress = 0.0
        self.is_changing_lane = False
        
        # Calculate center X positions for each lane (dynamically based on NUM_LANES)
        self.lane_center_x = [
            Config.ROAD_X + Config.LANE_WIDTH * lane + Config.LANE_WIDTH // 2
            for lane in range(Config.NUM_LANES)
        ]
        
        # Current X position (starts at middle lane center)
        self.x = self.lane_center_x[self.current_lane]
        self.y = Config.PLAYER_Y
        
        # For tank event - automatic movement
        self.auto_move_active = False
        self.auto_move_target_x = None
        self.auto_move_target_y = None
        self.auto_move_start_x = None
        self.auto_move_start_y = None
        self.auto_move_duration = 0.0
        self.auto_move_elapsed = 0.0
        
    def handle_input(self, keys: pygame.key.ScancodeWrapper, input_enabled: bool = True) -> None:
        """Handle player input for lane changes"""
        if not input_enabled:
            return
        if self.is_changing_lane or self.auto_move_active:
            return
            
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self._try_lane_change(-1)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self._try_lane_change(1)
            
    def _try_lane_change(self, direction: int) -> None:
        """Initiate a lane change if possible"""
        new_lane = self.current_lane + direction
        if 0 <= new_lane < Config.NUM_LANES:
            self.target_lane = new_lane
            self.is_changing_lane = True
            self.lane_change_progress = 0.0
            
    def start_auto_move_to_center(self, duration: float, target_y: float) -> None:
        """Start automatic movement to center lane and target Y position"""
        self.auto_move_active = True
        self.auto_move_start_x = self.x
        self.auto_move_start_y = self.y
        self.auto_move_target_x = self.lane_center_x[Config.NUM_LANES // 2]
        self.auto_move_target_y = target_y
        self.auto_move_duration = duration
        self.auto_move_elapsed = 0.0
        
    def update_auto_move(self, dt: float) -> bool:
        """Update automatic movement. Returns True when complete."""
        if not self.auto_move_active:
            return True
            
        self.auto_move_elapsed += dt
        progress = min(self.auto_move_elapsed / self.auto_move_duration, 1.0)
        
        # Smooth easing
        eased = progress * progress * (3 - 2 * progress)
        
        self.x = self.auto_move_start_x + (self.auto_move_target_x - self.auto_move_start_x) * eased
        self.y = self.auto_move_start_y + (self.auto_move_target_y - self.auto_move_start_y) * eased
        
        if progress >= 1.0:
            self.auto_move_active = False
            self.current_lane = Config.NUM_LANES // 2
            return True
        return False
            
    def update(self, dt: float) -> None:
        """Update player state and lane change animation"""
        if self.auto_move_active:
            self.update_auto_move(dt)
            return
            
        if self.is_changing_lane:
            self.lane_change_progress += dt / Config.LANE_CHANGE_DURATION
            
            if self.lane_change_progress >= 1.0:
                # Lane change complete
                self.current_lane = self.target_lane
                self.lane_change_progress = 0.0
                self.is_changing_lane = False
                self.x = self.lane_center_x[self.current_lane]
            else:
                # Linear interpolation for lane change
                start_x = self.lane_center_x[self.current_lane]
                end_x = self.lane_center_x[self.target_lane]
                # Ease-in-out for smoother animation
                t = self.lane_change_progress
                eased_t = t * t * (3 - 2 * t)  # Smoothstep
                self.x = start_x + (end_x - start_x) * eased_t
                
    def get_hitbox(self) -> pygame.Rect:
        """Get the player's hitbox (smaller than visual sprite)"""
        reduction = Config.PLAYER_WIDTH * Config.HITBOX_REDUCTION
        width = Config.PLAYER_WIDTH - 2 * reduction
        height = Config.PLAYER_HEIGHT - 2 * reduction
        x = self.x - width // 2
        y = self.y - height // 2
        return pygame.Rect(x, y, width, height)
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the player car with headlights during night"""
        # Main body (rounded rectangle approximation)
        body_rect = pygame.Rect(
            self.x - Config.PLAYER_WIDTH // 2,
            self.y - Config.PLAYER_HEIGHT // 2,
            Config.PLAYER_WIDTH,
            Config.PLAYER_HEIGHT
        )
        
        # Draw rounded corners by drawing ellipse-based shape
        pygame.draw.rect(screen, Config.COLOR_PLAYER, body_rect, border_radius=10)
        
        # Windshield (lighter rectangle at top)
        windshield_rect = pygame.Rect(
            self.x - Config.PLAYER_WIDTH // 2 + 5,
            self.y - Config.PLAYER_HEIGHT // 2 + 10,
            Config.PLAYER_WIDTH - 10,
            20
        )
        pygame.draw.rect(screen, Config.COLOR_PLAYER_WINDSHIELD, windshield_rect, border_radius=5)
        
        # Rear window
        rear_window_rect = pygame.Rect(
            self.x - Config.PLAYER_WIDTH // 2 + 8,
            self.y + Config.PLAYER_HEIGHT // 2 - 18,
            Config.PLAYER_WIDTH - 16,
            12
        )
        pygame.draw.rect(screen, Config.COLOR_PLAYER_WINDSHIELD, rear_window_rect, border_radius=3)
        
        # Wheels (4 small rectangles at corners)
        wheel_width = 8
        wheel_height = 12
        wheel_positions = [
            (self.x - Config.PLAYER_WIDTH // 2 - 2, self.y - Config.PLAYER_HEIGHT // 2 + 10),
            (self.x + Config.PLAYER_WIDTH // 2 - wheel_width + 2, self.y - Config.PLAYER_HEIGHT // 2 + 10),
            (self.x - Config.PLAYER_WIDTH // 2 - 2, self.y + Config.PLAYER_HEIGHT // 2 - wheel_height - 10),
            (self.x + Config.PLAYER_WIDTH // 2 - wheel_width + 2, self.y + Config.PLAYER_HEIGHT // 2 - wheel_height - 10),
        ]
        
        for wx, wy in wheel_positions:
            pygame.draw.rect(screen, Config.COLOR_PLAYER_WHEEL,
                           (wx, wy, wheel_width, wheel_height), border_radius=3)
        
        # Draw headlights (always on, visible during night)
        headlight_left = pygame.Rect(
            self.x - Config.PLAYER_WIDTH // 2 + 8,
            self.y - Config.PLAYER_HEIGHT // 2 - 2,
            10, 5
        )
        headlight_right = pygame.Rect(
            self.x + Config.PLAYER_WIDTH // 2 - 18,
            self.y - Config.PLAYER_HEIGHT // 2 - 2,
            10, 5
        )
        pygame.draw.rect(screen, (255, 255, 200), headlight_left)
        pygame.draw.rect(screen, (255, 255, 200), headlight_right)


# =============================================================================
# ENEMY CLASS
# =============================================================================
class Enemy:
    TYPE_CAR = "car"
    TYPE_TRUCK = "truck"
    TYPE_VAN = "van"
    TYPE_TRACTOR = "tractor"
    TYPE_MOPED = "moped"
    
    def __init__(self, lane: int, enemy_type: str, spawn_y: float = -150):
        self.lane = lane
        self.enemy_type = enemy_type
        
        # Set dimensions based on type
        if enemy_type == self.TYPE_TRUCK:
            self.width = Config.ENEMY_TRUCK_WIDTH
            self.height = Config.ENEMY_TRUCK_HEIGHT
            self.color = Config.COLOR_ENEMY_TRUCK
        elif enemy_type == self.TYPE_VAN:
            self.width = Config.ENEMY_VAN_WIDTH
            self.height = Config.ENEMY_VAN_HEIGHT
            self.color = Config.COLOR_ENEMY_VAN
        elif enemy_type == self.TYPE_TRACTOR:
            self.width = Config.ENEMY_TRACTOR_WIDTH
            self.height = Config.ENEMY_TRACTOR_HEIGHT
            self.color = Config.COLOR_ENEMY_TRACTOR
        elif enemy_type == self.TYPE_MOPED:
            self.width = Config.ENEMY_MOPED_WIDTH
            self.height = Config.ENEMY_MOPED_HEIGHT
            self.color = Config.COLOR_ENEMY_MOPED
        else:
            self.width = Config.ENEMY_CAR_WIDTH
            self.height = Config.ENEMY_CAR_HEIGHT
            self.color = Config.COLOR_ENEMY_CAR
            
        # Calculate center X position for the lane
        self.x = Config.ROAD_X + lane * Config.LANE_WIDTH + Config.LANE_WIDTH // 2
        self.y = spawn_y
        
        # Autonomous lane change properties
        self.is_changing_lane = False
        self.lane_change_progress = 0.0
        self.target_lane = lane
        self.lane_change_start_x = self.x
        self.lane_change_end_x = self.x
        
    def update(self, dt: float, speed: float, player_y: float = None) -> None:
        """Move enemy downward with the road scroll speed and handle autonomous lane changes"""
        self.y += speed * dt
        
        # Autonomous lane change logic (only if enabled and car is ahead of player)
        if Config.AUTONOMOUS_LANE_CHANGE_ENABLED and player_y is not None:
            # Check if car is within detection range (2 car lengths ahead of player)
            detection_distance = Config.AUTONOMOUS_LANE_CHANGE_DISTANCE * self.height
            if self.y > player_y - detection_distance and self.y < player_y:
                # Car is in detection zone - may attempt lane change
                if not self.is_changing_lane and random.random() < Config.AUTONOMOUS_LANE_CHANGE_CHANCE:
                    # Try to change to adjacent lane
                    if self.lane > 0:
                        self._start_lane_change(self.lane - 1)
                    elif self.lane < Config.NUM_LANES - 1:
                        self._start_lane_change(self.lane + 1)
        
        # Update lane change animation
        if self.is_changing_lane:
            self.lane_change_progress += dt / Config.AUTONOMOUS_LANE_CHANGE_DURATION
            if self.lane_change_progress >= 1.0:
                # Lane change complete
                self.lane = self.target_lane
                self.x = self.lane_change_end_x
                self.is_changing_lane = False
                self.lane_change_progress = 0.0
            else:
                # Smooth interpolation
                t = self.lane_change_progress
                eased_t = t * t * (3 - 2 * t)  # Smoothstep
                self.x = self.lane_change_start_x + (self.lane_change_end_x - self.lane_change_start_x) * eased_t
    
    def _start_lane_change(self, target_lane: int) -> None:
        """Start a lane change animation"""
        self.target_lane = target_lane
        self.is_changing_lane = True
        self.lane_change_progress = 0.0
        self.lane_change_start_x = self.x
        self.lane_change_end_x = Config.ROAD_X + target_lane * Config.LANE_WIDTH + Config.LANE_WIDTH // 2
        
    def is_off_screen(self) -> bool:
        """Check if enemy has passed the bottom of the screen"""
        return self.y > Config.WINDOW_HEIGHT + self.height
        
    def get_hitbox(self) -> pygame.Rect:
        """Get the enemy's hitbox (smaller than visual sprite)"""
        reduction_x = self.width * Config.HITBOX_REDUCTION
        reduction_y = self.height * Config.HITBOX_REDUCTION
        width = self.width - 2 * reduction_x
        height = self.height - 2 * reduction_y
        x = self.x - width // 2
        y = self.y - height // 2
        return pygame.Rect(x, y, width, height)
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the enemy vehicle"""
        # Main body
        body_rect = pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )
        pygame.draw.rect(screen, self.color, body_rect, border_radius=8)
        
        # Type-specific rendering
        if self.enemy_type == self.TYPE_TRUCK:
            # Truck has larger windshield at bottom (since it's coming toward us)
            windshield_rect = pygame.Rect(
                self.x - self.width // 2 + 5,
                self.y + self.height // 2 - 25,
                self.width - 10,
                18
            )
            pygame.draw.rect(screen, Config.COLOR_ENEMY_WINDSHIELD, windshield_rect, border_radius=3)
            
            # Truck cargo box lines
            cargo_line_y = self.y - self.height // 2 + 30
            while cargo_line_y < self.y + self.height // 2 - 25:
                pygame.draw.line(screen, (150, 100, 0),
                               (self.x - self.width // 2 + 5, cargo_line_y),
                               (self.x + self.width // 2 - 5, cargo_line_y), 2)
                cargo_line_y += 20
                
        elif self.enemy_type == self.TYPE_VAN:
            # Van has rear doors pattern
            windshield_rect = pygame.Rect(
                self.x - self.width // 2 + 5,
                self.y + self.height // 2 - 20,
                self.width - 10,
                15
            )
            pygame.draw.rect(screen, Config.COLOR_ENEMY_WINDSHIELD, windshield_rect, border_radius=3)
            
            # Van door lines
            center_line_y = self.y - self.height // 2 + self.height // 2
            pygame.draw.line(screen, (100, 80, 150),
                           (self.x, self.y - self.height // 2 + 10),
                           (self.x, self.y + self.height // 2 - 10), 2)
                           
        elif self.enemy_type == self.TYPE_TRACTOR:
            # Tractor has large rear wheels and small front wheels
            # Rear wheels (larger)
            rear_wheel_width = 8
            rear_wheel_height = 16
            rear_wheel_positions = [
                (self.x - self.width // 2 - 4, self.y + self.height // 2 - 20),
                (self.x + self.width // 2 - rear_wheel_width + 4, self.y + self.height // 2 - 20),
            ]
            for wx, wy in rear_wheel_positions:
                pygame.draw.rect(screen, Config.COLOR_PLAYER_WHEEL,
                               (wx, wy, rear_wheel_width, rear_wheel_height), border_radius=4)
            
            # Front wheels (smaller)
            front_wheel_width = 6
            front_wheel_height = 10
            front_wheel_positions = [
                (self.x - self.width // 2 - 2, self.y - self.height // 2 + 15),
                (self.x + self.width // 2 - front_wheel_width + 2, self.y - self.height // 2 + 15),
            ]
            for wx, wy in front_wheel_positions:
                pygame.draw.rect(screen, Config.COLOR_PLAYER_WHEEL,
                               (wx, wy, front_wheel_width, front_wheel_height), border_radius=2)
            
            # Tractor cabin
            cabin_rect = pygame.Rect(
                self.x - self.width // 2 + 8,
                self.y - self.height // 2 + 10,
                self.width - 16,
                30
            )
            pygame.draw.rect(screen, (40, 100, 30), cabin_rect, border_radius=5)
            
        elif self.enemy_type == self.TYPE_MOPED:
            # Moped is small with single headlight
            headlight_rect = pygame.Rect(
                self.x - 4,
                self.y + self.height // 2 - 12,
                8,
                8
            )
            pygame.draw.circle(screen, (255, 255, 200), 
                             (int(self.x), int(self.y + self.height // 2 - 8)), 4)
            
            # Handlebars
            pygame.draw.line(screen, Config.COLOR_PLAYER_WHEEL,
                           (self.x - self.width // 2 + 5, self.y + self.height // 2 - 15),
                           (self.x + self.width // 2 - 5, self.y + self.height // 2 - 15), 3)
            
            # Small wheels
            wheel_width = 4
            wheel_height = 8
            wheel_positions = [
                (self.x - self.width // 2 - 2, self.y - self.height // 2 + 10),
                (self.x + self.width // 2 - wheel_width + 2, self.y - self.height // 2 + 10),
            ]
            for wx, wy in wheel_positions:
                pygame.draw.rect(screen, Config.COLOR_PLAYER_WHEEL,
                               (wx, wy, wheel_width, wheel_height), border_radius=2)
            
            # Rider silhouette (simple circle)
            pygame.draw.circle(screen, (50, 50, 50),
                             (int(self.x), int(self.y - self.height // 2 + 15)), 6)
        else:
            # Car windshield at bottom
            windshield_rect = pygame.Rect(
                self.x - self.width // 2 + 5,
                self.y + self.height // 2 - 20,
                self.width - 10,
                15
            )
            pygame.draw.rect(screen, Config.COLOR_ENEMY_WINDSHIELD, windshield_rect, border_radius=3)
            
            # Standard car wheels
            wheel_width = 6
            wheel_height = 10
            wheel_positions = [
                (self.x - self.width // 2 - 2, self.y - self.height // 2 + 12),
                (self.x + self.width // 2 - wheel_width + 2, self.y - self.height // 2 + 12),
                (self.x - self.width // 2 - 2, self.y + self.height // 2 - wheel_height - 12),
                (self.x + self.width // 2 - wheel_width + 2, self.y + self.height // 2 - wheel_height - 12),
            ]
            for wx, wy in wheel_positions:
                pygame.draw.rect(screen, Config.COLOR_PLAYER_WHEEL,
                               (wx, wy, wheel_width, wheel_height), border_radius=2)


# =============================================================================
# ENEMY SPAWNER CLASS
# =============================================================================
class EnemySpawner:
    def __init__(self):
        self.spawn_timer = 0.0
        self.enemies: List[Enemy] = []
        self.last_spawn_positions: dict = {}  # lane -> y position of last spawn
        
    def update(self, dt: float, speed: float, elapsed_time: float) -> List[Enemy]:
        """Update spawner and potentially spawn new enemies"""
        self.spawn_timer += dt
        
        # Calculate current spawn interval based on speed
        spawn_interval = get_spawn_interval(speed)
        
        newly_spawned = []
        
        if self.spawn_timer >= spawn_interval:
            self.spawn_timer = 0.0
            enemies = self._try_spawn_multiple(speed, elapsed_time)
            for enemy in enemies:
                self.enemies.append(enemy)
                newly_spawned.append(enemy)
                
        return newly_spawned
    
    def _try_spawn_multiple(self, speed: float, elapsed_time: float) -> List[Enemy]:
        """Try to spawn one or multiple enemies side by side"""
        
        # Determine how many cars to spawn based on NUM_LANES
        # Must always leave at least 1 free lane (or NUM_LANES-2 for >=4 lanes)
        min_free_lanes = max(1, Config.NUM_LANES - 2) if Config.NUM_LANES >= 4 else 1
        max_spawn_count = len(range(Config.NUM_LANES)) - min_free_lanes
        
        # Weighted random for spawn count
        rand = random.random()
        if rand < 0.55:  # 55% chance for 1 car
            count = 1
        elif rand < 0.85:  # 30% chance for 2 cars
            count = 2
        else:  # 15% chance for 3 cars
            count = 3
            
        # Limit count to what's possible with free lane requirement
        count = min(count, max_spawn_count, Config.NUM_LANES)
        
        # Calculate minimum spawn Y to ensure reaction time
        min_reaction_distance = speed * Config.MIN_REACTION_TIME
        spawn_y = -min_reaction_distance - 50  # Spawn above screen with buffer
        
        # Find available lanes (not blocked in top zone)
        available_lanes = []
        
        for lane in range(Config.NUM_LANES):
            # Check if this lane is blocked in the top zone
            is_blocked = False
            
            for enemy in self.enemies:
                if enemy.lane == lane and enemy.y < Config.TOP_BLOCKED_ZONE_Y:
                    is_blocked = True
                    break
                    
            if not is_blocked:
                available_lanes.append(lane)
        
        # Must have at least one free lane in top zone
        if len(available_lanes) == 0:
            return []
        
        # Also check minimum distance on same lane
        valid_lanes = []
        for lane in available_lanes:
            is_valid = True
            
            for enemy in self.enemies:
                if enemy.lane == lane:
                    # Check if last spawned enemy on this lane is far enough
                    if enemy.y < Config.MIN_SPAWN_DISTANCE_SAME_LANE + abs(spawn_y):
                        is_valid = False
                        break
                        
            if is_valid:
                valid_lanes.append(lane)
        
        if len(valid_lanes) == 0:
            return []
        
        # Limit count to available valid lanes
        actual_count = min(count, len(valid_lanes))
        
        # Choose random lanes for spawning
        chosen_lanes = random.sample(valid_lanes, actual_count)
        
        # Spawn enemies on chosen lanes with configurable type probabilities
        spawned_enemies = []
        for lane in chosen_lanes:
            # Choose enemy type based on config probabilities
            rand_type = random.random()
            if rand_type < Config.SPAWN_CHANCE_CAR:
                enemy_type = Enemy.TYPE_CAR
            elif rand_type < Config.SPAWN_CHANCE_CAR + Config.SPAWN_CHANCE_TRUCK:
                enemy_type = Enemy.TYPE_TRUCK
            elif rand_type < Config.SPAWN_CHANCE_CAR + Config.SPAWN_CHANCE_TRUCK + Config.SPAWN_CHANCE_VAN:
                enemy_type = Enemy.TYPE_VAN
            elif rand_type < Config.SPAWN_CHANCE_CAR + Config.SPAWN_CHANCE_TRUCK + Config.SPAWN_CHANCE_VAN + Config.SPAWN_CHANCE_TRACTOR:
                enemy_type = Enemy.TYPE_TRACTOR
            else:
                enemy_type = Enemy.TYPE_MOPED
                
            enemy = Enemy(lane, enemy_type, spawn_y)
            self.last_spawn_positions[lane] = spawn_y
            spawned_enemies.append(enemy)
        
        return spawned_enemies
    
    def _try_spawn(self, speed: float, elapsed_time: float) -> Optional[Enemy]:
        """Try to spawn a new enemy following all rules (legacy method)"""
        # Calculate minimum spawn Y to ensure reaction time
        min_reaction_distance = speed * Config.MIN_REACTION_TIME
        spawn_y = -min_reaction_distance - 50  # Spawn above screen with buffer
        
        # Find available lanes (not blocked in top zone)
        available_lanes = []
        
        for lane in range(Config.NUM_LANES):
            # Check if this lane is blocked in the top zone
            is_blocked = False
            
            for enemy in self.enemies:
                if enemy.lane == lane and enemy.y < Config.TOP_BLOCKED_ZONE_Y:
                    is_blocked = True
                    break
                    
            if not is_blocked:
                available_lanes.append(lane)
                
        # Must have at least one free lane in top zone
        if len(available_lanes) == 0:
            return None
            
        # Also check minimum distance on same lane
        valid_lanes = []
        for lane in available_lanes:
            is_valid = True
            
            for enemy in self.enemies:
                if enemy.lane == lane:
                    # Check if last spawned enemy on this lane is far enough
                    if enemy.y < Config.MIN_SPAWN_DISTANCE_SAME_LANE + abs(spawn_y):
                        is_valid = False
                        break
                        
            if is_valid:
                valid_lanes.append(lane)
                
        if len(valid_lanes) == 0:
            return None
            
        # Choose a random valid lane
        chosen_lane = random.choice(valid_lanes)
        
        # Choose enemy type (20% chance for truck)
        enemy_type = Enemy.TYPE_TRUCK if random.random() < 0.2 else Enemy.TYPE_CAR
        
        enemy = Enemy(chosen_lane, enemy_type, spawn_y)
        self.last_spawn_positions[chosen_lane] = spawn_y
        
        return enemy
        
    def update_enemies(self, dt: float, speed: float, player_y: float = None) -> None:
        """Update all enemies and remove off-screen ones"""
        for enemy in self.enemies[:]:
            enemy.update(dt, speed, player_y)
            if enemy.is_off_screen():
                self.enemies.remove(enemy)
                
    def clear(self) -> None:
        """Clear all enemies"""
        self.enemies.clear()
        self.spawn_timer = 0.0
        self.last_spawn_positions.clear()


# =============================================================================
# TANK CLASS (for tank event)
# =============================================================================
class Tank:
    def __init__(self):
        self.width = Config.TANK_W
        self.height = Config.TANK_H
        self.x = Config.ROAD_X + Config.ROAD_WIDTH // 2  # Center of road
        self.y = Config.WINDOW_HEIGHT + self.height  # Start below screen
        self.target_y = Config.WINDOW_HEIGHT - 100  # Target position
        self.move_speed = Config.TANK_SPEED
        self.fire_timer = 0.0
        self.active = False
        
    def update(self, dt: float) -> None:
        """Move tank upward to target position"""
        if not self.active:
            return
            
        if self.y > self.target_y:
            self.y -= self.move_speed * dt
            
    def can_fire(self) -> bool:
        """Check if tank can fire"""
        return self.active and self.y <= self.target_y
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the tank"""
        # Main body
        body_rect = pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )
        pygame.draw.rect(screen, Config.TANK_COLOR, body_rect, border_radius=8)
        
        # Tank turret (circle on top)
        turret_rect = pygame.Rect(
            self.x - self.width // 4,
            self.y - self.height // 2 - 15,
            self.width // 2,
            30
        )
        pygame.draw.rect(screen, (50, 70, 40), turret_rect, border_radius=5)
        
        # Tank barrel
        barrel_rect = pygame.Rect(
            self.x - 8,
            self.y - self.height // 2 - 40,
            16,
            35
        )
        pygame.draw.rect(screen, (40, 60, 30), barrel_rect)
        
        # Tank tracks
        track_width = 15
        pygame.draw.rect(screen, (30, 30, 30),
                        (self.x - self.width // 2 - track_width, self.y - self.height // 2 + 10,
                         track_width, self.height - 20))
        pygame.draw.rect(screen, (30, 30, 30),
                        (self.x + self.width // 2, self.y - self.height // 2 + 10,
                         track_width, self.height - 20))


# =============================================================================
# BULLET CLASS (tank projectiles)
# =============================================================================
class Bullet:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.width = Config.BULLET_W
        self.height = Config.BULLET_H
        self.active = True
        
    def update(self, dt: float) -> None:
        """Move bullet upward"""
        self.y -= Config.BULLET_SPEED * dt
        
    def is_off_screen(self) -> bool:
        """Check if bullet is off screen"""
        return self.y < -self.height
        
    def get_hitbox(self) -> pygame.Rect:
        """Get bullet hitbox"""
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the bullet"""
        pygame.draw.rect(screen, Config.BULLET_COLOR,
                        (self.x - self.width // 2, self.y - self.height // 2,
                         self.width, self.height), border_radius=3)


# =============================================================================
# WALL CLASS (ramp wall for tank event)
# =============================================================================
class Wall:
    def __init__(self):
        self.height = Config.WALL_H
        self.width = Config.ROAD_WIDTH
        self.x = Config.ROAD_X
        self.y = -self.height  # Start above screen
        self.active = False
        self.speed_factor = Config.WALL_APPROACH_SPEED_FACTOR
        
    def update(self, dt: float, game_speed: float) -> None:
        """Move wall downward"""
        if self.active:
            self.y += game_speed * self.speed_factor * dt
            
    def is_off_screen(self) -> bool:
        """Check if wall is off screen"""
        return self.y > Config.WINDOW_HEIGHT
        
    def get_ramp_rect(self) -> pygame.Rect:
        """Get the ramp area rectangle"""
        ramp_x = self.x + (self.width - Config.RAMP_W) // 2
        return pygame.Rect(ramp_x, self.y, Config.RAMP_W, self.height)
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the wall with ramp"""
        # Draw main wall
        pygame.draw.rect(screen, Config.WALL_COLOR,
                        (self.x, self.y, self.width, self.height))
        
        # Draw ramp (triangle shape in the middle)
        ramp_x = self.x + (self.width - Config.RAMP_W) // 2
        ramp_points = [
            (ramp_x, self.y + self.height),  # Bottom left
            (ramp_x + Config.RAMP_W // 2, self.y),  # Top center
            (ramp_x + Config.RAMP_W, self.y + self.height)  # Bottom right
        ]
        pygame.draw.polygon(screen, Config.RAMP_COLOR, ramp_points)


# =============================================================================
# GAME CLASS
# =============================================================================
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Oncoming Rush")
        
        self.screen = pygame.Surface((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
        self.window = pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
        
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        
        # Load highscore
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.highscore_file = os.path.join(script_dir, Config.HIGHSCORE_FILE)
        self.highscore = load_highscore(self.highscore_file)
        
        # Game state
        self.state = GameState.MENU
        self.elapsed_time = 0.0
        self.current_speed = Config.BASE_SPEED
        
        # Game objects
        self.road = Road()
        self.player = Player()
        self.spawner = EnemySpawner()
        
        # Tank event objects and state
        self.tank = None
        self.bullets: List[Bullet] = []
        self.wall = None
        self.tank_event_phase = None
        self.tank_event_timer = 0.0
        self.last_tank_event_time = -Config.TANK_EVENT_COOLDOWN  # Allow first event after earliest time
        self.tank_announcement_text = ""
        self.tank_announcement_timer = 0.0
        self.jump_start_y = None
        self.jump_elapsed = 0.0
        self.event_escape_message = ""
        self.event_escape_timer = 0.0
        
        # For game over
        self.final_time = 0.0
        self.new_highscore = False
        
    def reset_game(self) -> None:
        """Reset game state for a new game"""
        self.elapsed_time = 0.0
        self.current_speed = Config.BASE_SPEED
        self.player = Player()
        self.spawner.clear()
        self._reset_tank_event()
        
    def _reset_tank_event(self) -> None:
        """Reset tank event state"""
        self.tank = None
        self.bullets = []
        self.wall = None
        self.tank_event_phase = None
        self.tank_event_timer = 0.0
        self.jump_start_y = None
        self.jump_elapsed = 0.0
        
    def _check_trigger_event(self, dt: float) -> bool:
        """Check if any event should be triggered (every 30 seconds)"""
        
        # Check cooldown and earliest time
        time_since_last = self.elapsed_time - self.last_tank_event_time
        if time_since_last < Config.EVENT_GLOBAL_COOLDOWN:
            return False
        if self.elapsed_time < Config.EVENT_EARLIEST:
            return False
        
        # Check if we're at a 30-second checkpoint
        prev_time = self.elapsed_time - dt
        prev_checkpoints = int(prev_time / Config.EVENT_CHECK_INTERVAL)
        curr_checkpoints = int(self.elapsed_time / Config.EVENT_CHECK_INTERVAL)
        
        if curr_checkpoints > prev_checkpoints:
            # We crossed a checkpoint boundary - roll for event
            if random.random() < Config.EVENT_TRIGGER_CHANCE:
                return True
        return False
    
    def _start_random_event(self) -> None:
        """Start a random event (tank, fog, EMP, or asteroid)"""
        
        # Choose event based on weights
        events = ['tank', 'fog', 'emp', 'asteroid']
        weights = [
            Config.EVENT_WEIGHT_TANK,
            Config.EVENT_WEIGHT_FOG,
            Config.EVENT_WEIGHT_EMP,
            Config.EVENT_WEIGHT_ASTEROID
        ]
        
        chosen_event = random.choices(events, weights=weights)[0]
        
        if chosen_event == 'tank':
            self._start_tank_event()
        elif chosen_event == 'fog':
            self._start_fog_event()
        elif chosen_event == 'emp':
            self._start_emp_event()
        elif chosen_event == 'asteroid':
            self._start_asteroid_event()
    
    def _check_trigger_tank_event(self, dt: float) -> bool:
        """Check if tank event should be triggered (legacy function)"""
        return self._check_trigger_event(dt)
        
    def _start_tank_event(self) -> None:
        """Start the tank event sequence"""
        self.tank_event_phase = TankEventPhase.TRIGGER_ANNOUNCEMENT
        self.tank_event_timer = 0.0
        self.tank_announcement_text = "⚠ ACHTUNG – PANZER!"
        self.tank_announcement_timer = 1.5
        
    def _update_tank_event(self, dt: float) -> None:
        """Update tank event logic"""
        if self.tank_event_phase is None:
            return
            
        # Phase 1: Trigger & Announcement
        if self.tank_event_phase == TankEventPhase.TRIGGER_ANNOUNCEMENT:
            self.tank_announcement_timer -= dt
            if self.tank_announcement_timer <= 0:
                # Move to phase 2
                self.tank_event_phase = TankEventPhase.MOVE_TO_CENTER
                self.tank_event_timer = 0.0
                self.player.start_auto_move_to_center(
                    Config.TANK_MOVE_TO_CENTER_DURATION,
                    Config.WINDOW_HEIGHT // 2
                )
                # Clear existing enemies
                self.spawner.clear()
                
        # Phase 2: Move to center
        elif self.tank_event_phase == TankEventPhase.MOVE_TO_CENTER:
            self.tank_event_timer += dt
            if self.player.update_auto_move(dt):
                # Movement complete, move to phase 3
                self.tank_event_phase = TankEventPhase.TANK_APPEARS
                self.tank_event_timer = 0.0
                self.tank = Tank()
                self.tank.active = True
                
        # Phase 3: Tank appears and fires
        elif self.tank_event_phase == TankEventPhase.TANK_APPEARS:
            self.tank_event_timer += dt
            if self.tank:
                self.tank.update(dt)
                
                # Tank fires periodically
                if self.tank.can_fire():
                    self.tank.fire_timer += dt
                    if self.tank.fire_timer >= Config.TANK_FIRE_INTERVAL:
                        self.tank.fire_timer = 0.0
                        # Spawn bullet
                        bullet = Bullet(self.tank.x, self.tank.y - self.tank.height // 2 - 10)
                        self.bullets.append(bullet)
                        
            # Update bullets
            for bullet in self.bullets[:]:
                bullet.update(dt)
                if bullet.is_off_screen():
                    self.bullets.remove(bullet)
                    
            # Check bullet collisions with player
            player_hitbox = self.player.get_hitbox()
            for bullet in self.bullets:
                if player_hitbox.colliderect(bullet.get_hitbox()):
                    self._game_over()
                    return
                    
            # Check if wall should appear
            if self.tank_event_timer >= Config.WALL_DELAY_AFTER_TANK:
                self.tank_event_phase = TankEventPhase.WALL_APPROACHING
                self.tank_event_timer = 0.0
                self.wall = Wall()
                self.wall.active = True
                
        # Phase 4: Wall approaching
        elif self.tank_event_phase == TankEventPhase.WALL_APPROACHING:
            self.tank_event_timer += dt
            if self.wall:
                self.wall.update(dt, self.current_speed)
                
            # Despawn enemies that collide with wall
            if self.wall:
                for enemy in self.spawner.enemies[:]:
                    enemy_rect = pygame.Rect(
                        enemy.x - enemy.width // 2,
                        enemy.y - enemy.height // 2,
                        enemy.width,
                        enemy.height
                    )
                    if enemy_rect.colliderect(pygame.Rect(self.wall.x, self.wall.y, self.wall.width, self.wall.height)):
                        self.spawner.enemies.remove(enemy)
                        
            # Check if player reached ramp
            if self.wall:
                player_rect = pygame.Rect(
                    self.player.x - Config.PLAYER_WIDTH // 2,
                    self.player.y - Config.PLAYER_HEIGHT // 2,
                    Config.PLAYER_WIDTH,
                    Config.PLAYER_HEIGHT
                )
                if player_rect.colliderect(self.wall.get_ramp_rect()):
                    # Start jump sequence
                    self.tank_event_phase = TankEventPhase.JUMP_SEQUENCE
                    self.jump_start_y = self.player.y
                    self.jump_elapsed = 0.0
                    
        # Phase 5: Jump sequence
        elif self.tank_event_phase == TankEventPhase.JUMP_SEQUENCE:
            self.jump_elapsed += dt
            
            if self.jump_elapsed <= Config.JUMP_DURATION:
                # Parabolic jump arc
                progress = self.jump_elapsed / Config.JUMP_DURATION
                # Arc: goes up then down
                arc_progress = 4 * progress * (1 - progress)  # Peaks at 0.5
                self.player.y = self.jump_start_y - arc_progress * Config.JUMP_ARC_HEIGHT
            else:
                # Jump complete
                self.player.y = self.jump_start_y
                self.tank_event_phase = TankEventPhase.RETURN_AND_END
                self.tank_event_timer = 0.0
                # Clear bullets
                self.bullets.clear()
                # Tank explodes (visual only - just remove it)
                self.tank = None
                
        # Phase 6: Return and end
        elif self.tank_event_phase == TankEventPhase.RETURN_AND_END:
            self.tank_event_timer += dt
            # Move player back to normal position
            target_y = Config.PLAYER_Y
            if abs(self.player.y - target_y) > 1:
                self.player.y += (target_y - self.player.y) * 5 * dt
            else:
                self.player.y = target_y
                # Event complete
                if self.tank_event_timer >= 0.5:
                    self.last_tank_event_time = self.elapsed_time
                    self.tank_event_phase = None
                    self.event_escape_message = "Entkommen!"
                    self.event_escape_timer = 2.0
                    # Wall continues scrolling off screen
        
    def handle_events(self) -> bool:
        """Handle pygame events. Returns False if should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_RETURN:
                        self.reset_game()
                        self.state = GameState.PLAYING
                        
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                        self.state = GameState.PAUSED
                        
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                        self.state = GameState.PLAYING
                        
                elif self.state == GameState.GAMEOVER:
                    if event.key == pygame.K_RETURN:
                        self.reset_game()
                        self.state = GameState.PLAYING
                        self.new_highscore = False
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU
                        
        return True
        
    def update(self, dt: float) -> None:
        """Update game logic"""
        if self.state != GameState.PLAYING:
            return
            
        # Update elapsed time
        self.elapsed_time += dt
        
        # Check for event trigger (every 30 seconds)
        if self.tank_event_phase is None and self._check_trigger_event(dt):
            self._start_random_event()
        
        # Update tank event if active
        if self.tank_event_phase is not None:
            self._update_tank_event(dt)
            # During tank event, normal spawning is paused in some phases
            if self.tank_event_phase in [TankEventPhase.TRIGGER_ANNOUNCEMENT, TankEventPhase.MOVE_TO_CENTER]:
                # No spawning during these phases
                pass
            else:
                # Normal spawning resumes after move to center
                self.spawner.update(dt, self.current_speed, self.elapsed_time)
        else:
            # Normal spawning
            self.spawner.update(dt, self.current_speed, self.elapsed_time)
        
        # Update speed based on elapsed time
        self.current_speed = get_current_speed(self.elapsed_time)
        
        # Update road
        self.road.update(dt, self.current_speed)
        
        # Handle player input and update (input disabled during some tank event phases)
        keys = pygame.key.get_pressed()
        input_enabled = (self.tank_event_phase is None or 
                        self.tank_event_phase in [TankEventPhase.TANK_APPEARS, TankEventPhase.WALL_APPROACHING])
        self.player.handle_input(keys, input_enabled)
        self.player.update(dt)
        
        # Update enemies with player position for autonomous lane changes
        self.spawner.update_enemies(dt, self.current_speed, self.player.y)
        
        # Update wall if active
        if self.wall and self.tank_event_phase is not None:
            if self.tank_event_phase == TankEventPhase.WALL_APPROACHING:
                self.wall.update(dt, self.current_speed)
            elif self.tank_event_phase in [TankEventPhase.JUMP_SEQUENCE, TankEventPhase.RETURN_AND_END]:
                self.wall.update(dt, self.current_speed)
                
        # Update escape message timer
        if self.event_escape_timer > 0:
            self.event_escape_timer -= dt
            
        # Check collisions with enemies
        player_hitbox = self.player.get_hitbox()
        for enemy in self.spawner.enemies:
            enemy_hitbox = enemy.get_hitbox()
            if player_hitbox.colliderect(enemy_hitbox):
                self._game_over()
                break
                
    def _game_over(self) -> None:
        """Handle game over"""
        self.state = GameState.GAMEOVER
        self.final_time = self.elapsed_time
        
        # Check for new highscore
        if int(self.final_time) > self.highscore:
            self.highscore = int(self.final_time)
            save_highscore(self.highscore_file, self.highscore)
            self.new_highscore = True
            
    def draw_menu(self) -> None:
        """Draw main menu"""
        self.screen.fill(Config.COLOR_GRASS)
        
        # Title
        title = self.font_large.render("ONCOMING RUSH", True, Config.COLOR_LINE_WHITE)
        title_rect = title.get_rect(center=(Config.WINDOW_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.font_medium.render("Endless Dodger", True, Config.COLOR_LINE_WHITE)
        subtitle_rect = subtitle.get_rect(center=(Config.WINDOW_WIDTH // 2, 260))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Controls
        controls = [
            "Controls:",
            "Arrow Keys or A/D - Change Lanes",
            "P or ESC - Pause",
        ]
        
        for i, text in enumerate(controls):
            surf = self.font_small.render(text, True, Config.COLOR_LINE_WHITE)
            rect = surf.get_rect(center=(Config.WINDOW_WIDTH // 2, 380 + i * 40))
            self.screen.blit(surf, rect)
            
        # Highscore
        hs_text = f"Highscore: {format_time(self.highscore)}"
        hs_surf = self.font_medium.render(hs_text, True, Config.COLOR_LINE_WHITE)
        hs_rect = hs_surf.get_rect(center=(Config.WINDOW_WIDTH // 2, 520))
        self.screen.blit(hs_surf, hs_rect)
        
        # Start prompt
        start_text = "Press ENTER to Start"
        start_surf = self.font_medium.render(start_text, True, Config.COLOR_LINE_WHITE)
        start_rect = start_surf.get_rect(center=(Config.WINDOW_WIDTH // 2, 620))
        self.screen.blit(start_surf, start_rect)
        
        # Scale to window
        scaled = pygame.transform.scale(self.screen, (Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
        self.window.blit(scaled, (0, 0))
        
    def draw_hud(self) -> None:
        """Draw HUD elements during gameplay"""
        # Survival time (top center)
        time_text = format_time(self.elapsed_time)
        time_surf = self.font_medium.render(time_text, True, Config.COLOR_HUD_TEXT)
        time_rect = time_surf.get_rect(center=(Config.WINDOW_WIDTH // 2, 30))
        self.screen.blit(time_surf, time_rect)
        
        # Highscore (top right)
        hs_text = f"Best: {format_time(self.highscore)}"
        hs_surf = self.font_small.render(hs_text, True, Config.COLOR_HUD_TEXT)
        hs_rect = hs_surf.get_rect(topright=(Config.WINDOW_WIDTH - 10, 10))
        self.screen.blit(hs_surf, hs_rect)
        
        # Level (top left)
        level = get_level(self.elapsed_time)
        level_text = f"Level {level}"
        level_surf = self.font_small.render(level_text, True, Config.COLOR_HUD_TEXT)
        level_rect = level_surf.get_rect(topleft=(10, 10))
        self.screen.blit(level_surf, level_rect)
        
        # Tank event banner during phases 3-5
        if self.tank_event_phase in [TankEventPhase.TANK_APPEARS, TankEventPhase.WALL_APPROACHING, TankEventPhase.JUMP_SEQUENCE]:
            # Red banner at top
            banner_rect = pygame.Rect(0, 50, Config.WINDOW_WIDTH, 40)
            pygame.draw.rect(self.screen, (180, 50, 50), banner_rect)
            banner_text = "⚠ PANZER-ANGRIFF"
            banner_surf = self.font_medium.render(banner_text, True, Config.COLOR_LINE_WHITE)
            banner_rect_text = banner_surf.get_rect(center=(Config.WINDOW_WIDTH // 2, 70))
            self.screen.blit(banner_surf, banner_rect_text)
            
            # Countdown during wall approaching phase
            if self.tank_event_phase == TankEventPhase.WALL_APPROACHING:
                remaining = max(0, Config.WALL_DELAY_AFTER_TANK - self.tank_event_timer)
                countdown_text = f"Mauer in: {remaining:.1f}s"
                countdown_surf = self.font_small.render(countdown_text, True, Config.COLOR_LINE_WHITE)
                countdown_rect = countdown_surf.get_rect(center=(Config.WINDOW_WIDTH // 2, 100))
                self.screen.blit(countdown_surf, countdown_rect)
        
        # Escape message after event
        if self.event_escape_timer > 0:
            escape_surf = self.font_medium.render(self.event_escape_message, True, (50, 200, 50))
            escape_rect = escape_surf.get_rect(center=(Config.WINDOW_WIDTH // 2, 100))
            self.screen.blit(escape_surf, escape_rect)
        
        # Announcement text during phase 1
        if self.tank_event_phase == TankEventPhase.TRIGGER_ANNOUNCEMENT and self.tank_announcement_timer > 0:
            announce_surf = self.font_large.render(self.tank_announcement_text, True, (255, 50, 50))
            announce_rect = announce_surf.get_rect(center=(Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT - 80))
            self.screen.blit(announce_surf, announce_rect)
        
        # Speedometer (bottom right - vertical bar)
        speed_ratio = (self.current_speed - Config.BASE_SPEED) / (Config.MAX_SPEED - Config.BASE_SPEED)
        bar_height = 100
        bar_width = 20
        bar_x = Config.WINDOW_WIDTH - 40
        bar_y = Config.WINDOW_HEIGHT - bar_height - 10
        
        # Background
        pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        
        # Fill bar based on speed
        fill_height = int(bar_height * speed_ratio)
        
        # Color gradient from green to red
        r = int(50 + 150 * speed_ratio)
        g = int(200 - 150 * speed_ratio)
        b = 50
        fill_color = (r, g, b)
        
        if fill_height > 0:
            pygame.draw.rect(self.screen, fill_color,
                           (bar_x, bar_y + bar_height - fill_height, bar_width, fill_height))
        
        # Border
        pygame.draw.rect(self.screen, Config.COLOR_LINE_WHITE,
                        (bar_x, bar_y, bar_width, bar_height), 2)
                        
        # Speed label
        speed_text = f"{int(self.current_speed)}"
        speed_surf = self.font_small.render(speed_text, True, Config.COLOR_HUD_TEXT)
        speed_rect = speed_surf.get_rect(center=(bar_x + bar_width // 2, bar_y - 10))
        self.screen.blit(speed_surf, speed_rect)
        
    def draw_pause(self) -> None:
        """Draw pause overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill(Config.COLOR_PAUSE_OVERLAY)
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = "PAUSE"
        pause_surf = self.font_large.render(pause_text, True, Config.COLOR_LINE_WHITE)
        pause_rect = pause_surf.get_rect(center=(Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT // 2 - 30))
        self.screen.blit(pause_surf, pause_rect)
        
        # Continue hint
        continue_text = "Press P or ESC to continue"
        continue_surf = self.font_small.render(continue_text, True, Config.COLOR_LINE_WHITE)
        continue_rect = continue_surf.get_rect(center=(Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT // 2 + 30))
        self.screen.blit(continue_surf, continue_rect)
        
    def draw_gameover(self) -> None:
        """Draw game over screen"""
        # Dark overlay
        overlay = pygame.Surface((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill(Config.COLOR_GAMEOVER_BG)
        self.screen.blit(overlay, (0, 0))
        
        # Game Over text
        go_text = "GAME OVER"
        go_surf = self.font_large.render(go_text, True, (255, 50, 50))
        go_rect = go_surf.get_rect(center=(Config.WINDOW_WIDTH // 2, 150))
        self.screen.blit(go_surf, go_rect)
        
        # Time survived
        time_label = "Time Survived:"
        time_label_surf = self.font_small.render(time_label, True, Config.COLOR_HUD_TEXT)
        time_label_rect = time_label_surf.get_rect(center=(Config.WINDOW_WIDTH // 2, 230))
        self.screen.blit(time_label_surf, time_label_rect)
        
        time_value = format_time(self.final_time)
        time_value_surf = self.font_medium.render(time_value, True, Config.COLOR_HUD_TEXT)
        time_value_rect = time_value_surf.get_rect(center=(Config.WINDOW_WIDTH // 2, 270))
        self.screen.blit(time_value_surf, time_value_rect)
        
        # Level reached
        level = get_level(self.final_time)
        level_text = f"Level Reached: {level}"
        level_surf = self.font_small.render(level_text, True, Config.COLOR_HUD_TEXT)
        level_rect = level_surf.get_rect(center=(Config.WINDOW_WIDTH // 2, 330))
        self.screen.blit(level_surf, level_rect)
        
        # Highscore display
        hs_label = "Highscore:"
        hs_label_surf = self.font_small.render(hs_label, True, Config.COLOR_HUD_TEXT)
        hs_label_rect = hs_label_surf.get_rect(center=(Config.WINDOW_WIDTH // 2, 390))
        self.screen.blit(hs_label_surf, hs_label_rect)
        
        hs_color = Config.COLOR_HIGHSCORE_NEW if self.new_highscore else Config.COLOR_HUD_TEXT
        hs_value = format_time(self.highscore)
        hs_value_surf = self.font_medium.render(hs_value, True, hs_color)
        hs_value_rect = hs_value_surf.get_rect(center=(Config.WINDOW_WIDTH // 2, 430))
        self.screen.blit(hs_value_surf, hs_value_rect)
        
        if self.new_highscore:
            new_hs_text = "New Highscore!"
            new_hs_surf = self.font_small.render(new_hs_text, True, Config.COLOR_HIGHSCORE_NEW)
            new_hs_rect = new_hs_surf.get_rect(center=(Config.WINDOW_WIDTH // 2, 470))
            self.screen.blit(new_hs_surf, new_hs_rect)
            
        # Restart prompt
        restart_text = "Press ENTER to Play Again"
        restart_surf = self.font_small.render(restart_text, True, Config.COLOR_HUD_TEXT)
        restart_rect = restart_surf.get_rect(center=(Config.WINDOW_WIDTH // 2, 550))
        self.screen.blit(restart_surf, restart_rect)
        
        # Menu prompt
        menu_text = "Press ESC for Menu"
        menu_surf = self.font_small.render(menu_text, True, Config.COLOR_HUD_TEXT)
        menu_rect = menu_surf.get_rect(center=(Config.WINDOW_WIDTH // 2, 590))
        self.screen.blit(menu_surf, menu_rect)
        
    def draw(self) -> None:
        """Draw everything"""
        # Always draw road first
        self.road.draw(self.screen)
        
        if self.state == GameState.MENU:
            self.draw_menu()
        else:
            # Draw enemies
            for enemy in self.spawner.enemies:
                enemy.draw(self.screen)
                
            # Draw player
            self.player.draw(self.screen)
            
            # Draw tank event objects
            if self.tank_event_phase is not None:
                # Draw tank
                if self.tank and self.tank.active:
                    self.tank.draw(self.screen)
                    
                # Draw bullets
                for bullet in self.bullets:
                    bullet.draw(self.screen)
                    
                # Draw wall
                if self.wall and (self.wall.active or self.tank_event_phase in [TankEventPhase.WALL_APPROACHING, TankEventPhase.JUMP_SEQUENCE, TankEventPhase.RETURN_AND_END]):
                    self.wall.draw(self.screen)
            
            # Draw HUD
            self.draw_hud()
            
            if self.state == GameState.PAUSED:
                self.draw_pause()
            elif self.state == GameState.GAMEOVER:
                self.draw_gameover()
                
        # Scale and display
        scaled = pygame.transform.scale(self.screen, (Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
        self.window.blit(scaled, (0, 0))
        pygame.display.flip()
        
    def run(self) -> None:
        """Main game loop"""
        running = True
        
        while running:
            dt = self.clock.tick(Config.FPS) / 1000.0  # Convert to seconds
            
            running = self.handle_events()
            self.update(dt)
            self.draw()
            
        pygame.quit()


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    game = Game()
    game.run()

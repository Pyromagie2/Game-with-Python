"""
Oncoming Rush - A 2D Top-Down Endless Dodger Game
Built with Pygame for Linux
"""

import pygame
import json
import os
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
    LANE_COUNT = 3
    LANE_WIDTH = ROAD_WIDTH // LANE_COUNT
    
    # Colors
    COLOR_GRASS = (34, 139, 34)
    COLOR_ROAD = (50, 50, 50)
    COLOR_LINE_WHITE = (255, 255, 255)
    COLOR_PLAYER = (50, 100, 200)
    COLOR_PLAYER_WINDSHIELD = (150, 200, 255)
    COLOR_PLAYER_WHEEL = (30, 30, 30)
    COLOR_ENEMY_CAR = (200, 50, 50)
    COLOR_ENEMY_TRUCK = (200, 150, 50)
    COLOR_ENEMY_WINDSHIELD = (100, 100, 100)
    COLOR_HUD_TEXT = (255, 255, 255)
    COLOR_SPEEDOMETER_LOW = (50, 200, 50)
    COLOR_SPEEDOMETER_HIGH = (200, 50, 50)
    COLOR_PAUSE_OVERLAY = (0, 0, 0, 180)
    COLOR_GAMEOVER_BG = (0, 0, 0, 220)
    COLOR_HIGHSCORE_NEW = (255, 215, 0)
    
    # Speed settings
    BASE_SPEED = 150  # px/s
    MAX_SPEED = 1300  # px/s
    SPEED_CURVE_EXPONENT = 1.6
    SPEED_NORM_TIME = 1800  # 30 minutes in seconds
    
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
    MIN_SPAWN_DISTANCE_SAME_LANE = 250  # Minimum pixels between enemies on same lane
    MIN_REACTION_TIME = 1.5  # seconds
    TOP_BLOCKED_ZONE_Y = 200  # y < this value must have at least 1 free lane
    
    # Spawn timing (in seconds)
    SPAWN_INTERVAL_START = 2.5
    SPAWN_INTERVAL_MIN = 0.6
    
    # Level thresholds (in seconds)
    LEVEL_THRESHOLDS = [0, 60, 180, 360, 600, 900, 1200, 1500]  # 8 levels
    
    # File paths
    HIGHSCORE_FILE = "highscore.json"


# =============================================================================
# GAME STATES
# =============================================================================
class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAMEOVER = auto()


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
    """Calculate current speed based on elapsed time using non-linear formula"""
    t = min(elapsed_seconds / Config.SPEED_NORM_TIME, 1.0)
    return Config.BASE_SPEED + (Config.MAX_SPEED - Config.BASE_SPEED) * (t ** Config.SPEED_CURVE_EXPONENT)


def get_spawn_interval(speed: float) -> float:
    """Calculate spawn interval based on current speed"""
    speed_ratio = (speed - Config.BASE_SPEED) / (Config.MAX_SPEED - Config.BASE_SPEED)
    return Config.SPAWN_INTERVAL_START - speed_ratio * (Config.SPAWN_INTERVAL_START - Config.SPAWN_INTERVAL_MIN)


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
        
    def update(self, dt: float, speed: float) -> None:
        """Update road scrolling based on speed"""
        scroll_amount = speed * dt
        self.line_offset = (self.line_offset + scroll_amount) % 80
        self.post_offset = (self.post_offset + scroll_amount) % 100
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the road with all markings"""
        # Draw grass background
        screen.fill(Config.COLOR_GRASS)
        
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
        
        for lane in range(1, Config.LANE_COUNT):
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
        self.current_lane = 1  # Start in middle lane (0, 1, 2)
        self.target_lane = 1
        self.lane_change_progress = 0.0
        self.is_changing_lane = False
        
        # Calculate center X positions for each lane
        self.lane_center_x = [
            Config.ROAD_X + Config.LANE_WIDTH * lane + Config.LANE_WIDTH // 2
            for lane in range(Config.LANE_COUNT)
        ]
        
        # Current X position (starts at middle lane center)
        self.x = self.lane_center_x[self.current_lane]
        self.y = Config.PLAYER_Y
        
    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        """Handle player input for lane changes"""
        if self.is_changing_lane:
            return
            
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self._try_lane_change(-1)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self._try_lane_change(1)
            
    def _try_lane_change(self, direction: int) -> None:
        """Initiate a lane change if possible"""
        new_lane = self.current_lane + direction
        if 0 <= new_lane < Config.LANE_COUNT:
            self.target_lane = new_lane
            self.is_changing_lane = True
            self.lane_change_progress = 0.0
            
    def update(self, dt: float) -> None:
        """Update player state and lane change animation"""
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
        """Draw the player car"""
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


# =============================================================================
# ENEMY CLASS
# =============================================================================
class Enemy:
    TYPE_CAR = "car"
    TYPE_TRUCK = "truck"
    
    def __init__(self, lane: int, enemy_type: str, spawn_y: float = -150):
        self.lane = lane
        self.enemy_type = enemy_type
        
        # Set dimensions based on type
        if enemy_type == self.TYPE_TRUCK:
            self.width = Config.ENEMY_TRUCK_WIDTH
            self.height = Config.ENEMY_TRUCK_HEIGHT
            self.color = Config.COLOR_ENEMY_TRUCK
        else:
            self.width = Config.ENEMY_CAR_WIDTH
            self.height = Config.ENEMY_CAR_HEIGHT
            self.color = Config.COLOR_ENEMY_CAR
            
        # Calculate center X position for the lane
        self.x = Config.ROAD_X + lane * Config.LANE_WIDTH + Config.LANE_WIDTH // 2
        self.y = spawn_y
        
    def update(self, dt: float, speed: float) -> None:
        """Move enemy downward with the road scroll speed"""
        self.y += speed * dt
        
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
        
        # Windshield(s)
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
        else:
            # Car windshield at bottom
            windshield_rect = pygame.Rect(
                self.x - self.width // 2 + 5,
                self.y + self.height // 2 - 20,
                self.width - 10,
                15
            )
            pygame.draw.rect(screen, Config.COLOR_ENEMY_WINDSHIELD, windshield_rect, border_radius=3)
            
        # Wheels
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
            enemy = self._try_spawn(speed, elapsed_time)
            if enemy:
                self.enemies.append(enemy)
                newly_spawned.append(enemy)
                
        return newly_spawned
        
    def _try_spawn(self, speed: float, elapsed_time: float) -> Optional[Enemy]:
        """Try to spawn a new enemy following all rules"""
        # Calculate minimum spawn Y to ensure reaction time
        min_reaction_distance = speed * Config.MIN_REACTION_TIME
        spawn_y = -min_reaction_distance - 50  # Spawn above screen with buffer
        
        # Find available lanes (not blocked in top zone)
        available_lanes = []
        
        for lane in range(Config.LANE_COUNT):
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
        import random
        chosen_lane = random.choice(valid_lanes)
        
        # Choose enemy type (20% chance for truck)
        enemy_type = Enemy.TYPE_TRUCK if random.random() < 0.2 else Enemy.TYPE_CAR
        
        enemy = Enemy(chosen_lane, enemy_type, spawn_y)
        self.last_spawn_positions[chosen_lane] = spawn_y
        
        return enemy
        
    def update_enemies(self, dt: float, speed: float) -> None:
        """Update all enemies and remove off-screen ones"""
        for enemy in self.enemies[:]:
            enemy.update(dt, speed)
            if enemy.is_off_screen():
                self.enemies.remove(enemy)
                
    def clear(self) -> None:
        """Clear all enemies"""
        self.enemies.clear()
        self.spawn_timer = 0.0
        self.last_spawn_positions.clear()


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
        
        # For game over
        self.final_time = 0.0
        self.new_highscore = False
        
    def reset_game(self) -> None:
        """Reset game state for a new game"""
        self.elapsed_time = 0.0
        self.current_speed = Config.BASE_SPEED
        self.player = Player()
        self.spawner.clear()
        
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
        
        # Update speed based on elapsed time
        self.current_speed = get_current_speed(self.elapsed_time)
        
        # Update road
        self.road.update(dt, self.current_speed)
        
        # Handle player input and update
        keys = pygame.key.get_scancode()
        self.player.handle_input(keys)
        self.player.update(dt)
        
        # Update enemies
        self.spawner.update(dt, self.current_speed, self.elapsed_time)
        self.spawner.update_enemies(dt, self.current_speed)
        
        # Check collisions
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

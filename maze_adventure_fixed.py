import pygame
import random
import heapq
import json
import os
from datetime import datetime

# ========== 常量设置 ==========
CELL_SIZE = 30
MIN_MAZE_SIZE = 10
MAX_MAZE_SIZE = 30
DEFAULT_SIZE = 20

# 窗口尺寸会根据迷宫大小动态计算
STATUS_BAR_HEIGHT = 70

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (60, 60, 60)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
PURPLE = (147, 0, 211)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
DARK_BLUE = (20, 20, 50)
MENU_BG = (15, 15, 35)
BUTTON_HOVER = (60, 60, 120)
BUTTON_NORMAL = (40, 40, 80)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
BRONZE = (205, 127, 50)


# ========== 安全字体加载 ==========
def get_font(size):
    """获取可用字体，兼容所有系统"""
    try:
        # 尝试使用系统默认字体
        return pygame.font.SysFont(None, size)
    except:
        try:
            # 备用：使用 pygame 内置默认字体
            return pygame.font.Font(None, size)
        except:
            # 最后备用
            return pygame.font.SysFont("arial", size)


# ========== 排行榜管理 ==========
class Leaderboard:
    def __init__(self, filename="leaderboard.json"):
        try:
            self.filename = os.path.join(os.path.dirname(__file__), filename)
        except:
            self.filename = filename
        self.records = self.load()

    def load(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    def save(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, ensure_ascii=False, indent=2)

    def add_record(self, name, maze_size, manual_steps, ai_steps, time_seconds, mode):
        record = {
            "name": name,
            "maze_size": maze_size,
            "manual_steps": manual_steps,
            "ai_steps": ai_steps,
            "time": round(time_seconds, 2),
            "mode": mode,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.records.append(record)
        self.records.sort(key=lambda x: (x["maze_size"], x["time"]))
        self.records = self.records[:20]
        self.save()

    def get_top(self, maze_size=None, limit=10):
        filtered = [r for r in self.records if maze_size is None or r["maze_size"] == maze_size]
        return filtered[:limit]


# ========== Cell 类 ==========
class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.walls = [True, True, True, True]
        self.visited = False

    def get_neighbors(self, grid, maze_height, maze_width):
        neighbors = []
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        for i, (dx, dy) in enumerate(directions):
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < maze_height and 0 <= ny < maze_width:
                neighbor = grid[nx][ny]
                if not neighbor.visited:
                    neighbors.append((i, neighbor))
        return neighbors


# ========== Maze 类 ==========
class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[Cell(i, j) for j in range(width)] for i in range(height)]
        self.start = (0, 0)
        self.end = (height - 1, width - 1)

    def generate(self):
        stack = []
        current = self.grid[0][0]
        current.visited = True
        stack.append(current)

        while stack:
            current = stack[-1]
            neighbors = current.get_neighbors(self.grid, self.height, self.width)
            if neighbors:
                direction, next_cell = random.choice(neighbors)
                current.walls[direction] = False
                opposite = (direction + 2) % 4
                next_cell.walls[opposite] = False
                next_cell.visited = True
                stack.append(next_cell)
            else:
                stack.pop()

        for row in self.grid:
            for cell in row:
                cell.visited = False

    def draw(self, screen, cell_size, explored=None, path=None, explore_progress=None):
        screen.fill(BLACK)

        if explored:
            for idx, (x, y) in enumerate(explored):
                if explore_progress is not None and idx >= explore_progress:
                    break
                intensity = min(255, 50 + idx * 2)
                color = (intensity // 4, intensity // 4, intensity // 2)
                rect = pygame.Rect(y * cell_size + 1, x * cell_size + 1, cell_size - 2, cell_size - 2)
                pygame.draw.rect(screen, color, rect)

        if path:
            for (x, y) in path:
                rect = pygame.Rect(y * cell_size + cell_size // 4, x * cell_size + cell_size // 4, 
                                  cell_size - cell_size // 2, cell_size - cell_size // 2)
                pygame.draw.rect(screen, ORANGE, rect)

        for row in self.grid:
            for cell in row:
                x = cell.y * cell_size
                y = cell.x * cell_size
                if cell.walls[0]:
                    pygame.draw.line(screen, WHITE, (x, y), (x + cell_size, y), 2)
                if cell.walls[1]:
                    pygame.draw.line(screen, WHITE, (x + cell_size, y), (x + cell_size, y + cell_size), 2)
                if cell.walls[2]:
                    pygame.draw.line(screen, WHITE, (x, y + cell_size), (x + cell_size, y + cell_size), 2)
                if cell.walls[3]:
                    pygame.draw.line(screen, WHITE, (x, y), (x, y + cell_size), 2)

        sx, sy = self.start
        ex, ey = self.end
        pad = cell_size // 5
        pygame.draw.rect(screen, GREEN, (sy * cell_size + pad, sx * cell_size + pad, 
                                          cell_size - pad * 2, cell_size - pad * 2))
        pygame.draw.rect(screen, RED, (ey * cell_size + pad, ex * cell_size + pad, 
                                        cell_size - pad * 2, cell_size - pad * 2))


# ========== Player 类 ==========
class Player:
    def __init__(self, maze, start_pos):
        self.maze = maze
        self.x, self.y = start_pos
        self.color = BLUE
        self.manual_steps = 0
        self.trail = []

    def move(self, direction):
        current_cell = self.maze.grid[self.x][self.y]
        if current_cell.walls[direction]:
            return False
        dx, dy = [(-1, 0), (0, 1), (1, 0), (0, -1)][direction]
        new_x, new_y = self.x + dx, self.y + dy
        if 0 <= new_x < self.maze.height and 0 <= new_y < self.maze.width:
            self.x, self.y = new_x, new_y
            self.manual_steps += 1
            self.trail.append((self.x, self.y))
            if len(self.trail) > 20:
                self.trail.pop(0)
            return True
        return False

    def set_position(self, x, y):
        self.x, self.y = x, y

    def draw(self, screen, cell_size):
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            size = cell_size // 4 * (i / len(self.trail))
            if size > 2:
                surf = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
                pygame.draw.circle(surf, (*self.color[:3], alpha), (int(size), int(size)), int(size))
                screen.blit(surf, (ty * cell_size + cell_size // 2 - int(size), 
                                   tx * cell_size + cell_size // 2 - int(size)))

        center_x = self.y * cell_size + cell_size // 2
        center_y = self.x * cell_size + cell_size // 2
        radius = cell_size // 3
        pygame.draw.circle(screen, self.color, (center_x, center_y), radius)
        pygame.draw.circle(screen, WHITE, (center_x, center_y), radius, 2)

    def check_win(self):
        return (self.x, self.y) == self.maze.end


# ========== A* 寻路算法 ==========
class AStarSolver:
    def __init__(self, maze):
        self.maze = maze

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_neighbors(self, pos):
        x, y = pos
        cell = self.maze.grid[x][y]
        neighbors = []
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        for i, (dx, dy) in enumerate(directions):
            if not cell.walls[i]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.maze.height and 0 <= ny < self.maze.width:
                    neighbors.append((nx, ny))
        return neighbors

    def solve(self):
        start = self.maze.start
        end = self.maze.end

        counter = 0
        open_set = [(0, counter, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, end)}
        explored = [start]

        while open_set:
            _, _, current = heapq.heappop(open_set)
            if current == end:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                return explored, path

            for neighbor in self.get_neighbors(current):
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + self.heuristic(neighbor, end)
                    f_score[neighbor] = f
                    counter += 1
                    heapq.heappush(open_set, (f, counter, neighbor))
                    explored.append(neighbor)

        return explored, []


# ========== A* 动画控制器 ==========
class AStarAnimator:
    def __init__(self, explored, path, explore_speed=1, path_speed=3):
        self.explored = explored
        self.path = path
        self.explore_speed = explore_speed
        self.path_speed = path_speed
        self.phase = "exploring"
        self.explore_index = 0
        self.path_index = 0
        self.timer = 0
        self.finished = False

    def update(self):
        self.timer += 1
        if self.phase == "exploring":
            if self.timer >= self.explore_speed:
                self.timer = 0
                self.explore_index += 2
                if self.explore_index >= len(self.explored):
                    self.explore_index = len(self.explored)
                    self.phase = "pathing"
                    self.timer = 0
        elif self.phase == "pathing":
            if self.timer >= self.path_speed:
                self.timer = 0
                self.path_index += 1
                if self.path_index >= len(self.path):
                    self.path_index = len(self.path)
                    self.finished = True

    def get_explore_progress(self):
        return self.explore_index

    def get_path_progress(self):
        return self.path[:self.path_index] if self.path_index > 0 else []

    def get_current_pos(self):
        if self.phase == "pathing" and self.path and self.path_index > 0:
            idx = min(self.path_index - 1, len(self.path) - 1)
            return self.path[idx]
        return None


# ========== 烟花特效系统 ==========
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -1)
        self.color = color
        self.life = 1.0
        self.decay = random.uniform(0.01, 0.03)
        self.size = random.randint(3, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.life -= self.decay
        return self.life > 0

    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * self.life)
            surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color[:3], alpha), (self.size, self.size), self.size)
            screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))


class FireworkSystem:
    def __init__(self):
        self.particles = []

    def explode(self, x, y, color=None):
        if color is None:
            color = random.choice([RED, GREEN, BLUE, YELLOW, PURPLE, CYAN, ORANGE, GOLD])
        for _ in range(30):
            self.particles.append(Particle(x, y, color))

    def update(self):
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)

    def is_active(self):
        return len(self.particles) > 0


# ========== 菜单系统 ==========
class Button:
    def __init__(self, x, y, width, height, text, callback, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = font
        self.hovered = False

    def draw(self, screen):
        color = BUTTON_HOVER if self.hovered else BUTTON_NORMAL
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=10)

        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered and event.button == 1:
                self.callback()
                return True
        return False


class Menu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = get_font(32)
        self.title_font = get_font(56)
        self.small_font = get_font(20)

        self.selected_size = DEFAULT_SIZE
        self.show_leaderboard = False
        self.leaderboard = Leaderboard()
        self.name_input = "Player"
        self.input_active = False

        cx = screen_width // 2
        cy = screen_height // 2

        self.buttons = [
            Button(cx - 120, cy - 80, 240, 50, "Easy (15x15)", 
                   lambda: self.set_size(15), self.font),
            Button(cx - 120, cy - 10, 240, 50, "Medium (20x20)", 
                   lambda: self.set_size(20), self.font),
            Button(cx - 120, cy + 60, 240, 50, "Hard (25x25)", 
                   lambda: self.set_size(25), self.font),
            Button(cx - 120, cy + 130, 240, 50, "Custom Size", 
                   lambda: self.toggle_custom(), self.font),
            Button(cx - 120, cy + 200, 240, 50, "Leaderboard", 
                   lambda: self.toggle_leaderboard(), self.font),
        ]

        self.custom_buttons = []
        self.start_game = False

    def set_size(self, size):
        self.selected_size = size
        self.start_game = True

    def toggle_custom(self):
        if not self.custom_buttons:
            cx = self.screen_width // 2
            for i, size in enumerate([10, 12, 15, 18, 20, 22, 25, 28, 30]):
                x = cx - 200 + (i % 3) * 140
                y = 420 + (i // 3) * 60
                self.custom_buttons.append(
                    Button(x, y, 120, 45, f"{size}x{size}", 
                           lambda s=size: self.set_size(s), self.small_font)
                )
        else:
            self.custom_buttons = []

    def toggle_leaderboard(self):
        self.show_leaderboard = not self.show_leaderboard

    def draw(self, screen):
        screen.fill(MENU_BG)

        title = self.title_font.render("Maze Adventure", True, CYAN)
        title_rect = title.get_rect(center=(self.screen_width // 2, 80))
        screen.blit(title, title_rect)

        subtitle = self.small_font.render("A* Pathfinding Visualization", True, GRAY)
        subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, 140))
        screen.blit(subtitle, subtitle_rect)

        hints = [
            "Arrow Keys: Move | Space: A* Auto | R: Restart",
            "Watch AI think and find the shortest path!"
        ]
        for i, hint in enumerate(hints):
            surf = self.small_font.render(hint, True, DARK_GRAY)
            rect = surf.get_rect(center=(self.screen_width // 2, 180 + i * 25))
            screen.blit(surf, rect)

        if self.show_leaderboard:
            self.draw_leaderboard(screen)
        else:
            for btn in self.buttons:
                btn.draw(screen)
            for btn in self.custom_buttons:
                btn.draw(screen)

    def draw_leaderboard(self, screen):
        records = self.leaderboard.get_top(limit=10)

        panel = pygame.Rect(self.screen_width // 2 - 250, 200, 500, 350)
        pygame.draw.rect(screen, DARK_BLUE, panel, border_radius=10)
        pygame.draw.rect(screen, WHITE, panel, 2, border_radius=10)

        title = self.font.render("Leaderboard TOP 10", True, GOLD)
        screen.blit(title, (panel.centerx - title.get_width() // 2, 210))

        if not records:
            msg = self.small_font.render("No records yet. Come challenge!", True, GRAY)
            screen.blit(msg, (panel.centerx - msg.get_width() // 2, 350))
            return

        headers = ["Rank", "Player", "Size", "Mode", "Steps", "Time", "Date"]
        x_positions = [panel.left + 20, panel.left + 70, panel.left + 140, 
                       panel.left + 200, panel.left + 270, panel.left + 330, panel.left + 400]

        for i, h in enumerate(headers):
            surf = self.small_font.render(h, True, YELLOW)
            screen.blit(surf, (x_positions[i], 250))

        colors = [GOLD, SILVER, BRONZE, WHITE]
        for i, r in enumerate(records[:10]):
            y = 280 + i * 28
            color = colors[i] if i < 3 else WHITE
            rank = "1st" if i == 0 else "2nd" if i == 1 else "3rd" if i == 2 else str(i + 1)

            vals = [rank, r["name"], f"{r['maze_size']}x{r['maze_size']}", 
                    "AI" if r["mode"] == "ai" else "Manual", 
                    str(r["ai_steps"] if r["mode"] == "ai" else r["manual_steps"]),
                    f"{r['time']}s", r["date"][5:]]

            for j, v in enumerate(vals):
                surf = self.small_font.render(str(v), True, color)
                screen.blit(surf, (x_positions[j], y))

    def handle_event(self, event):
        if self.show_leaderboard:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.show_leaderboard = False
                return
        else:
            for btn in self.buttons:
                if btn.handle_event(event):
                    return
            for btn in self.custom_buttons:
                if btn.handle_event(event):
                    return


# ========== 状态栏绘制 ==========
def draw_status_bar(screen, font, player, maze_size, ai_animator=None, won=False, 
                    ai_steps=0, explore_count=0, elapsed_time=0, mode=""):
    bar_y = CELL_SIZE * maze_size
    pygame.draw.rect(screen, DARK_BLUE, (0, bar_y, CELL_SIZE * maze_size, STATUS_BAR_HEIGHT))
    pygame.draw.line(screen, WHITE, (0, bar_y), (CELL_SIZE * maze_size, bar_y), 2)

    status = "CLEARED!" if won else "AI Exploring..." if ai_animator and ai_animator.phase == "exploring" else "AI Pathing..." if ai_animator else "Manual Mode"
    color = YELLOW if won else CYAN if ai_animator and ai_animator.phase == "exploring" else PURPLE if ai_animator else WHITE

    status_surf = font.render(status, True, color)
    screen.blit(status_surf, (10, bar_y + 8))

    stats = [
        f"Manual: {player.manual_steps} steps",
        f"AI: {ai_steps} steps",
        f"Explored: {explore_count}",
        f"Time: {elapsed_time:.1f}s",
        f"Mode: {mode}"
    ]

    x = 10
    for stat in stats:
        surf = font.render(stat, True, GRAY)
        screen.blit(surf, (x, bar_y + 35))
        x += surf.get_width() + 20


# ========== 主程序 ==========
def main():
    pygame.init()

    menu_width, menu_height = 600, 650
    screen = pygame.display.set_mode((menu_width, menu_height))
    pygame.display.set_caption("Maze Adventure - Main Menu")
    clock = pygame.time.Clock()

    menu = Menu(menu_width, menu_height)
    leaderboard = Leaderboard()

    in_menu = True
    while in_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            menu.handle_event(event)

        menu.draw(screen)
        pygame.display.flip()
        clock.tick(60)

        if menu.start_game:
            in_menu = False

    maze_size = menu.selected_size
    cell_size = min(30, 800 // maze_size)
    window_width = cell_size * maze_size
    window_height = cell_size * maze_size + STATUS_BAR_HEIGHT

    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption(f"Maze Adventure - {maze_size}x{maze_size}")

    font = get_font(16)
    big_font = get_font(40)

    maze = Maze(maze_size, maze_size)
    maze.generate()
    player = Player(maze, maze.start)

    ai_mode = False
    ai_animator = None
    explored_nodes = []
    full_path = []
    ai_steps = 0
    explore_count = 0
    win_mode = ""

    fireworks = FireworkSystem()

    start_time = pygame.time.get_ticks()
    elapsed_time = 0
    won = False
    win_time = 0

    running = True
    while running:
        if not won:
            elapsed_time = (pygame.time.get_ticks() - start_time) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    maze = Maze(maze_size, maze_size)
                    maze.generate()
                    player = Player(maze, maze.start)
                    ai_mode = False
                    ai_animator = None
                    explored_nodes = []
                    full_path = []
                    ai_steps = 0
                    explore_count = 0
                    won = False
                    win_mode = ""
                    start_time = pygame.time.get_ticks()
                    elapsed_time = 0

                elif event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_SPACE and not ai_mode and not won:
                    solver = AStarSolver(maze)
                    explored_nodes, full_path = solver.solve()
                    ai_steps = len(full_path) - 1 if full_path else 0
                    explore_count = len(explored_nodes)

                    if full_path:
                        ai_mode = True
                        ai_animator = AStarAnimator(explored_nodes, full_path, explore_speed=1, path_speed=3)
                        player.color = PURPLE

                elif not ai_mode and not won:
                    moved = False
                    if event.key == pygame.K_UP:
                        moved = player.move(0)
                    elif event.key == pygame.K_RIGHT:
                        moved = player.move(1)
                    elif event.key == pygame.K_DOWN:
                        moved = player.move(2)
                    elif event.key == pygame.K_LEFT:
                        moved = player.move(3)

                    if moved and player.check_win():
                        won = True
                        win_mode = "manual"
                        win_time = elapsed_time
                        fireworks.explode(window_width // 2, window_height // 3, GOLD)
                        fireworks.explode(window_width // 3, window_height // 4, RED)
                        fireworks.explode(window_width * 2 // 3, window_height // 4, GREEN)
                        leaderboard.add_record(menu.name_input, maze_size, player.manual_steps, 
                                              ai_steps, win_time, win_mode)

        displayed_path = []
        explore_progress = None

        if ai_mode and ai_animator:
            ai_animator.update()
            explore_progress = ai_animator.get_explore_progress()
            displayed_path = ai_animator.get_path_progress()

            current_pos = ai_animator.get_current_pos()
            if current_pos:
                player.set_position(*current_pos)

            if ai_animator.finished and not won:
                won = True
                win_mode = "ai"
                win_time = elapsed_time
                player.color = BLUE
                fireworks.explode(window_width // 2, window_height // 3, GOLD)
                fireworks.explode(window_width // 3, window_height // 4, CYAN)
                fireworks.explode(window_width * 2 // 3, window_height // 4, PURPLE)
                leaderboard.add_record(menu.name_input, maze_size, player.manual_steps,
                                      ai_steps, win_time, win_mode)

        fireworks.update()

        maze.draw(screen, cell_size, explored=explored_nodes, path=displayed_path,
                  explore_progress=explore_progress)
        player.draw(screen, cell_size)

        draw_status_bar(screen, font, player, maze_size, ai_animator, won,
                       ai_steps, explore_count, elapsed_time, 
                       "AI" if win_mode == "ai" else "Manual" if win_mode == "manual" else "")

        if won:
            overlay = pygame.Surface((window_width, window_height - STATUS_BAR_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            fireworks.draw(screen)

            if not fireworks.is_active():
                text = big_font.render("CLEARED!", True, YELLOW)
                text_rect = text.get_rect(center=(window_width // 2, (window_height - STATUS_BAR_HEIGHT) // 2 - 40))
                screen.blit(text, text_rect)

                mode_text = "AI Auto Clear" if win_mode == "ai" else "Manual Clear"
                mode_surf = font.render(mode_text, True, CYAN if win_mode == "ai" else GREEN)
                mode_rect = mode_surf.get_rect(center=(window_width // 2, (window_height - STATUS_BAR_HEIGHT) // 2 + 10))
                screen.blit(mode_surf, mode_rect)

                summary = f"Time: {win_time:.1f}s | Manual: {player.manual_steps} steps | AI: {ai_steps} steps"
                summary_surf = font.render(summary, True, WHITE)
                summary_rect = summary_surf.get_rect(center=(window_width // 2, (window_height - STATUS_BAR_HEIGHT) // 2 + 45))
                screen.blit(summary_surf, summary_rect)

                hint = font.render("Press R to restart | ESC to quit", True, GRAY)
                hint_rect = hint.get_rect(center=(window_width // 2, (window_height - STATUS_BAR_HEIGHT) // 2 + 80))
                screen.blit(hint, hint_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()

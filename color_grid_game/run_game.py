
import sys
import os
import pygame
# Ajoutez le chemin du dossier parent au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from color_grid_game import *

pygame.init()

class UIManager:
    """Manages the UI elements and rendering for the game."""

    def __init__(self, screen: pygame.Surface, colors: dict, colors_title: dict):
        """
        Initialize the UIManager with screen, colors, and title colors.

        Parameters:
        -----------
        screen : pygame.Surface
            The game screen.
        colors : dict
            Dictionary of colors for the game.
        colors_title : dict
            Dictionary of colors for the title.
        """
        self.screen = screen
        self.colors = colors
        self.colors_title = colors_title
        self.volume_theme = 0.01
        self.volume = 0.02

        # Load sound effects and images
        self.game_theme = pygame.mixer.Sound("./medias/game theme.mp3")
        self.win_sound = pygame.mixer.Sound("./medias/win.mp3")
        self.lose_sound = pygame.mixer.Sound("./medias/lose.mp3")
        self.sound_on_img = pygame.transform.scale(
            pygame.image.load("./medias/sound on.png").convert_alpha(),
            (30, 30)
        )
        self.sound_off_img = pygame.transform.scale(
            pygame.image.load("./medias/sound off.png").convert_alpha(),
            (30, 30)
        )

        self.game_theme.set_volume(self.volume_theme)
        self.win_sound.set_volume(self.volume)
        self.lose_sound.set_volume(self.volume)
        self.game_theme.play(loops=-1)

        # Animation variables
        self.color_index = 0
        self.color_timer = 0
        self.color_interval = 500

    def draw_volume_button(self, window_size: tuple, pressed: bool):
        """
        Draws the volume toggle button.

        Parameters:
        -----------
        window_size : tuple
            The size of the window.
        pressed : bool
            Whether the button is pressed.
        """
        button_rect = pygame.Rect(window_size[0] - 95, window_size[1] - 70, 50, 40)
        color = (30, 30, 30) if pressed else (50, 50, 50)
        pygame.draw.rect(self.screen, color, button_rect)

        img = self.sound_off_img if self.volume == 0 else self.sound_on_img
        img_rect = img.get_rect(center=button_rect.center)
        self.screen.blit(img, img_rect)

    def toggle_volume(self):
        """Toggles the volume between muted and last volume."""
        if self.volume == 0:
            self.volume = 0.02
            self.volume_theme = 0.01
            self.game_theme.set_volume(self.volume_theme)
            self.win_sound.set_volume(self.volume)
            self.lose_sound.set_volume(self.volume)
        else:
            self.volume = 0
            self.game_theme.set_volume(self.volume)
            self.win_sound.set_volume(self.volume)
            self.lose_sound.set_volume(self.volume)

    def draw_title(self, window_size: tuple):
        """
        Draws the title of the game with animated colors.

        Parameters:
        -----------
        window_size : tuple
            The size of the window.
        """
        font = pygame.font.Font(None, 72)
        title = "ColorGrid"

        current_time = pygame.time.get_ticks()
        if current_time - self.color_timer > self.color_interval:
            self.color_index = (self.color_index + 1) % len(self.colors_title)
            self.color_timer = current_time

        colors = [self.colors_title[(self.color_index + i) % len(self.colors_title)] for i in range(len(title))]

        total_width = sum(font.size(char)[0] for char in title)
        start_x = (window_size[0] - total_width) // 2

        current_x = start_x
        for i, char in enumerate(title):
            text = font.render(char, True, colors[i])
            self.screen.blit(text, (current_x, 20))
            current_x += text.get_width()

    def draw_grid_options(self, window_size: tuple, scroll: int, scroll_bar_rect: pygame.Rect, scroll_bar_height: int, grid_files: list, grid_colors: list, pressed_index: int = -1):
        """
        Draws the grid options with scrolling functionality.

        Parameters:
        -----------
        window_size : tuple
            The size of the window.
        scroll : int
            The current scroll position.
        scroll_bar_rect : pygame.Rect
            The rectangle for the scroll bar.
        scroll_bar_height : int
            The height of the scroll bar.
        grid_files : list
            List of grid files.
        grid_colors : list
            List of colors for the grid files.
        pressed_index : int, optional
            The index of the pressed grid option. Default is -1.
        """
        font = pygame.font.Font(None, 36)
        y_offset = 100
        max_scroll = max(0, len(grid_files) * 50 - (window_size[1] - 170))
        scroll = max(0, min(scroll, max_scroll))

        pygame.draw.rect(self.screen, (255, 255, 255), (50, 100, window_size[0] - 120, window_size[1] - 170))

        for i, (filename, _) in enumerate(grid_files):
            if y_offset + 50 - scroll > window_size[1] - 70:
                break

            btn_color = self.darken_color(grid_colors[i]) if i == pressed_index else grid_colors[i]
            brightness = (btn_color[0] * 299 + btn_color[1] * 587 + btn_color[2] * 114) // 1000
            text_color = (0, 0, 0) if brightness > 128 else (255, 255, 255)

            formatted_name = f"Grid {filename[4:-3]}" if filename.startswith("grid") and filename.endswith(".in") else filename

            btn_rect = pygame.Rect(window_size[0] // 2 - 100, y_offset - scroll, 200, 40)
            pygame.draw.rect(self.screen, btn_color, btn_rect)
            text_surface = font.render(formatted_name, True, text_color)
            text_rect = text_surface.get_rect(center=btn_rect.center)
            self.screen.blit(text_surface, text_rect)
            y_offset += 50

        pygame.draw.rect(self.screen, (150, 150, 150), scroll_bar_rect.inflate(0, scroll_bar_height - scroll_bar_rect.height))

    def darken_color(self, color: tuple, factor: float = 0.7) -> tuple:
        """
        Darkens a color by a given factor.

        Parameters:
        -----------
        color : tuple
            The color to darken.
        factor : float, optional
            The factor by which to darken the color. Default is 0.7.

        Returns:
        --------
        tuple
            The darkened color.
        """
        return (int(color[0] * factor), int(color[1] * factor), int(color[2] * factor))

    def draw_grid(self, grid: Grid, solver: Solver, cell_size: int, selected_cells: list = [], game_mode: str = 'one', player_pairs: list = None, top_margin: int = 0):
        """
        Draws the game grid with cells and pairs.

        Parameters:
        -----------
        grid : Grid
            The game grid.
        solver : Solver
            The solver for the game.
        cell_size : int
            The size of each cell.
        selected_cells : list, optional
            List of selected cells. Default is [].
        game_mode : str, optional
            The game mode. Default is 'one'.
        player_pairs : list, optional
            List of player pairs. Default is None.
        top_margin : int, optional
            The top margin for the grid. Default is 0.
        """
        for i in range(grid.n):
            for j in range(grid.m):
                color = self.colors[grid.color[i][j]]
                if (i, j) in selected_cells:
                    color = self.darken_color(color)
                pygame.draw.rect(self.screen, color, (j * cell_size, i * cell_size + top_margin, cell_size, cell_size))
                pygame.draw.rect(self.screen, (0, 0, 0), (j * cell_size, i * cell_size + top_margin, cell_size, cell_size), 1)
                font = pygame.font.Font(None, 36)
                text = font.render(str(grid.value[i][j]), True, (0, 0, 0))
                self.screen.blit(text, (j * cell_size + cell_size // 2 - text.get_width() // 2, i * cell_size + top_margin + cell_size // 2 - text.get_height() // 2))

        if game_mode == 'one':
            for pair in solver.pairs:
                self.draw_pair_frame(pair, self.colors[5], cell_size, top_margin)
        else:
            if player_pairs:
                for pair in player_pairs[0]:
                    self.draw_pair_frame(pair, self.colors[5], cell_size, top_margin)
                for pair in player_pairs[1]:
                    self.draw_pair_frame(pair, (148, 0, 211), cell_size, top_margin)

    def draw_pair_frame(self, pair: tuple, color: tuple, cell_size: int, top_margin: int):
        """
        Draws a frame around a pair of cells.

        Parameters:
        -----------
        pair : tuple
            The pair of cells.
        color : tuple
            The color of the frame.
        cell_size : int
            The size of each cell.
        top_margin : int
            The top margin for the grid.
        """
        (i1, j1), (i2, j2) = pair
        min_i = min(i1, i2)
        max_i = max(i1, i2)
        min_j = min(j1, j2)
        max_j = max(j1, j2)

        frame_inset = 4
        frame_x = min_j * cell_size + frame_inset
        frame_y = min_i * cell_size + top_margin + frame_inset
        frame_width = (max_j - min_j + 1) * cell_size - 2 * frame_inset
        frame_height = (max_i - min_i + 1) * cell_size - 2 * frame_inset

        pygame.draw.rect(self.screen, color, (frame_x, frame_y, frame_width, frame_height), 4)

    def draw_score(self, solver: Solver, window_size: tuple, cell_size: int, player1_score: int, player2_score: int, game_mode: str = 'one'):
        """
        Draws the current score.

        Parameters:
        -----------
        solver : Solver
            The solver for the game.
        window_size : tuple
            The size of the window.
        cell_size : int
            The size of each cell.
        player1_score : int
            The score of player 1.
        player2_score : int
            The score of player 2.
        game_mode : str, optional
            The game mode. Default is 'one'.
        """
        font = pygame.font.Font(None, 38)

        if game_mode == 'one':
            text = font.render(f"Score: {solver.score()}", True, (0, 0, 0))
            self.screen.blit(text, (5, window_size[1] - cell_size - 45))
        elif game_mode == 'two':
            text = font.render(f"Player 1: {player1_score}", True, self.colors[5])
            self.screen.blit(text, (5, window_size[1] - cell_size - 45))
            text = font.render(f"Player 2: {player2_score}", True, (148, 0, 211))
            self.screen.blit(text, (5, window_size[1] - cell_size - 15))
        else:
            text = font.render(f"Player 1: {player1_score}", True, self.colors[5])
            self.screen.blit(text, (5, window_size[1] - cell_size - 45))
            text = font.render(f"Stockfish: {player2_score}", True, (148, 0, 211))
            self.screen.blit(text, (5, window_size[1] - cell_size - 15))

    def draw_turn_indicator(self, current_player: int, window_size: tuple, top_margin: int, game_mode: str):
        """
        Shows whose turn it is.

        Parameters:
        -----------
        current_player : int
            The current player.
        window_size : tuple
            The size of the window.
        top_margin : int
            The top margin for the grid.
        game_mode : str
            The game mode.
        """
        font = pygame.font.Font(None, 46)
        color = self.colors[5] if current_player == 1 else (148, 0, 211)
        text = font.render(f"{'Player 1' if current_player == 1 else 'Player 2' if current_player == 2 and game_mode == 'two' else 'Stockfish'} to play", True, color)
        x_position = (window_size[0] - text.get_width()) // 2
        self.screen.blit(text, (x_position, top_margin // 2 - 20))

    def draw_end_screen(self, message: str, color: tuple, window_size: tuple):
        """
        Displays the end screen with a semi-transparent overlay and centered message.

        Parameters:
        -----------
        message : str
            The message to display.
        color : tuple
            The color of the message.
        window_size : tuple
            The size of the window.
        """
        pygame.time.delay(200)
        overlay = pygame.Surface(window_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.Font(None, 72)
        text = font.render(message, True, color)
        text_rect = text.get_rect(center=(window_size[0] // 2, window_size[1] // 2))

        border_surface = pygame.Surface((text_rect.width + 4, text_rect.height + 4), pygame.SRCALPHA)
        self.screen.blit(border_surface, (text_rect.x - 2, text_rect.y - 2))

        self.screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.wait(4000)

    def draw_error_message(self, message: str, window_size: tuple, mode: str, cell_size: int):
        """
        Displays an error message.

        Parameters:
        -----------
        message : str
            The error message.
        window_size : tuple
            The size of the window.
        mode : str
            The game mode.
        cell_size : int
            The size of each cell.
        """
        font = pygame.font.Font(None, 38)
        text = font.render(message, True, (200, 0, 0))
        y_position = window_size[1] - cell_size - 15 if mode == "one" else window_size[1] - cell_size + 15
        self.screen.blit(text, (5, y_position))
        pygame.display.flip()
        pygame.time.wait(700)

    def draw_restart_button(self, window_size: tuple, pressed: bool, mode: str):
        """
        Draws the restart button.

        Parameters:
        -----------
        window_size : tuple
            The size of the window.
        pressed : bool
            Whether the button is pressed.
        mode : str
            The game mode.
        """
        font = pygame.font.Font(None, 36)
        text = font.render("Restart", True, (255, 255, 255))
        button_rect = pygame.Rect(window_size[0] - 330, window_size[1] - 70, 100, 40) if mode == "one" else pygame.Rect(window_size[0] - 220, window_size[1] - 70, 100, 40)
        text_rect = text.get_rect(center=button_rect.center)
        color = (30, 30, 30) if pressed else (50, 50, 50)
        pygame.draw.rect(self.screen, color, button_rect)
        self.screen.blit(text, text_rect.topleft)

    def draw_solution_button(self, window_size: tuple, pressed: bool):
        """
        Draws the solution button.

        Parameters:
        -----------
        window_size : tuple
            The size of the window.
        pressed : bool
            Whether the button is pressed.
        """
        font = pygame.font.Font(None, 36)
        text = font.render("Solution", True, (255, 255, 255))
        button_rect = pygame.Rect(window_size[0] - 225, window_size[1] - 70, 110, 40)
        text_rect = text.get_rect(center=button_rect.center)
        color = (0, 150, 0) if pressed else (0, 200, 0)
        pygame.draw.rect(self.screen, color, button_rect)
        self.screen.blit(text, text_rect.topleft)

    def draw_menu_button(self, window_size: tuple, pressed: bool):
        """
        Draws the menu button.

        Parameters:
        -----------
        window_size : tuple
            The size of the window.
        pressed : bool
            Whether the button is pressed.
        """
        font = pygame.font.Font(None, 36)
        text = font.render("Menu", True, (255, 255, 255))
        button_rect = pygame.Rect(window_size[0] - 110, window_size[1] - 70, 100, 40)
        text_rect = text.get_rect(center=button_rect.center)
        color = (30, 30, 30) if pressed else (50, 50, 50)
        pygame.draw.rect(self.screen, color, button_rect)
        self.screen.blit(text, text_rect.topleft)

    def draw_rules_button(self, window_size: tuple, pressed: bool):
        """
        Draws the rules button.

        Parameters:
        -----------
        window_size : tuple
            The size of the window.
        pressed : bool
            Whether the button is pressed.
        """
        font = pygame.font.Font(None, 36)
        text = font.render("Rules", True, (255, 255, 255))
        button_rect = pygame.Rect(window_size[0] - 200, window_size[1] - 70, 100, 40)
        text_rect = text.get_rect(center=button_rect.center)
        color = (30, 30, 30) if pressed else (50, 50, 50)
        pygame.draw.rect(self.screen, color, button_rect)
        self.screen.blit(text, text_rect.topleft)

    def draw_player_choice(self, window_size: tuple, pressed_button: str):
        """
        Draws the player choice buttons.

        Parameters:
        -----------
        window_size : tuple
            The size of the window.
        pressed_button : str
            The pressed button.
        """
        font = pygame.font.Font(None, 50)

        one_rect = pygame.Rect(window_size[0] // 2 - 140, 200, 300, 60)
        color_choice = (30, 30, 30) if pressed_button == 'one' else (50, 50, 50)
        pygame.draw.rect(self.screen, color_choice, one_rect)
        text = font.render("One Player", True, (255, 255, 255))
        text_rect = text.get_rect(center=one_rect.center)
        self.screen.blit(text, text_rect)

        two_rect = pygame.Rect(window_size[0] // 2 - 140, 300, 300, 60)
        color_choice = (30, 30, 30) if pressed_button == 'two' else (50, 50, 50)
        pygame.draw.rect(self.screen, color_choice, two_rect)
        text = font.render("Two Players", True, (255, 255, 255))
        text_rect = text.get_rect(center=two_rect.center)
        self.screen.blit(text, text_rect)

        bot_rect = pygame.Rect(window_size[0] // 2 - 140, 400, 300, 60)
        color_choice = (30, 30, 30) if pressed_button == 'bot' else (50, 50, 50)
        pygame.draw.rect(self.screen, color_choice, bot_rect)
        text = font.render("Versus Stockfish", True, (255, 255, 255))
        text_rect = text.get_rect(center=bot_rect.center)
        self.screen.blit(text, text_rect)

    def draw_rules(self, window_size: tuple, scroll: int, scroll_bar_rect: pygame.Rect, scroll_bar_height: int):
        """
        Draws the game rules with scrolling functionality and animated title.

        Parameters:
        -----------
        window_size : tuple
            The size of the window.
        scroll : int
            The current scroll position.
        scroll_bar_rect : pygame.Rect
            The rectangle for the scroll bar.
        scroll_bar_height : int
            The height of the scroll bar.
        """
        font = pygame.font.Font(None, 72)
        font_title = pygame.font.Font(None, 72)
        font_content = pygame.font.Font(None, 24)
        rules = [
            "Consider a grid of size n × m where n ≥ 1 and m ≥ 2 are integers representing the number",
            "of rows and columns respectively. Cells have coordinates (i,j) where:",
            "i in {0,...,n−1} (row index), j in {0,...,m−1} (column index).",
            "",
            "Each cell has 2 attributes:",
            "   — Color c(i,j) in {0 (white), 1 (red), 2 (blue), 3 (green), 4 (black)}",
            "   — Value v(i,j) in N* (positive integer)",
            "",
            "Pairing rules:",
            "   1. Adjacent cells only (horizontal/vertical)",
            "   2. Color constraints:",
            "       - Black (4) cannot be paired",
            "       - White (0) pairs with any except black",
            "       - Blue (2)/Red (1) pair with white/blue/red",
            "       - Green (3) pairs only with white/green",
            "   3. Each cell can only be in one pair",
            "",
            "Score calculation:",
            "   Score = ∑|v(i1,j1) − v(i2,j2)| for all pairs + ∑v for unpaired cells",
            "",
            "Objective: Find pairing with minimal score"
        ]

        self.screen.fill((255, 255, 255))

        title = "Game Rules"
        title_colors = [
            (0, 0, 0), (200, 0, 0), (0, 0, 200), (0, 200, 0), (0, 0, 0),
            (200, 0, 0), (0, 0, 200), (0, 200, 0), (200, 0, 0), (0, 0, 200)
        ]

        current_time = pygame.time.get_ticks()
        if current_time - self.color_timer > self.color_interval:
            self.color_index = (self.color_index + 1) % len(title_colors)
            self.color_timer = current_time

        colors = [title_colors[(self.color_index + i) % len(title_colors)] for i in range(len(title))]

        total_width = sum(font_title.size(char)[0] for char in title)
        start_x = (window_size[0] - total_width) // 2

        current_x = start_x
        for i, char in enumerate(title):
            text = font_title.render(char, True, colors[i])
            self.screen.blit(text, (current_x, 20))
            current_x += text.get_width()

        content_clip_top = 92
        content_clip_bottom = window_size[1] - 70
        content_clip_rect = pygame.Rect(0, content_clip_top, window_size[0], content_clip_bottom - content_clip_top)
        self.screen.set_clip(content_clip_rect)
        y_offset = 92

        for line in rules:
            formatted_line = ''.join(line)
            text_color = (200, 0, 0) if line.startswith("Objective:") else (0, 0, 0)
            text_surface = font_content.render(formatted_line, True, text_color)
            current_y = y_offset - scroll
            self.screen.blit(text_surface, (20, current_y))
            y_offset += 30

        self.screen.set_clip(None)
        pygame.draw.rect(self.screen, (150, 150, 150), scroll_bar_rect)
        self.draw_menu_button(window_size, False)
        pygame.display.flip()

class GridManager:
    """Manages the loading and coloring of grid files."""

    def __init__(self, data_path: str):
        """
        Initialize the GridManager with the data path.

        Parameters:
        -----------
        data_path : str
            The path to the data directory.
        """
        self.data_path = data_path
        self.grid_files = []
        self.difficulties = []
        self.grid_colors = []

        for f in os.listdir(data_path):
            if f.endswith(".in"):
                difficulty = self.extract_difficulty(f)
                self.grid_files.append((f, difficulty))
                self.difficulties.append(difficulty)

        self.min_d = min(self.difficulties) if self.difficulties else 0
        self.max_d = max(self.difficulties) if self.difficulties else 1
        self.range_d = self.max_d - self.min_d if self.max_d != self.min_d else 1
        self.grid_colors = [self.get_difficulty_color(d) for d in self.difficulties]

    def extract_difficulty(self, filename: str) -> int:
        """
        Extracts the difficulty level from the filename.

        Parameters:
        -----------
        filename : str
            The name of the file.

        Returns:
        --------
        int
            The difficulty level.
        """
        base = filename[4:-3]
        parts = base.split('_')
        try:
            return int(parts[-1])
        except (IndexError, ValueError):
            return 0

    def get_difficulty_color(self, difficulty: int) -> tuple:
        """
        Returns a color based on the difficulty level.

        Parameters:
        -----------
        difficulty : int
            The difficulty level.

        Returns:
        --------
        tuple
            The color corresponding to the difficulty level.
        """
        normalized = (difficulty - self.min_d) / self.range_d if self.range_d != 0 else 0.5
        normalized = max(0.0, min(normalized, 1.0))

        stops = [
            (0.0, (255, 255, 255)),
            (0.2, (0, 200, 0)),
            (0.4, (220, 220, 0)),
            (0.6, (255, 165, 0)),
            (0.8, (200, 0, 0)),
            (1.0, (0, 0, 0))
        ]

        for i in range(len(stops) - 1):
            start_pos, start_color = stops[i]
            end_pos, end_color = stops[i + 1]
            if start_pos <= normalized <= end_pos:
                t = (normalized - start_pos) / (end_pos - start_pos)
                return (
                    int(start_color[0] + t * (end_color[0] - start_color[0])),
                    int(start_color[1] + t * (end_color[1] - start_color[1])),
                    int(start_color[2] + t * (end_color[2] - start_color[2]))
                )
        return stops[-1][1]

    def load_grid(self, selected_grid: str) -> Grid:
        """
        Loads a grid from a file.

        Parameters:
        -----------
        selected_grid : str
            The name of the selected grid file.

        Returns:
        --------
        Grid
            The loaded grid.
        """
        return Grid.grid_from_file(os.path.join(self.data_path, selected_grid), read_values=True)

class SolverManager:
    """Manages the solver logic for the game."""

    def __init__(self, grid: Grid):
        """
        Initialize the SolverManager with a grid.

        Parameters:
        -----------
        grid : Grid
            The game grid.
        """
        self.solver = Solver(grid)
        self.solver_general = SolverHungarian(grid)
        self.solver_general.run()
        self.general_score = self.solver_general.score()

    def can_pair(self, color1: int, color2: int) -> bool:
        """
        Checks if two colors can be paired.

        Parameters:
        -----------
        color1 : int
            The first color.
        color2 : int
            The second color.

        Returns:
        --------
        bool
            True if the colors can be paired, False otherwise.
        """
        allowed = {
            0: {0, 1, 2, 3},
            1: {0, 1, 2},
            2: {0, 1, 2},
            3: {0, 3}
        }
        return color2 in allowed.get(color1, set()) and color1 in allowed.get(color2, set())

    def pair_is_valid(self, pair: tuple, existing_pairs: list, grid: Grid, player_pairs: list) -> bool:
        """
        Checks if a pair is valid considering the pairs of both players.

        Parameters:
        -----------
        pair : tuple
            The pair to check.
        existing_pairs : list
            List of existing pairs.
        grid : Grid
            The game grid.
        player_pairs : list
            List of player pairs.

        Returns:
        --------
        bool
            True if the pair is valid, False otherwise.
        """
        (i1, j1), (i2, j2) = pair
        if grid.is_forbidden(i1, j1) or grid.is_forbidden(i2, j2):
            return False
        if (i1, j1) in [cell for pair in existing_pairs for cell in pair]:
            return False
        if (i2, j2) in [cell for pair in existing_pairs for cell in pair]:
            return False
        if (i1, j1) in [cell for pair in player_pairs[0] for cell in pair] or (i2, j2) in [cell for pair in player_pairs[0] for cell in pair]:
            return False
        if (i1, j1) in [cell for pair in player_pairs[1] for cell in pair] or (i2, j2) in [cell for pair in player_pairs[1] for cell in pair]:
            return False
        if self.can_pair(grid.color[i1][j1], grid.color[i2][j2]):
            return True
        return False

    def calculate_player_score(self, player_pairs: list, grid: Grid) -> int:
        """
        Calculates the score for a player considering their pairs and unpaired cells.

        Parameters:
        -----------
        player_pairs : list
            List of player pairs.
        grid : Grid
            The game grid.

        Returns:
        --------
        int
            The calculated score.
        """
        paired_cells = set(cell for pair in player_pairs for cell in pair)
        score = sum(abs(grid.value[i1][j1] - grid.value[i2][j2]) for (i1, j1), (i2, j2) in player_pairs)
        score += sum(grid.value[i][j] for i in range(grid.n) for j in range(grid.m) if (i, j) not in paired_cells and grid.color[i][j] != 4)
        return score

    def calculate_two_player_score(self, player_pairs: list, grid: Grid) -> int:
        """
        Calculates the score for a player considering their pairs and unpaired cells.

        Parameters:
        -----------
        player_pairs : list
            List of player pairs.
        grid : Grid
            The game grid.

        Returns:
        --------
        int
            The calculated score.
        """
        paired_cells = set(cell for pair in player_pairs for cell in pair)
        score = sum(grid.cost((u,v)) for u, v in player_pairs)
        return score

class Game:
    """Main game class that handles the game loop and user interactions."""

    def __init__(self):
        """Initialize the game with colors and screen setup."""
        self.colors = {
            0: (255, 255, 255),
            1: (199, 14, 14),
            2: (21, 143, 225),
            3: (80, 193, 45),
            4: (0, 0, 0),
            5: (255, 145, 0)
        }
        self.colors_title = {
            0: (0, 0, 0),
            1: (200, 0, 0),
            2: (0, 0, 200),
            3: (0, 200, 0)
        }
        self.screen = pygame.display.set_mode((600, 600))
        pygame.display.set_caption("ColorGrid")
        self.ui_manager = UIManager(self.screen, self.colors, self.colors_title)
        self.grid_manager = GridManager("./input/")
        self.selected_grid = None
        self.scroll = 0
        self.scroll_bar_dragging = False
        self.mouse_y_offset = 0
        self.selected_cells = []
        self.game_over = False
        self.show_solution = False
        self.pressed_button = None
        self.pressed_grid_index = -1
        self.rules_scroll = 0
        self.rules_scroll_bar_dragging = False
        self.rules_mouse_y_offset = 0
        self.player_mode = None
        self.current_player = 1
        self.player_pairs = [[], []]
        self.player_scores = [0, 0]
        self.volume_button_pressed_time = None

    def main(self):
        """Main game loop."""
        while self.selected_grid is None:
            self.screen.fill((255, 255, 255))
            window_size = (600, 600)
            visible_height = window_size[1] - 170
            total_content_height = len(self.grid_manager.grid_files) * 50
            max_scroll = max(0, total_content_height - visible_height)

            scroll_bar_height = max(20, int((visible_height / total_content_height) * visible_height)) if max_scroll > 0 else visible_height
            scroll_percentage = self.scroll / max_scroll if max_scroll > 0 else 0
            scroll_bar_y = 100 + (scroll_percentage * (visible_height - scroll_bar_height))
            scroll_bar_rect = pygame.Rect(580, int(scroll_bar_y), 20, scroll_bar_height)

            self.ui_manager.draw_grid_options(window_size, self.scroll, scroll_bar_rect, scroll_bar_height,
                                            self.grid_manager.grid_files, self.grid_manager.grid_colors, self.pressed_grid_index)
            pygame.draw.rect(self.screen, (255, 255, 255), (0, 0, 600, 100))
            self.ui_manager.draw_title(window_size)
            self.ui_manager.draw_rules_button(window_size, self.pressed_button == 'rules')
            self.ui_manager.draw_volume_button(window_size, self.pressed_button == 'volume')
            current_time = pygame.time.get_ticks()
            if (self.volume_button_pressed_time is not None and current_time - self.volume_button_pressed_time >= 150):
                self.pressed_button = None
                self.volume_button_pressed_time = None
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        x, y = event.pos
                        volume_rect = pygame.Rect(window_size[0] - 95, window_size[1] - 70, 50, 40)
                        if volume_rect.collidepoint(x, y):
                            self.pressed_button = 'volume'
                            self.volume_button_pressed_time = pygame.time.get_ticks()
                            self.ui_manager.toggle_volume()
                        if scroll_bar_rect.collidepoint(x, y) and max_scroll > 0:
                            self.scroll_bar_dragging = True
                            self.mouse_y_offset = y - scroll_bar_rect.y
                        else:
                            self.pressed_grid_index = -1
                            for i in range(len(self.grid_manager.grid_files)):
                                btn_y = 100 + i * 50 - self.scroll
                                if btn_y < 100 or btn_y + 40 > window_size[1] - 70:
                                    continue
                                btn_rect = pygame.Rect(window_size[0] // 2 - 100, btn_y, 200, 40)
                                if btn_rect.collidepoint(x, y):
                                    self.pressed_grid_index = i
                                    break
                            rules_rect = pygame.Rect(window_size[0] - 200, window_size[1] - 70, 100, 40)
                            if rules_rect.collidepoint(x, y):
                                self.pressed_button = 'rules'
                            elif y >= window_size[1] - 40 and x <= 220:
                                self.ui_manager.update_volume((x - 20) / 200)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.pressed_grid_index != -1:
                        x, y = event.pos
                        volume_rect = pygame.Rect(window_size[0] - 95, window_size[1] - 70, 50, 40)
                        if self.pressed_button == 'volume' and volume_rect.collidepoint(x, y):
                            self.ui_manager.toggle_volume()
                        visible_y = y + self.scroll - 100
                        released_index = visible_y // 50

                        if 0 <= released_index < len(self.grid_manager.grid_files) and released_index == self.pressed_grid_index:
                            self.ui_manager.draw_grid_options(window_size, self.scroll, scroll_bar_rect,
                                                            scroll_bar_height, self.grid_manager.grid_files,
                                                            self.grid_manager.grid_colors, self.pressed_grid_index)
                            pygame.display.flip()
                            pygame.time.delay(100)
                            self.selected_grid = self.grid_manager.grid_files[self.pressed_grid_index][0]

                    self.scroll_bar_dragging = False
                    self.pressed_grid_index = -1

                    if self.pressed_button == 'rules':
                        self.screen = pygame.display.set_mode((800, 600))
                        self.show_rules()
                        self.pressed_button = None

                elif event.type == pygame.MOUSEMOTION:
                    if self.scroll_bar_dragging and max_scroll > 0:
                        mouse_y = event.pos[1] - self.mouse_y_offset
                        new_y = max(100, min(mouse_y, 100 + visible_height - scroll_bar_height))
                        self.scroll = ((new_y - 100) / (visible_height - scroll_bar_height)) * max_scroll
                        self.scroll = max(0, min(self.scroll, max_scroll))
                elif event.type == pygame.MOUSEWHEEL:
                    self.scroll -= event.y * 50
                    self.scroll = max(0, min(self.scroll, max_scroll))

        self.player_mode = None
        while self.player_mode is None:
            self.screen.fill((255, 255, 255))
            window_size = (600, 600)
            self.ui_manager.draw_title(window_size)
            self.ui_manager.draw_player_choice(window_size, self.pressed_button)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        x, y = event.pos
                        one_rect = pygame.Rect(window_size[0] // 2 - 100, 200, 220, 60)
                        two_rect = pygame.Rect(window_size[0] // 2 - 100, 300, 220, 60)
                        bot_rect = pygame.Rect(window_size[0] // 2 - 100, 400, 220, 60)
                        if one_rect.collidepoint(x, y):
                            self.pressed_button = 'one'
                        elif two_rect.collidepoint(x, y):
                            self.pressed_button = 'two'
                        elif bot_rect.collidepoint(x, y):
                            self.pressed_button = 'bot'
                        elif y >= window_size[1] - 40 and x <= 220:
                            self.ui_manager.update_volume((x - 20) / 200)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.pressed_button:
                        x, y = event.pos
                        one_rect = pygame.Rect(window_size[0] // 2 - 100, 200, 220, 60)
                        two_rect = pygame.Rect(window_size[0] // 2 - 100, 300, 220, 60)
                        bot_rect = pygame.Rect(window_size[0] // 2 - 100, 400, 220, 60)
                        if one_rect.collidepoint(x, y) and self.pressed_button == 'one':
                            pygame.time.wait(150)
                            self.player_mode = 'one'
                        elif two_rect.collidepoint(x, y) and self.pressed_button == 'two':
                            pygame.time.wait(150)
                            self.player_mode = 'two'
                        elif bot_rect.collidepoint(x, y) and self.pressed_button == 'bot':
                            pygame.time.wait(150)
                            self.player_mode = 'bot'
                        self.pressed_button = None

        grid = self.grid_manager.load_grid(self.selected_grid)
        solver_manager = SolverManager(grid)
        general_score = solver_manager.general_score

        cell_size = 60
        top_margin = 50 if self.player_mode in ['two', 'bot'] else 0
        window_height = grid.n * cell_size + 110 + top_margin
        window_width = max(600, grid.m * cell_size)
        window_size = (window_width, window_height)
        self.screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)
        self.selected_cells = []
        self.game_over = False
        self.show_solution = False
        self.pressed_button = None

        while True:
            if self.player_mode == 'bot' and self.current_player == 2 and not self.game_over:
                grid_copy = Grid(grid.n, grid.m,
                                [row.copy() for row in grid.color],
                                [row.copy() for row in grid.value])

                for pair_list in self.player_pairs:
                    for pair in pair_list:
                        for (i, j) in pair:
                            grid_copy.color[i][j] = 4

                bot_pair = Bot.move_to_play(grid_copy)
                if bot_pair is not None:
                    valid = solver_manager.pair_is_valid(
                        bot_pair, [], grid, self.player_pairs)
                    if valid:
                        pygame.time.wait(1000)
                        self.player_pairs[1].append(bot_pair)
                        self.player_scores[1] = solver_manager.calculate_two_player_score(
                            self.player_pairs[1], grid)
                        self.current_player = 1
                    else:
                        self.game_over = True
                else:
                    self.game_over = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if y >= grid.n * cell_size + top_margin:
                        reset_rect = pygame.Rect(window_size[0] - 225, window_size[1] - 70, 110, 40) if self.player_mode in ['two', 'bot'] else pygame.Rect(window_size[0] - 330, window_size[1] - 70, 100, 40)
                        solution_rect = pygame.Rect(window_size[0] - 225, window_size[1] - 70, 110, 40) if self.player_mode == 'one' else None
                        menu_rect = pygame.Rect(window_size[0] - 110, window_size[1] - 70, 100, 40)

                        if reset_rect.collidepoint(x, y):
                            self.pressed_button = 'reset'
                        elif solution_rect and solution_rect.collidepoint(x, y):
                            self.pressed_button = 'solution'
                        elif menu_rect.collidepoint(x, y):
                            self.pressed_button = 'menu'
                        elif y >= window_size[1] - 40 and x <= 220:
                            self.ui_manager.update_volume((x - 20) / 200)
                        else:
                            self.pressed_button = None
                    else:
                        i, j = (y - top_margin) // cell_size, x // cell_size
                        if 0 <= i < grid.n and 0 <= j < grid.m:
                            if grid.is_forbidden(i, j):
                                self.ui_manager.draw_error_message("Invalid pair!", window_size, self.player_mode, cell_size)
                                self.selected_cells = []
                            elif (i, j) in [cell for pair in solver_manager.solver.pairs for cell in pair]:
                                for pair in solver_manager.solver.pairs:
                                    if (i, j) in pair:
                                        solver_manager.solver.pairs.remove(pair)
                                        break
                            elif (i, j) not in [cell for pair in solver_manager.solver.pairs for cell in pair]:
                                self.selected_cells.append((i, j))
                                if len(self.selected_cells) == 2:
                                    if self.selected_cells[1] in grid.vois(self.selected_cells[0][0], self.selected_cells[0][1]):
                                        color1 = grid.color[self.selected_cells[0][0]][self.selected_cells[0][1]]
                                        color2 = grid.color[self.selected_cells[1][0]][self.selected_cells[1][1]]
                                        if solver_manager.can_pair(color1, color2):
                                            if self.player_mode == 'one':
                                                solver_manager.solver.pairs.append((self.selected_cells[0], self.selected_cells[1]))
                                            elif self.player_mode == 'bot':
                                                valid = solver_manager.pair_is_valid(
                                                    (self.selected_cells[0], self.selected_cells[1]),
                                                    [], grid, self.player_pairs)
                                                if valid:
                                                    self.player_pairs[0].append((self.selected_cells[0], self.selected_cells[1]))
                                                    self.player_scores[0] = solver_manager.calculate_two_player_score(self.player_pairs[0], grid)
                                                    self.current_player = 2
                                                else:
                                                    self.ui_manager.draw_error_message("Invalid pair!", window_size, self.player_mode, cell_size)
                                            else:
                                                if solver_manager.pair_is_valid((self.selected_cells[0], self.selected_cells[1]), solver_manager.solver.pairs, grid, self.player_pairs):
                                                    self.player_pairs[self.current_player - 1].append((self.selected_cells[0], self.selected_cells[1]))
                                                    self.player_scores[self.current_player - 1] = solver_manager.calculate_two_player_score(self.player_pairs[self.current_player - 1], grid)
                                                    self.current_player = 2 if self.current_player == 1 else 1
                                                else:
                                                    self.ui_manager.draw_error_message("Invalid pair!", window_size, self.player_mode, cell_size)
                                        else:
                                            self.ui_manager.draw_error_message("Invalid pair!", window_size, self.player_mode, cell_size)
                                    else:
                                        self.ui_manager.draw_error_message("Invalid pair!", window_size, self.player_mode, cell_size)
                                    self.selected_cells = []
                            self.pressed_button = None
                elif event.type == pygame.MOUSEBUTTONUP:
                    x, y = event.pos
                    if self.pressed_button:
                        button_rect = None
                        if self.pressed_button == 'reset':
                            button_rect = pygame.Rect(window_size[0] - 225, window_size[1] - 70, 110, 40) if self.player_mode in ['two', 'bot'] else pygame.Rect(window_size[0] - 330, window_size[1] - 70, 100, 40)
                        elif self.pressed_button == 'solution' and self.player_mode == 'one':
                            button_rect = pygame.Rect(window_size[0] - 225, window_size[1] - 70, 110, 40)
                        elif self.pressed_button == 'menu':
                            button_rect = pygame.Rect(window_size[0] - 110, window_size[1] - 70, 100, 40)
                            self.reset_game_state()
                            pygame.time.wait(150)

                        if button_rect and button_rect.collidepoint(x, y):
                            if self.pressed_button == 'menu':
                                self.reset_game_state()
                                pygame.time.delay(150)

                            if self.pressed_button == 'reset':
                                solver_manager.solver.pairs = []
                                self.selected_cells = []
                                self.game_over = False
                                self.show_solution = False
                                self.player_pairs = [[], []]
                                self.current_player = 1
                                self.player_scores = [0, 0]
                            elif self.pressed_button == 'solution':
                                solver_manager.solver.pairs = solver_manager.solver_general.pairs
                                self.show_solution = True
                            elif self.pressed_button == 'menu':
                                self.reset_game_state()
                                pygame.time.wait(150)

                        self.pressed_button = None

            self.screen.fill((220, 220, 220))
            self.ui_manager.draw_grid(grid, solver_manager.solver, cell_size, self.selected_cells, self.player_mode, self.player_pairs, top_margin)
            self.ui_manager.draw_score(solver_manager.solver, window_size, cell_size, self.player_scores[0], self.player_scores[1], self.player_mode)

            if self.player_mode == 'two':
                self.ui_manager.draw_turn_indicator(self.current_player, window_size, top_margin, 'two')
                self.ui_manager.draw_restart_button(window_size, self.pressed_button == 'reset', self.player_mode)
            if self.player_mode == 'bot':
                self.ui_manager.draw_turn_indicator(self.current_player, window_size, top_margin, 'bot')
                self.ui_manager.draw_restart_button(window_size, self.pressed_button == 'reset', self.player_mode)
            if self.player_mode == 'one':
                self.ui_manager.draw_solution_button(window_size, self.pressed_button == 'solution')
                self.ui_manager.draw_restart_button(window_size, self.pressed_button == 'reset', self.player_mode)
            self.ui_manager.draw_menu_button(window_size, self.pressed_button == 'menu')

            pygame.display.flip()

            if not self.show_solution and not any(
                solver_manager.pair_is_valid(pair, solver_manager.solver.pairs, grid, self.player_pairs)
                for pair in grid.all_pairs()
            ):
                if not self.game_over:
                    self.game_over = True
                    if self.player_mode == 'one':
                        if solver_manager.solver.score() <= general_score:
                            self.ui_manager.win_sound.play()
                            self.ui_manager.draw_end_screen("You won!", (0, 200, 0), window_size)
                        else:
                            self.ui_manager.lose_sound.play()
                            self.ui_manager.draw_end_screen("You lost!", (200, 0, 0), window_size)
                        solver_manager.solver.pairs = []
                        self.selected_cells = []
                        self.game_over = False
                    elif self.player_mode == 'two':
                        if self.player_scores[0] < self.player_scores[1]:
                            self.ui_manager.win_sound.play()
                            self.ui_manager.draw_end_screen("Player 1 has won!", self.colors[5], window_size)
                        elif self.player_scores[1] < self.player_scores[0]:
                            self.ui_manager.lose_sound.play()
                            self.ui_manager.draw_end_screen("Player 2 has won!", (148, 0, 211), window_size)
                        else:
                            self.ui_manager.lose_sound.play()
                            self.ui_manager.draw_end_screen("It's a tie!", (0, 255, 255), window_size)
                        self.player_pairs = [[], []]
                        self.player_scores = [0, 0]
                        self.current_player = 1
                        self.game_over = False
                    elif self.player_mode == 'bot':
                        if self.player_scores[0] < self.player_scores[1]:
                            self.ui_manager.win_sound.play()
                            self.ui_manager.draw_end_screen("You won!", self.colors[5], window_size)
                        elif self.player_scores[1] < self.player_scores[0]:
                            self.ui_manager.lose_sound.play()
                            self.ui_manager.draw_end_screen("Stockfish wins!", (148, 0, 211), window_size)
                        else:
                            self.ui_manager.lose_sound.play()
                            self.ui_manager.draw_end_screen("It's a tie!", (0, 255, 255), window_size)
                        self.player_pairs = [[], []]
                        self.player_scores = [0, 0]
                        self.current_player = 1
                        self.game_over = False

    def show_rules(self):
        """Displays the game rules screen."""
        window_size = (800, 600)
        visible_height = window_size[1] - 170
        line_height = 30
        total_lines = 22
        total_content_height = total_lines * line_height
        max_scroll = max(0, total_content_height - visible_height)
        scroll_bar_height = max(20, int((visible_height / total_content_height) * visible_height)) if max_scroll > 0 else visible_height

        while True:
            scroll_percentage = self.rules_scroll / max_scroll if max_scroll > 0 else 0
            scroll_bar_y = 100 + (scroll_percentage * (visible_height - scroll_bar_height))
            scroll_bar_rect = pygame.Rect(780, int(scroll_bar_y), 20, scroll_bar_height)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        x, y = event.pos
                        if scroll_bar_rect.collidepoint(x, y) and max_scroll > 0:
                            self.rules_scroll_bar_dragging = True
                            self.rules_mouse_y_offset = y - scroll_bar_rect.y
                        else:
                            menu_rect = pygame.Rect(window_size[0] - 110, window_size[1] - 70, 100, 40)
                            if menu_rect.collidepoint(x, y):
                                self.pressed_button = 'menu'

                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.pressed_button == 'menu':
                        self.reset_game_state()
                        x, y = event.pos
                        menu_rect = pygame.Rect(window_size[0] - 110, window_size[1] - 70, 100, 40)
                        if menu_rect.collidepoint(x, y):
                            self.ui_manager.draw_menu_button(window_size, True)
                            pygame.display.update(menu_rect)
                            pygame.time.delay(100)
                            self.reset_game_state()
                            return
                    self.pressed_button = None
                    self.rules_scroll_bar_dragging = False

                elif event.type == pygame.MOUSEMOTION:
                    if self.rules_scroll_bar_dragging and max_scroll > 0:
                        mouse_y = event.pos[1] - self.rules_mouse_y_offset
                        new_y = max(100, min(mouse_y, 100 + visible_height - scroll_bar_height))
                        self.rules_scroll = ((new_y - 100) / (visible_height - scroll_bar_height)) * max_scroll
                        self.rules_scroll = max(0, min(self.rules_scroll, max_scroll))

                elif event.type == pygame.MOUSEWHEEL:
                    self.rules_scroll -= event.y * 30
                    self.rules_scroll = max(0, min(self.rules_scroll, max_scroll))

            self.screen.fill((255, 255, 255))
            self.ui_manager.draw_rules(window_size, self.rules_scroll, scroll_bar_rect, scroll_bar_height)
            self.ui_manager.draw_menu_button(window_size, self.pressed_button == 'menu')
            pygame.display.flip()

    def reset_game_state(self):
        """Resets the game state to the initial menu and clears the grid."""
        self.selected_grid = None
        self.scroll = 0
        self.scroll_bar_dragging = False
        self.mouse_y_offset = 0
        self.selected_cells = []
        self.game_over = False
        self.show_solution = False
        self.pressed_button = None
        self.pressed_grid_index = -1
        self.rules_scroll = 0
        self.rules_scroll_bar_dragging = False
        self.rules_mouse_y_offset = 0
        self.player_scores = [0, 0]
        self.player_pairs = [[], []]
        self.current_player = 1
        self.screen = pygame.display.set_mode((600, 600))
        self.main()

if __name__ == "__main__":
    game = Game()
    game.main()

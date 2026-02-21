import pygame
import chess
import stockfish
import os
import json
from typing import Dict

pygame.init()
pygame.font.init()
pygame.mixer.init()

class ChessGame:
    def __init__(self):
        self.screen_width, self.screen_height = 1400, 800
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("Chess AI - Unbeatable Stockfish")
        
        self.clock = pygame.time.Clock()
        self.elo_ratings = self.load_elo()
        self.player_elo = self.elo_ratings.get("player", 1200)
        self.ai_elo = self.elo_ratings.get("ai", 1600)
        
        self.engine = stockfish.Stockfish(path="./stockfish.exe")
        self.difficulty = "unbeatable"
        
        self.square_size = (self.screen_height - 150) // 8
        self.board_offset = (80, 100)
        self.font = pygame.font.Font(None, 32)
        self.big_font = pygame.font.Font(None, 64)
        
        self.light_square = (245, 222, 179)
        self.dark_square  = (139, 69, 19)
        self.select_color = (255, 255, 0, 100)
        self.move_color = (0, 255, 0, 100)
        self.last_move_color = (255, 255, 0, 80)

        self.piece_images = {}
        self.load_pieces()
        self.load_sounds()
        
        self.reset_game()
        self.piece_images = {}
        self.load_pieces()
    
    def handle_resize(self, event):
        self.screen_width, self.screen_height = event.w, event.h
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        # Reduced vertical padding from 100 to 50 to allow a taller board
        self.square_size = min((self.screen_width - 350) // 8, (self.screen_height - 50) // 8)
        self.load_pieces() # Important: Re-scale the piece images to the new size
    
    def load_pieces(self):
        piece_names = {
            chess.PAWN: "pawn", chess.KNIGHT: "knight", chess.BISHOP: "bishop",
            chess.ROOK: "rook", chess.QUEEN: "queen", chess.KING: "king",
        }
        for piece_type, name in piece_names.items():
            for color, color_name in [(chess.WHITE, "white"), (chess.BLACK, "black")]:
                img_path = os.path.join("assets", "pieces", f"{color_name}_{name}.png")
                try:
                    img = pygame.image.load(img_path).convert_alpha()
                    # Scale to the NEW square_size
                    img = pygame.transform.smoothscale(img, (self.square_size, self.square_size))
                    self.piece_images[(piece_type, color)] = img
                except Exception as e:
                    print(f"Could not load {img_path}: {e}")
                    
    def __del__(self):
        """Ensures the Stockfish process is terminated when the object is destroyed."""
        if hasattr(self, 'engine'):
            del self.engine
    
    def reset_game(self):
        self.board = chess.Board()
        self.selected_square = None
        self.legal_moves = []
        self.game_history = []
        self.game_over = False
        self.winner = None
        self.pending_promotion = None
    
    def undo_move(self):
        """Undoes the last full turn (AI's move and Player's move)."""
        # If at least 2 moves have been made, undo both so it's the player's turn again
        if len(self.game_history) >= 2:
            self.board.pop() # Undo AI move
            self.board.pop() # Undo Player move
            self.game_history.pop()
            self.game_history.pop()
            
        # If only 1 move was made (e.g., game ended immediately or testing), just undo 1
        elif len(self.game_history) == 1:
            self.board.pop()
            self.game_history.pop()
            
        # Reset game states so you can continue playing
        self.game_over = False
        self.winner = None
        self.selected_square = None
        self.legal_moves = []
        self.pending_promotion = None

    def load_pieces(self):
        self.piece_images.clear()
        piece_names = {chess.PAWN: "pawn", chess.KNIGHT: "knight", chess.BISHOP: "bishop",
                       chess.ROOK: "rook", chess.QUEEN: "queen", chess.KING: "king"}
        for piece_type, name in piece_names.items():
            for color, color_name in [(chess.WHITE, "white"), (chess.BLACK, "black")]:
                img_path = os.path.join("assets", "pieces", f"{color_name}_{name}.png")
                try:
                    img = pygame.image.load(img_path).convert_alpha()
                    img = pygame.transform.smoothscale(img, (self.square_size, self.square_size))
                    self.piece_images[(piece_type, color)] = img
                except FileNotFoundError: pass 

    def load_sounds(self):
        try:
            self.move_sound = pygame.mixer.Sound(os.path.join("assets", "sounds", "move.wav"))
            self.capture_sound = pygame.mixer.Sound(os.path.join("assets", "sounds", "capture.wav"))
            self.check_sound = pygame.mixer.Sound(os.path.join("assets", "sounds", "check.wav")) # NEW
        except (FileNotFoundError, pygame.error):
            self.move_sound = self.capture_sound = self.check_sound = None

    def play_move_sound(self, move: chess.Move):
        # We check is_check() AFTER pushing the move, but is_capture() BEFORE.
        # So we handle logic inside the move execution loop instead.
        pass
                    
    def execute_move(self, move):
        """Helper to play sounds and push move correctly."""
        is_cap = self.board.is_capture(move)
        self.board.push(move)
        self.game_history.append(move)
        
        # Priority: Check sound > Capture sound > Move sound
        if self.board.is_check():
            if self.check_sound: self.check_sound.play()
        elif is_cap:
            if self.capture_sound: self.capture_sound.play()
        elif self.move_sound:
            self.move_sound.play()
            
        self.check_game_over()

    def load_elo(self) -> Dict[str, float]:
        if os.path.exists("elo.json"):
            with open("elo.json", "r") as f: return json.load(f)
        return {"player": 1200, "ai": 1600}
    
    def save_elo(self):
        with open("elo.json", "w") as f: json.dump(self.elo_ratings, f)
    
    def update_elo(self, player_won: bool):
        K = 32
        expected = 1 / (1 + 10**((self.ai_elo - self.player_elo) / 400))
        self.player_elo += K * ((1.0 if player_won else 0.0) - expected)
        self.ai_elo += K * ((0.0 if player_won else 1.0) - (1-expected))
        self.elo_ratings = {"player": self.player_elo, "ai": self.ai_elo}
        self.save_elo()
    
    def get_ai_move(self) -> chess.Move:
        self.engine.set_fen_position(self.board.fen())
        levels = {"easy": (0, 1), "medium": (5, 5), "hard": (15, 10), "unbeatable": (20, 20)}
        skill, depth = levels.get(self.difficulty, (20, 20))
        self.engine.set_skill_level(skill)
        self.engine.set_depth(depth)
        uci_move = self.engine.get_best_move()
        return self.board.parse_uci(uci_move) if uci_move else None
    
    def pixel_to_square(self, pos: tuple) -> chess.Square:
        x, y = pos
        col = (x - self.board_offset[0]) // self.square_size
        row = 7 - (y - self.board_offset[1]) // self.square_size
        return chess.square(col, row) if 0 <= row < 8 and 0 <= col < 8 else None
    
    def draw_board(self):
        board_rect = pygame.Rect(self.board_offset[0], self.board_offset[1], self.square_size * 8, self.square_size * 8)
        pygame.draw.rect(self.screen, (60, 60, 60), board_rect, 3)
        for row in range(8):
            for col in range(8):
                color = self.light_square if (row + col) % 2 == 0 else self.dark_square
                rect = pygame.Rect(self.board_offset[0] + col * self.square_size, self.board_offset[1] + row * self.square_size, self.square_size, self.square_size)
                pygame.draw.rect(self.screen, color, rect)
                if self.selected_square == chess.square(col, 7-row):
                    pygame.draw.rect(self.screen, self.select_color, rect, 4)
        if self.game_history:
            last_move = self.game_history[-1]
            highlight = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
            highlight.fill(self.last_move_color)
            for sq in [last_move.from_square, last_move.to_square]:
                self.screen.blit(highlight, (self.board_offset[0] + chess.square_file(sq) * self.square_size, self.board_offset[1] + (7 - chess.square_rank(sq)) * self.square_size))
        for move in self.legal_moves:
            center = (self.board_offset[0] + chess.square_file(move.to_square) * self.square_size + self.square_size // 2, self.board_offset[1] + (7 - chess.square_rank(move.to_square)) * self.square_size + self.square_size // 2)
            pygame.draw.circle(self.screen, self.move_color, center, self.square_size // 6)
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                img = self.piece_images.get((piece.piece_type, piece.color))
                if img: self.screen.blit(img, (self.board_offset[0] + chess.square_file(square) * self.square_size, self.board_offset[1] + (7 - chess.square_rank(square)) * self.square_size))

    def draw_promotion_menu(self):
        if not self.pending_promotion: return
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        menu_w, menu_h = self.square_size * 4, self.square_size
        start_x, start_y = (self.screen_width - menu_w) // 2, (self.screen_height - menu_h) // 2
        pygame.draw.rect(self.screen, (220, 220, 220), (start_x, start_y, menu_w, menu_h))
        pieces = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
        for i, pt in enumerate(pieces):
            img = self.piece_images.get((pt, self.board.turn))
            if img: self.screen.blit(img, (start_x + i * self.square_size, start_y))

    def draw_ui(self):
        y_off = self.board_offset[1]
        
        # 1. Draw the Title
        # Draw title 60 pixels ABOVE the board
        title_surface = self.big_font.render("Python Chess (Stockfish)", True, (30, 30, 30))
        self.screen.blit(title_surface, (self.board_offset[0], self.board_offset[1] - 70))
        self.screen.blit(self.big_font.render("Python Chess (Stockfish)", True, (30, 30, 30)), (self.board_offset[0] + 8 * self.square_size + 20, y_off - 60))
        
        # 2. Visual "CHECK" indicator
        if self.board.is_check():
            check_txt = self.font.render("!! CHECK !!", True, (200, 0, 0))
            # Placed slightly lower so it doesn't overlap with the stats
            self.screen.blit(check_txt, (self.board_offset[0] + 8 * self.square_size + 20, y_off + 200))

        # 3. Game Stats and Controls (Updated with Undo)
        info = [
            f"Player ELO: {self.player_elo:.0f}", 
            f"AI ELO: {self.ai_elo:.0f}", 
            f"Difficulty: {self.difficulty.capitalize()}", 
            f"Turn: {'White' if self.board.turn == chess.WHITE else 'Black'}", 
            "", 
            "Controls:", 
            "1–4: Difficulty", 
            "Backspace: Undo Move",   # NEW: Added instruction here
            "R: Reset | Q: Quit"
        ]
        
        for i, text in enumerate(info):
            self.screen.blit(self.font.render(text, True, (50, 50, 50)), (self.board_offset[0] + 8 * self.square_size + 20, y_off + i * 40))

        # 4. Game Over Overlay
        if self.game_over:
            txt = "Game Drawn!" if self.winner is None else f"{'Player Wins!' if self.winner == chess.WHITE else 'AI Wins!'}"
            rendered = self.big_font.render(txt + " (Press R to Restart)", True, (255, 0, 0))
            self.screen.blit(rendered, rendered.get_rect(center=(self.screen_width // 2, self.screen_height // 2)))
            
    def check_game_over(self):
        if self.board.is_game_over():
            self.game_over = True
            res = self.board.result()
            if res == "1-0": self.winner = chess.WHITE; self.update_elo(True)
            elif res == "0-1": self.winner = chess.BLACK; self.update_elo(False)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                elif event.type == pygame.KEYDOWN:
                    diffs = {pygame.K_1: "easy", pygame.K_2: "medium", pygame.K_3: "hard", pygame.K_4: "unbeatable"}
                    if event.key in diffs: self.difficulty = diffs[event.key]
                    elif event.key == pygame.K_r: self.reset_game()
                    elif event.key == pygame.K_q: running = False
                    elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_LEFT: 
                        self.undo_move() # NEW: Triggers the undo action
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    pos = pygame.mouse.get_pos()
                    if self.pending_promotion:
                        start_x = (self.screen_width - self.square_size * 4) // 2
                        start_y = (self.screen_height - self.square_size) // 2
                        if start_y <= pos[1] <= start_y + self.square_size:
                            idx = int((pos[0] - start_x) // self.square_size)
                            if 0 <= idx < 4:
                                move = chess.Move(self.pending_promotion[0], self.pending_promotion[1], promotion=[chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT][idx])
                                self.execute_move(move)
                        self.pending_promotion = self.selected_square = None
                        self.legal_moves = []
                        continue
                    square = self.pixel_to_square(pos)
                    if square is not None:
                        if self.selected_square == square: self.selected_square = None; self.legal_moves = []
                        elif self.selected_square is None and self.board.piece_at(square) and self.board.piece_at(square).color == self.board.turn:
                            self.selected_square = square
                            self.legal_moves = [m for m in self.board.legal_moves if m.from_square == square]
                        elif self.selected_square is not None:
                            move = next((m for m in self.legal_moves if m.to_square == square), None)
                            if move:
                                if move.promotion: self.pending_promotion = (self.selected_square, square)
                                else: self.execute_move(move); self.selected_square = None; self.legal_moves = []
                            else: self.selected_square = None; self.legal_moves = []
            
            if self.board.turn == chess.BLACK and not self.game_over and not self.selected_square and not self.pending_promotion:
                move = self.get_ai_move()
                if move: self.execute_move(move)
            
            self.screen.fill((255, 255, 255))
            self.draw_board(); self.draw_ui(); self.draw_promotion_menu()
            pygame.display.flip(); self.clock.tick(60)
        del self.engine
        pygame.quit()

if __name__ == "__main__":
    game = ChessGame()
    game.run()
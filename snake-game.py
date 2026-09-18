import json
import random
import tkinter as tk
from pathlib import Path


class SnakeGame:
	CELL_SIZE = 24
	GRID_WIDTH = 25
	GRID_HEIGHT = 22
	BOARD_WIDTH = CELL_SIZE * GRID_WIDTH
	BOARD_HEIGHT = CELL_SIZE * GRID_HEIGHT
	BACKGROUND = "#08111f"
	PANEL = "#101c2e"
	GRID = "#14263a"
	TEXT = "#e8f1f7"
	MUTED = "#8da3b5"
	ACCENT = "#52e0a4"
	FOOD = "#ff6b6b"

	def __init__(self, root):
		self.root = root
		self.root.title("Neon Snake")
		self.root.configure(bg=self.BACKGROUND)
		self.root.resizable(False, False)
		self.high_score_path = Path(__file__).with_name("snake-high-score.json")
		self.high_score = self.load_high_score()
		self.speed_options = {"Chill": 165, "Classic": 115, "Turbo": 78}
		self.speed_name = tk.StringVar(value="Classic")

		self.build_interface()
		self.bind_keys()
		self.reset_game()
		self.root.after(120, self.draw)

	def build_interface(self):
		header = tk.Frame(self.root, bg=self.BACKGROUND)
		header.pack(fill="x", padx=22, pady=(18, 10))

		title = tk.Label(
			header,
			text="NEON SNAKE",
			font=("Segoe UI", 21, "bold"),
			fg=self.ACCENT,
			bg=self.BACKGROUND,
		)
		title.pack(side="left")

		stats = tk.Frame(header, bg=self.BACKGROUND)
		stats.pack(side="right")
		self.score_label = self.make_stat(stats, "SCORE")
		self.best_label = self.make_stat(stats, "BEST")

		self.canvas = tk.Canvas(
			self.root,
			width=self.BOARD_WIDTH,
			height=self.BOARD_HEIGHT,
			bg=self.BACKGROUND,
			highlightthickness=1,
			highlightbackground="#20364d",
		)
		self.canvas.pack(padx=22, pady=4)

		footer = tk.Frame(self.root, bg=self.BACKGROUND)
		footer.pack(fill="x", padx=22, pady=(10, 20))

		self.status_label = tk.Label(
			footer,
			text="",
			font=("Segoe UI", 10),
			fg=self.MUTED,
			bg=self.BACKGROUND,
			anchor="w",
		)
		self.status_label.pack(side="left")

		speed_menu = tk.OptionMenu(
			footer,
			self.speed_name,
			*self.speed_options,
			command=self.change_speed,
		)
		speed_menu.configure(
			bg=self.PANEL,
			fg=self.TEXT,
			activebackground="#20364d",
			activeforeground=self.TEXT,
			highlightthickness=0,
			bd=0,
			font=("Segoe UI", 9),
		)
		speed_menu["menu"].configure(bg=self.PANEL, fg=self.TEXT)
		speed_menu.pack(side="right")

	def make_stat(self, parent, label):
		block = tk.Frame(parent, bg=self.BACKGROUND)
		block.pack(side="left", padx=(18, 0))
		value = tk.Label(
			block,
			text="0",
			font=("Segoe UI", 15, "bold"),
			fg=self.TEXT,
			bg=self.BACKGROUND,
		)
		value.pack()
		tk.Label(
			block,
			text=label,
			font=("Segoe UI", 8, "bold"),
			fg=self.MUTED,
			bg=self.BACKGROUND,
		).pack()
		return value

	def bind_keys(self):
		self.root.bind("<KeyPress>", self.handle_key)
		self.root.bind("<FocusIn>", lambda _event: self.canvas.focus_set())
		self.canvas.focus_set()

	def reset_game(self):
		center = (self.GRID_WIDTH // 2, self.GRID_HEIGHT // 2)
		self.snake = [center, (center[0] - 1, center[1]), (center[0] - 2, center[1])]
		self.direction = (1, 0)
		self.next_direction = self.direction
		self.food = self.place_food()
		self.score = 0
		self.state = "ready"
		self.update_hud()

	def start_game(self):
		if self.state in ("ready", "game_over"):
			self.reset_game()
		self.state = "running"
		self.status_label.configure(text="Arrow keys / WASD to move   |   P to pause   |   R to restart")
		self.canvas.focus_set()

	def toggle_pause(self):
		if self.state == "running":
			self.state = "paused"
		elif self.state == "paused":
			self.state = "running"
		self.update_hud()

	def handle_key(self, event):
		key = event.keysym.lower()
		directions = {
			"up": (0, -1), "w": (0, -1),
			"down": (0, 1), "s": (0, 1),
			"left": (-1, 0), "a": (-1, 0),
			"right": (1, 0), "d": (1, 0),
		}
		if key in directions:
			candidate = directions[key]
			if self.state in ("ready", "game_over"):
				self.start_game()
			if candidate != (-self.direction[0], -self.direction[1]):
				self.next_direction = candidate
		elif key == "p" and self.state in ("running", "paused"):
			self.toggle_pause()
		elif key == "r":
			self.start_game()
		elif key in ("space", "return") and self.state in ("ready", "game_over"):
			self.start_game()

	def change_speed(self, _selection=None):
		self.update_hud()

	def place_food(self):
		available = [
			(x, y)
			for x in range(self.GRID_WIDTH)
			for y in range(self.GRID_HEIGHT)
			if (x, y) not in self.snake
		]
		return random.choice(available) if available else None

	def update(self):
		if self.state != "running":
			return

		self.direction = self.next_direction
		head_x, head_y = self.snake[0]
		new_head = (head_x + self.direction[0], head_y + self.direction[1])
		hit_wall = not (0 <= new_head[0] < self.GRID_WIDTH and 0 <= new_head[1] < self.GRID_HEIGHT)
		will_eat = new_head == self.food
		hit_body = new_head in (self.snake if will_eat else self.snake[:-1])

		if hit_wall or hit_body:
			self.finish_game()
			return

		self.snake.insert(0, new_head)
		if will_eat:
			self.score += 10
			self.food = self.place_food()
			if self.food is None:
				self.finish_game(won=True)
		else:
			self.snake.pop()

		self.update_hud()

	def finish_game(self, won=False):
		self.state = "won" if won else "game_over"
		if self.score > self.high_score:
			self.high_score = self.score
			self.save_high_score()
		self.update_hud()

	def update_hud(self):
		self.score_label.configure(text=str(self.score))
		self.best_label.configure(text=str(max(self.high_score, self.score)))
		if self.state == "ready":
			self.status_label.configure(text="Press SPACE or an arrow key to begin")
		elif self.state == "paused":
			self.status_label.configure(text="PAUSED   |   Press P to resume")
		elif self.state == "game_over":
			self.status_label.configure(text="Game over   |   Press R or SPACE to try again")
		elif self.state == "won":
			self.status_label.configure(text="Board cleared   |   Press R to play again")

	def draw(self):
		self.update()
		self.canvas.delete("all")
		self.draw_grid()

		if self.food:
			self.draw_food(self.food)
		for index, segment in enumerate(reversed(self.snake)):
			self.draw_segment(segment, index == len(self.snake) - 1)

		if self.state != "running":
			self.draw_overlay()
		self.root.after(self.speed_options[self.speed_name.get()], self.draw)

	def draw_grid(self):
		for x in range(0, self.BOARD_WIDTH, self.CELL_SIZE):
			self.canvas.create_line(x, 0, x, self.BOARD_HEIGHT, fill=self.GRID)
		for y in range(0, self.BOARD_HEIGHT, self.CELL_SIZE):
			self.canvas.create_line(0, y, self.BOARD_WIDTH, y, fill=self.GRID)

	def draw_segment(self, position, is_head):
		x, y = position
		inset = 3 if is_head else 4
		color = "#a4f5cf" if is_head else self.ACCENT
		self.canvas.create_rectangle(
			x * self.CELL_SIZE + inset,
			y * self.CELL_SIZE + inset,
			(x + 1) * self.CELL_SIZE - inset,
			(y + 1) * self.CELL_SIZE - inset,
			fill=color,
			outline="",
		)
		if is_head:
			eye_x = x * self.CELL_SIZE + (16 if self.direction[0] >= 0 else 7)
			eye_y = y * self.CELL_SIZE + (7 if self.direction[1] >= 0 else 16)
			self.canvas.create_oval(eye_x - 2, eye_y - 2, eye_x + 2, eye_y + 2, fill=self.BACKGROUND)

	def draw_food(self, position):
		x, y = position
		center_x = x * self.CELL_SIZE + self.CELL_SIZE // 2
		center_y = y * self.CELL_SIZE + self.CELL_SIZE // 2
		self.canvas.create_oval(
			center_x - 8, center_y - 8, center_x + 8, center_y + 8,
			fill=self.FOOD, outline="#ff9b8d", width=2,
		)

	def draw_overlay(self):
		self.canvas.create_rectangle(
			0, 0, self.BOARD_WIDTH, self.BOARD_HEIGHT,
			fill="#08111f", stipple="gray50", outline="",
		)
		messages = {
			"ready": ("READY?", "Eat the red food. Stay alive."),
			"paused": ("PAUSED", "Press P when you are ready to move."),
			"game_over": ("GAME OVER", f"Final score: {self.score}"),
			"won": ("PERFECT RUN", "You filled the whole board!"),
		}
		headline, subhead = messages[self.state]
		self.canvas.create_text(
			self.BOARD_WIDTH // 2, self.BOARD_HEIGHT // 2 - 22,
			text=headline, fill=self.TEXT, font=("Segoe UI", 25, "bold"),
		)
		self.canvas.create_text(
			self.BOARD_WIDTH // 2, self.BOARD_HEIGHT // 2 + 18,
			text=subhead, fill=self.MUTED, font=("Segoe UI", 11),
		)

	def load_high_score(self):
		try:
			return int(json.loads(self.high_score_path.read_text(encoding="utf-8"))["high_score"])
		except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
			return 0

	def save_high_score(self):
		try:
			self.high_score_path.write_text(
				json.dumps({"high_score": self.high_score}), encoding="utf-8"
			)
		except OSError:
			pass


if __name__ == "__main__":
	window = tk.Tk()
	SnakeGame(window)
	window.mainloop()

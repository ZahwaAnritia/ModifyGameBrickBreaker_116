import tkinter as tk
import random
import winsound  


class BrickBreaker:
    def __init__(self, root):
        self.root = root
        self.root.title("Brick Breaker")
        self.width = 500
        self.height = 400
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="#FFB6C1")  # Background pink muda
        self.canvas.pack()
        self.canvas.bind("<z>", self.toggle_pause)

        # HUD
        self.lives = 3
        self.score = 0
        self.level = 1


        self.hud_lives = None
        self.hud_score = None

        # Paddle
        self.paddle = self.canvas.create_rectangle(250, 360, 350, 370, fill="blue")
        self.canvas.bind("<Motion>", self.move_paddle)

        # Ball
        self.ball = self.canvas.create_oval(290, 340, 310, 360, fill="red")
        self.ball_dx = 3
        self.ball_dy = -3

        # Bricks
        self.bricks = []
        self.create_bricks()

        # Game loop
        self.running = False  # Game tidak langsung berjalan
        self.waiting_to_start = True
        self.start_text = self.canvas.create_text(self.width / 2, self.height / 2,
                                                  text="Press Space to Start",
                                                  font=("Courier New", 24, "bold"), fill="black")
        self.update_hud()

        # Binding tombol Space untuk memulai permainan
        self.canvas.focus_set()
        self.canvas.bind("<space>", self.start_game)
        self.canvas.bind("<Left>", self.move_left)
        self.canvas.bind("<Right>", self.move_right)

    def toggle_pause(self, event=None):
        """Menjeda atau melanjutkan permainan."""
        if self.running:
            self.running = False
            self.pause_text = self.canvas.create_text(self.width / 2, self.height / 2,
                                                  text="Game Paused\nPress 'Z' to Resume",
                                                  font=("Courier New", 24, "bold"), fill="black")
        else:
            self.running = True
            self.canvas.delete(self.pause_text)
            self.animate()

    def create_bricks(self):
        """Membuat brick dengan kekerasan berbeda berdasarkan posisinya."""
        rows = 3  
        columns = 6  
        brick_colors = ["#FF6347", "#FFD700", "#32CD32"]  
        brick_strengths = [3, 2, 1]  

        for i in range(columns):
            for j in range(rows):
                x1 = i * 80 + 10
                y1 = j * 25 + 10
                x2 = x1 + 70
                y2 = y1 + 20

                # Atur kekerasan dan warna berdasarkan posisi baris
                color = brick_colors[j]
                strength = brick_strengths[j]

                brick_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags="brick")
                self.bricks.append({"id": brick_id, "strength": strength})

    def move_paddle(self, event):
        """Menggerakkan paddle berdasarkan posisi mouse."""
        paddle_width = self.canvas.coords(self.paddle)[2] - self.canvas.coords(self.paddle)[0]
        if event.x > paddle_width / 2 and event.x < self.width - paddle_width / 2:
            self.canvas.coords(self.paddle, event.x - paddle_width / 2, 360, event.x + paddle_width / 2, 370)

    def move_left(self, event):
        """Menggerakkan paddle ke kiri dengan tombol kiri."""
        paddle_coords = self.canvas.coords(self.paddle)
        if paddle_coords[0] > 0:
            self.canvas.move(self.paddle, -10, 0)

    def move_right(self, event):
        """Menggerakkan paddle ke kanan dengan tombol kanan."""
        paddle_coords = self.canvas.coords(self.paddle)
        if paddle_coords[2] < self.width:
            self.canvas.move(self.paddle, 10, 0)

    def start_game(self, event=None):
        """Memulai permainan setelah menekan tombol Space."""
        if self.waiting_to_start:
            self.waiting_to_start = False
            self.running = True
            self.canvas.delete(self.start_text)
            self.animate()

    def animate(self):
        """Animasi utama bola dan logika permainan."""
        if not self.running:
            return

        # Move the ball
        self.canvas.move(self.ball, self.ball_dx, self.ball_dy)
        ball_coords = self.canvas.coords(self.ball)

        # Ball collision with walls
        if ball_coords[0] <= 0 or ball_coords[2] >= self.width:
            self.ball_dx = -self.ball_dx
            self.play_sound("bounce")
        if ball_coords[1] <= 0:
            self.ball_dy = -self.ball_dy
            self.play_sound("bounce")

        # Ball collision with paddle
        paddle_coords = self.canvas.coords(self.paddle)
        if (ball_coords[2] >= paddle_coords[0] and ball_coords[0] <= paddle_coords[2]
                and ball_coords[3] >= paddle_coords[1]):
            self.ball_dy = -abs(self.ball_dy)  # Bounce up
            self.play_sound("bounce")

        # Ball collision with bricks
        for brick in self.bricks:
            brick_coords = self.canvas.coords(brick["id"])
            if (brick_coords and ball_coords[2] >= brick_coords[0]
                    and ball_coords[0] <= brick_coords[2]
                    and ball_coords[3] >= brick_coords[1]
                    and ball_coords[1] <= brick_coords[3]):
                brick["strength"] -= 1
                if brick["strength"] <= 0:
                    self.canvas.delete(brick["id"])
                    self.bricks.remove(brick)
                    self.score += 10 * self.level
                else:
                    # mengubah transparansi brick sesuai kekuatannya
                    if brick["strength"] == 2:
                        self.canvas.itemconfig(brick["id"], fill="#FFA500")  # Oranye (Strength 2)
                    elif brick["strength"] == 1:
                        self.canvas.itemconfig(brick["id"], fill="#FFFF00")  # Kuning terang (Strength 1)
                self.ball_dy = -self.ball_dy  # Bounce
                self.play_sound("brick_hit")
                break

        # Check if ball is out of bounds
        if ball_coords[3] > self.height:
            self.lives -= 1
            self.reset_ball()
            if self.lives == 0:
                self.game_over("Game Over!")
                return

        # Check if all bricks are broken
        if len(self.bricks) == 0:
            self.level_up()
            return

        # Update HUD and repeat animation
        self.update_hud()
        self.root.after(16, self.animate)

    def destroy_brick_with_effect(self, brick):
        """Efek visual saat brick dihancurkan."""
        brick_coords = self.canvas.coords(brick["id"])
        

    def update_hud(self):
        """Memperbarui tampilan HUD (skor, level, nyawa)."""
        # Hapus HUD sebelumnya
        if self.hud_lives is not None:
            for heart in self.hud_lives:
                self.canvas.delete(heart)
        if self.hud_score is not None:
            self.canvas.delete(self.hud_score)

        # Gambar nyawa berupa hati
        self.hud_lives = []
        for i in range(self.lives):
            heart = self.canvas.create_text(30 + i * 30, 20, text="❤️", font=("Arial", 16), fill="red")
            self.hud_lives.append(heart)

        # Gambar skor dan level
        self.hud_score = self.canvas.create_text(self.width - 100, 20,
                                                 text=f"Score: {self.score} | Level: {self.level}",
                                                 font=("Arial", 16), fill="black")

    def reset_ball(self):
        """Mengatur ulang posisi bola."""
        self.canvas.coords(self.ball, 290, 340, 310, 360)
        self.ball_dx = 3 * (1 if random.choice([True, False]) else -1)  # Randomize starting direction
        self.ball_dy = -3

    def level_up(self):
        """Logika untuk naik level."""
        self.level += 1
        self.create_bricks()
        self.reset_ball()
        self.update_hud()
        self.ball_dx += 1  # menambah kecepatan bola setiap level
        self.ball_dy -= 1

        self.root.after(1000, self.resume_game)  # Melanjutkan permainan setelah 1 detik
    def resume_game(self):
        """Lanjutkan permainan setelah level up."""
        self.running = True  # Menyusun ulang status permainan
        self.animate()

        self.canvas.configure(bg=random.choice(["#F0F8FF", "#FFFACD", "#E6E6FA", "#FFB6C1"]))

        # Play sound when leveling up
        self.play_sound("level_up")

    def game_over(self, message):
        """Menampilkan pesan akhir permainan."""
        self.running = False
        self.canvas.create_text(self.width / 2, self.height / 2, text=message, font=("Arial", 24), fill="black")
        self.play_sound("game_over")

    def play_sound(self, sound_type):
        """Memainkan suara berdasarkan tipe event."""
        if sound_type == "bounce":
            winsound.Beep(600, 50)
        elif sound_type == "brick_hit":
            winsound.Beep(800, 50)
        elif sound_type == "level_up":
            winsound.Beep(1000, 50)
        elif sound_type == "game_over":
            winsound.Beep(400, 50)


if __name__ == "__main__":
    root = tk.Tk()
    game = BrickBreaker(root)
    root.mainloop()
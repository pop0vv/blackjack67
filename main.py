import tkinter as tk
from tkinter import messagebox
import random
import threading
import winsound
import time

# -----------------------
# GLOBAL SETTINGS
# -----------------------

FONT_SIZE = 14
VOLUME = 5
running_music = True
exit_count = 0


# -----------------------
# MUSIC GENERATOR
# -----------------------

def casino_music():
    tones = [220, 247, 262, 294, 330, 390, 294, 330, 220, 247, 390, 262]
    while running_music:
        for t in tones:
            winsound.Beep(int(t * (VOLUME/5)), 200)
            time.sleep(0.05)

def start_music():
    thread = threading.Thread(target=casino_music, daemon=True)
    thread.start()


# -----------------------
# BLACKJACK LOGIC
# -----------------------

suits = ["♠", "♥", "♦", "♣"]
values = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

def create_deck():
    deck = []
    for s in suits:
        for v in values:
            deck.append(v + s)
    random.shuffle(deck)
    return deck

def card_value(card):

    v = card[:-1]

    if v in ["J","Q","K"]:
        return 10
    if v == "A":
        return 11
    return int(v)

def hand_value(hand):

    total = 0
    aces = 0

    for c in hand:
        val = card_value(c)
        total += val
        if c[:-1] == "A":
            aces += 1

    while total > 21 and aces:
        total -= 10
        aces -= 1

    return total


# -----------------------
# GAME CLASS
# -----------------------

class Blackjack:

    def __init__(self, root):

        self.root = root
        self.name = ""
        self.money = 2000
        self.bet = 0

        self.deck = []
        self.player = []
        self.dealer = []
        self.ai1 = []
        self.ai2 = []
        self.ai3 = []

        self.main_menu()

    # -----------------------
    # MAIN MENU
    # -----------------------

    def main_menu(self):

        for w in self.root.winfo_children():
            w.destroy()

        tk.Label(self.root, text="BLACKJACK CASINO",
                 font=("Arial", FONT_SIZE+10)).pack(pady=20)

        tk.Label(self.root, text="Unesi ime:",
                 font=("Arial", FONT_SIZE)).pack()

        self.name_entry = tk.Entry(self.root, font=("Arial", FONT_SIZE))
        self.name_entry.pack()

        tk.Button(self.root, text="Start",
                  command=self.start_game).pack(pady=10)

        tk.Button(self.root, text="Settings",
                  command=self.settings_menu).pack()

        tk.Button(self.root, text="Exit",
                  command=annoying_exit).pack(pady=10)

    # -----------------------
    # SETTINGS
    # -----------------------

    def settings_menu(self):

        global FONT_SIZE, VOLUME

        win = tk.Toplevel(self.root)
        win.title("Settings")

        tk.Label(win, text="Font Size").pack()

        def bigger():
            global FONT_SIZE
            FONT_SIZE += 2

        def smaller():
            global FONT_SIZE
            FONT_SIZE -= 2

        tk.Button(win, text="+", command=bigger).pack()
        tk.Button(win, text="-", command=smaller).pack()

        tk.Label(win, text="Music Volume").pack()

        def vol_up():
            global VOLUME
            VOLUME = min(10, VOLUME+1)

        def vol_down():
            global VOLUME
            VOLUME = max(1, VOLUME-1)

        tk.Button(win, text="Volume +", command=vol_up).pack()
        tk.Button(win, text="Volume -", command=vol_down).pack()

    # -----------------------
    # START GAME
    # -----------------------

    def start_game(self):

        self.name = self.name_entry.get()

        if not self.name:
            messagebox.showerror("Error", "Upisi ime!")
            return

        self.game_screen()

    # -----------------------
    # GAME SCREEN
    # -----------------------

    def game_screen(self):

        for w in self.root.winfo_children():
            w.destroy()

        self.info = tk.Label(self.root,
                             text=f"Igrač: {self.name}   Novac: {self.money}€",
                             font=("Arial", FONT_SIZE))
        self.info.pack()

        self.table = tk.Label(self.root, text="", font=("Arial", FONT_SIZE))
        self.table.pack(pady=20)

        bet_frame = tk.Frame(self.root)
        bet_frame.pack()

        tk.Label(bet_frame, text="Oklada:").pack(side="left")

        self.bet_entry = tk.Entry(bet_frame)
        self.bet_entry.pack(side="left")

        tk.Button(self.root, text="Deal", command=self.deal).pack()

        self.hit_btn = tk.Button(self.root, text="Hit",
                                 command=self.hit, state="disabled")
        self.hit_btn.pack()

        self.stand_btn = tk.Button(self.root, text="Stand",
                                   command=self.stand, state="disabled")
        self.stand_btn.pack()

    # -----------------------
    # DEAL
    # -----------------------

    def deal(self):

        try:
            self.bet = int(self.bet_entry.get())
        except:
            return

        if self.bet > self.money:
            messagebox.showerror("Error", "Nemaš toliko novca!")
            return

        self.deck = create_deck()

        self.player = [self.deck.pop(), self.deck.pop()]
        self.dealer = [self.deck.pop(), self.deck.pop()]
        self.ai1 = [self.deck.pop(), self.deck.pop()]
        self.ai2 = [self.deck.pop(), self.deck.pop()]
        self.ai3 = [self.deck.pop(), self.deck.pop()]

        self.hit_btn.config(state="normal")
        self.stand_btn.config(state="normal")

        self.update_table()

    def hit(self):

        self.player.append(self.deck.pop())

        if hand_value(self.player) > 21:
            self.end_round()

        self.update_table()

    def stand(self):

        while hand_value(self.dealer) < 17:
            self.dealer.append(self.deck.pop())

        self.end_round()

    def end_round(self):

        player_score = hand_value(self.player)
        dealer_score = hand_value(self.dealer)

        if player_score > 21:
            self.money -= self.bet
            result = "Bust! Izgubio si."
        elif dealer_score > 21 or player_score > dealer_score:
            self.money += self.bet
            result = "Pobijedio si!"
        elif player_score == dealer_score:
            result = "Push!"
        else:
            self.money -= self.bet
            result = "Dealer pobjeđuje."

        self.update_table(show_all=True)

        messagebox.showinfo("Rezultat", result)

        if self.money <= 0:

            if messagebox.askyesno("Game Over",
                                   "Izgubio si sve! Restart?"):
                self.money = 2000
            else:
                annoying_exit()

        self.info.config(text=f"Igrač: {self.name}   Novac: {self.money}€")

        self.hit_btn.config(state="disabled")
        self.stand_btn.config(state="disabled")

    def update_table(self, show_all=False):

        dealer_cards = self.dealer if show_all else [self.dealer[0], "?"]

        text = f"""
Dealer: {dealer_cards} ({hand_value(self.dealer) if show_all else ""})

{self.name}: {self.player} ({hand_value(self.player)})

AI1: {self.ai1}
AI2: {self.ai2}
AI3: {self.ai3}
"""

        self.table.config(text=text)


# -----------------------
# ANNOYING EXIT SYSTEM
# -----------------------

def annoying_exit():

    global exit_count
    exit_count += 1

    win = tk.Toplevel(root)
    win.title("Siguran?")
    win.geometry("300x150")

    tk.Label(win,
             text=f"Jesi li siguran da želiš izaći? ({exit_count}/51)",
             font=("Arial", FONT_SIZE)).pack(pady=10)

    if exit_count < 51:

        size = max(2, 18 - exit_count//2)

        tk.Button(
            win,
            text="DA",
            width=size,
            command=lambda:[win.destroy(), annoying_exit()]
        ).pack(pady=5)

        tk.Button(
            win,
            text="NE",
            width=10,
            command=win.destroy
        ).pack()

    else:

        tk.Button(
            win,
            text="NE",
            width=10,
            command=win.destroy
        ).pack(pady=20)


# -----------------------
# RUN
# -----------------------

root = tk.Tk()
root.title("Blackjack Casino")
root.geometry("600x500")

root.protocol("WM_DELETE_WINDOW", annoying_exit)

start_music()

game = Blackjack(root)

root.mainloop()

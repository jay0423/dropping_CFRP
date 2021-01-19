import random

class JANKEN:
    def __init__(self, player_name):
        self.player_name = player_name
        self.computer_hand = 0
        self.player_hand = 0
        self.win_or_lose = ""
        
    def make_computer_hand(self):
        self.computer_hand = random.choice([0, 1, 2])
    
    def make_player_hand(self):
        while True:
            input_ = input("選択してください\n0: グー, 1: チョキ, 2: パー： ")
            if input_ == "0" or input_ == "1" or input_ == "2":
                self.player_hand = int(input_)
                break
        
    def draw(self):
        print("あいこです．")
        self.make_computer_hand()
        self.make_player_hand()
        self.djage_winner()
    
    def djage_winner(self):
        janken_d = {0: "グー", 1: "チョキ", 2: "パー"}
        print("コンピュータ： {}，{}： {}".format(janken_d[self.computer_hand], self.player_name, janken_d[self.player_hand]))
        if self.computer_hand == 0 and self.player_hand == 1:
            self.win_or_lose = "computer"
        elif self.computer_hand == 1 and self.player_hand == 0:
            self.win_or_lose = self.player_name
        elif self.computer_hand == 1 and self.player_hand == 2:
            self.win_or_lose = "computer"
        elif self.computer_hand == 2 and self.player_hand == 1:
            self.win_or_lose = self.player_name
        elif self.computer_hand == 2 and self.player_hand == 0:
            self.win_or_lose = "computer"
        elif self.computer_hand == 0 and self.player_hand == 2:
            self.win_or_lose = self.player_name
        else:
            self.draw()
            
    
    def output_winner(self):
        self.make_computer_hand()
        self.make_player_hand()
        self.djage_winner()
        return self.win_or_lose
    
    
if __name__ == "__main__":
    a = JANKEN(input("player name: "))
    winner = a.output_winner()
    print("勝者： ", winner)
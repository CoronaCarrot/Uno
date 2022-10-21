
# define card class


class Red_0:
    def __init__(self, game):
        self.game = game
        self.card = game.card
    
    def check(self):
        # check if card can be played
        playfield = self.game.playfield
        # get latest card on playfield
        latest_card = playfield[-1]
        # check if card is red
        if latest_card.color == "red":
            return True
        elif latest_card.number == 0:
            return True
        elif latest_card.type == "special" and self.game.uno.currentcolor == "red":
            return True
        else:
            return False

    def play(self):
        # append card to playfield
        self.game.playfield.append(self.card)
        # remove card from hand
        self.game.player.hand.remove(self.card)
        # check if player has won
        if len(self.game.player.hand) == 0 and self.card.type != "special":
            self.game.win()
        elif len(self.game.player.hand) == 0 and self.card.type == "special":
            # draw a card
            self.game.drawCard()
        
        return self.game
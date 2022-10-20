import discord
import json
from random import shuffle

class Player():
    def __init__(self, core: discord.Member, hand = []):
        self.core = core
        self.displayname = core.display_name
        self.hand = hand
        self.remainingCards = len(self.hand)

class Game():
    playerTurn = 0
    winningPlayer = -1
    playfield = []
    turnOrder = 1
    playersToSkip = 0
    
    def __init__(self, players, deckName = "Default"):
        self.players = players
        self.numberOfPlayers = len(self.players)
        self.deckName = deckName
        
        #assemble the deck
        countfilepath = "Modules/uno/decks/" + deckName + "/assets/deck.json"
        counts = json.load(open(countfilepath))
        cardTypes = counts.keys()
        deck = []
        for card in cardTypes:
            for i in range(counts[card]):
                deck.append(card)
        self.deck = shuffle(deck)
        self.completedeck = deck
        

    def win(self, playerNum = playerTurn):
        self.winningPlayer = playerNum

    def nextPlayer(self):
        self.playerTurn += (self.turnOrder) * (self.playersToSkip + 1)
        self.playerTurn %= self.numberOfPlayers
        self.playersToSkip = 0

    def drawcard(self):
        if len(self.deck) == 0:
            self.deck = shuffle(self.completedeck)
        self.players[self.playerTurn].hand.append(self.deck.pop(0))

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
        cardTypes = counts['cards'].keys()
        deck = []
        for card in cardTypes:
            for i in range(counts['cards'][card]):
                deck.append(card)
        self.deck = shuffle(deck)
        self.completedeck = deck
        self.startCards = counts['hand_size']
        

    def win(self, playerNum = playerTurn):
        self.winningPlayer = playerNum

    def nextPlayer(self):
        self.playerTurn += (self.turnOrder) * (self.playersToSkip + 1)
        self.playerTurn %= self.numberOfPlayers
        self.playersToSkip = 0
    
    def removeCardFromDeck(self, cardID, amount = 1):
        for i in range(amount):
            if cardID in self.deck:
                self.deck.remove(cardID)

    def playfieldDeckMerge(self):
        for i in range(len(self.playfield) - 1):
            self.deck.append(self.playfield.pop(0))

    def drawCard(self):
        if len(self.deck) == 0:
            self.playfieldDeckMerge()
        self.players[self.playerTurn].hand.append(self.deck.pop(0))

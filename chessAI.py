import random

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3# Higher depth means stronger but slower play

# Standard material point values
pieceScore = {
    "K": 0, 
    "Q": 9, 
    "R": 5, 
    "B": 3, 
    "N": 3, 
    "P": 1
}

def findRandomMove(validMoves):
    """Returns a completely random move from the list of valid moves."""
    return validMoves[random.randint(0, len(validMoves) - 1)]

def findBestMove(gs, validMoves):
    """
    Main entry point for the AI engine. Shuffles the valid moves 
    to introduce variation and calculates the optimal move using NegaMax.
    """
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    
    # 1 if white's turn, -1 if black's turn
    turnMultiplier = 1 if gs.whiteToMove else -1
    
    findMoveNegaMax(gs, validMoves, DEPTH, turnMultiplier)
    return nextMove

def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    """
    Recursive NegaMax algorithm to search ahead through the game tree.
    """
    global nextMove
    
    # Base case: we reached our search depth or game is over
    if depth == 0 or gs.checkMate or gs.staleMate:
        return turnMultiplier * scoreBoard(gs)
    
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        
        # In NegaMax, the opponent's max score is inverted (-) with an updated turn multiplier
        score = -findMoveNegaMax(gs, nextMoves, depth - 1, -turnMultiplier)
        
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
                
        gs.undoMove() # Backtrack board state
        
    return maxScore

def scoreBoard(gs):
    """
    Evaluates the current state of the board. Returns a positive score if the 
    position favors white, and a negative score if it favors black.
    """
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE  # White is trapped in checkmate (Black wins)
        else:
            return CHECKMATE   # Black is trapped in checkmate (White wins)
            
    if gs.staleMate:
        return STALEMATE

    # Material balance calculations
    score = 0
    for row in gs.board:
        for square in row:
            if square != '--':
                if square[0] == 'w':
                    score += pieceScore[square[1]]
                elif square[0] == 'b':
                    score -= pieceScore[square[1]]
                    
    return score
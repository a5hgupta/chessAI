import pygame as p 
import chessEngine 
import chessAI

boardWidth = boardHeight = 512
moveLogPanelWidth = 250
moveLogPanelHeight = boardHeight
dimension = 8
sqSize = boardHeight // dimension
maxFPS = 15
images = {}

def LoadImages():
    global images
    pieces = ["wR", "wN", "wB", "wQ", "wK", "wP", "bR", "bN", "bB", "bQ", "bK", "bP"]
    for piece in pieces:
        images[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (sqSize, sqSize))

def main():
    p.init()
    screen = p.display.set_mode((boardWidth + moveLogPanelWidth, boardHeight))
    p.display.set_caption("Chess Engine")
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    moveLogFont= p.font.SysFont("Arial", 12, False, False)
    gs = chessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False 
    animate = False # Flag for when we should animate a move
    
    LoadImages()
    running = True
    sqSelected = ()
    playerClicks = []
    gameOver = False
    playerOne = False# True if a human is playing white
    playerTwo =  False# True if a human is playing black
    
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()
                    col = location[0] // sqSize
                    row = location[1] // sqSize
                    if sqSelected == (row, col) or col >= 8:
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:
                        move = chessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True # Turn on animation for human moves
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:    
                            playerClicks = [sqSelected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: # Undo move
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False

                if e.key == p.K_r: # Reset board
                    gs = chessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False

        # AI Turn Logic
        if not gameOver and not humanTurn:
            AIMove = chessAI.findBestMove(gs, validMoves)
            if AIMove is None:
                AIMove = chessAI.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True # Turn on animation for AI moves
        
        if moveMade:
            if animate:
                animateMove(gs.moveLog[len(gs.moveLog) -1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGamestate(screen, gs, validMoves, sqSelected, moveLogFont)

        # Game Over Screen Checks
        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawEndGameText(screen, 'Black wins by Checkmate')
            else:
                drawEndGameText(screen, 'White wins by Checkmate')
        elif gs.staleMate:
            gameOver = True
            drawEndGameText(screen, 'STALEMATE')

        clock.tick(maxFPS)
        p.display.flip()

def drawGamestate(screen, gs, validMoves, sqSelected, moveLogFont):
    drawBoard(screen)
    highLightSquare(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board, images)
    drawMoveLog(screen, gs, moveLogFont )

def highLightSquare(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((sqSize, sqSize)) 
            s.set_alpha(100)
            s.fill(p.Color('green'))
            screen.blit(s, (c*sqSize, r*sqSize))
            s.fill(p.Color('blue'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*sqSize, move.endRow*sqSize))



def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(dimension):
        for c in range(dimension):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*sqSize, r*sqSize, sqSize, sqSize))

def drawPieces(screen, board, images):
    for r in range(dimension):
        for c in range(dimension):
            piece = board[r][c]
            if piece != '--':
                if piece in images:
                    screen.blit(images[piece], p.Rect(c*sqSize, r*sqSize, sqSize, sqSize))

def drawMoveLog(screen, gs, font):
    moveLogText = ""
    for i in range(0, len(gs.moveLog), 2):
        moveLogText += str(i//2 + 1) + ". " + gs.moveLog[i].getChessNotation() + " "
        if i+1 < len(gs.moveLog):
            moveLogText += gs.moveLog[i+1].getChessNotation() + "\n"
    moveLogRect = p.Rect(boardWidth, 0 , moveLogPanelWidth, moveLogPanelHeight)
    moveLog = gs.moveLog
    moveTexts = moveLog
    padding = 5
    linespacing = 2
    textY = padding
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    textObject = font.render(moveLogText, 0, p.Color('Gray'))
    textLocation = p.Rect(boardWidth, 0, moveLogPanelWidth, moveLogPanelHeight)
    screen.blit(textObject, textLocation)
    textY += textObject.get_height() + linespacing

def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    frameCount = max(abs(dR), abs(dC)) * 8  # Frames speed factor
    
    for frame in range(frameCount + 1):
        r = move.startRow + dR * frame / frameCount
        c = move.startCol + dC * frame / frameCount
        drawBoard(screen)
        
        # Draw all pieces except the one currently animating
        for row in range(dimension):
            for col in range(dimension):
                piece = board[row][col]
                if piece != '--':
                    # Skip drawing the piece at its final location during interpolation
                    if not (row == move.endRow and col == move.endCol):
                        screen.blit(images[piece], p.Rect(col*sqSize, row*sqSize, sqSize, sqSize))
                    # If there's a piece captured, don't draw it underneath the animation path
                    elif row == move.endRow and col == move.endCol and move.pieceCaptured != '--':
                        pass
        
        # Draw moving piece at its current sliding position
        screen.blit(images[move.pieceMoved], p.Rect(int(c*sqSize), int(r*sqSize), sqSize, sqSize))
        p.display.flip()
        clock.tick(60)

def drawEndGameText(screen, text):
    # Fixed font typo from 'Helvitce' -> 'Helvetica'
    font = p.font.SysFont("Helvetica", 32, True, False)
    textObject = font.render(text, True, p.Color('Black'))
    
    # Center text box computation
    textRect = textObject.get_rect(center=(boardWidth // 2, boardHeight // 2))
    
    # Draw a clean background panel behind text overlay box
    background_rect = p.Rect(textRect.x - 10, textRect.y - 5, textRect.width + 20, textRect.height + 10)
    p.draw.rect(screen, p.Color('Light Gray'), background_rect)
    p.draw.rect(screen, p.Color('Black'), background_rect, 2)
    
    screen.blit(textObject, textRect)

if __name__ == "__main__":
    main()
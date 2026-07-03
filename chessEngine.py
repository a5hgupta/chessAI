class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassentMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        
        # Promotion state evaluation flags
        self.isPawnPromotion = (self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved == 'bP' and self.endRow == 7)
        
        # En Passant property assignments
        self.isEnpassentMove = isEnpassentMove
        if self.isEnpassentMove:
            self.pieceCaptured = 'wP' if self.pieceMoved == 'bP' else 'bP'
            
        # Castle flag
        self.isCastleMove = isCastleMove
        
        self.moveId = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):    
        if isinstance(other, Move):
            return self.moveId == other.moveId
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]



class GameState():

    def __init__(self):
        # The board is an 8x8 2D list, each element has 2 characters.
        # The first character represents the color: 'b' or 'w'
        # The second character represents the type of the piece: 'R', 'N', 'B', 'Q', 'K' or 'P'
        # "--" represents an empty space with no piece.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunction = {
            'P': self.getPawnMove, 'R': self.getRookMove, 'N': self.getKnightMove,
            'B': self.getBishopMove, 'Q': self.getQueenMove, 'K': self.getKingMove
        }
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = True
        self.staleMate = True
        
        # En Passant tracking: coordinates of the square where an en passant capture is possible
        self.enpassantPossible = () 
        
        # Castling Rights tracking
        """
        Minimal chess engine to support the UI and AI in this workspace.

        This module provides a compact, consistent `GameState` and `Move` implementation
        with a naive move generator. It intentionally omits advanced rules (detailed
        check validation, en-passant edge cases, full promotion handling, etc.) but is
        sufficient for running the provided UI and basic AI.
        """

        class GameState:
            def __init__(self):
                # Board is an 8x8 list of strings, e.g. 'wP', 'bK' or '--'
                self.board = [
                    ["bR","bN","bB","bQ","bK","bB","bN","bR"],
                    ["bP"]*8,
                    ["--"]*8,
                    ["--"]*8,
                    ["--"]*8,
                    ["--"]*8,
                    ["wP"]*8,
                    ["wR","wN","wB","wQ","wK","wB","wN","wR"],
                ]
                self.whiteToMove = True
                self.moveLog = []
                self.checkMate = False
                self.staleMate = False

            def makeMove(self, move):
                self.board[move.startRow][move.startCol] = "--"
                move.pieceCaptured = self.board[move.endRow][move.endCol]
                self.board[move.endRow][move.endCol] = move.pieceMoved
                self.moveLog.append(move)
                self.whiteToMove = not self.whiteToMove

            def undoMove(self):
                if not self.moveLog:
                    return
                move = self.moveLog.pop()
                self.board[move.startRow][move.startCol] = move.pieceMoved
                self.board[move.endRow][move.endCol] = move.pieceCaptured
                self.whiteToMove = not self.whiteToMove

            def getValidMoves(self):
                # Naive generator: does not filter moves that leave king in check
                return self._generateAllPossibleMoves()

            def _generateAllPossibleMoves(self):
                moves = []
                for r in range(8):
                    for c in range(8):
                        piece = self.board[r][c]
                        if piece == "--":
                            continue
                        color = piece[0]
                        if (color == 'w') == self.whiteToMove:
                            pt = piece[1]
                            if pt == 'P':
                                self._getPawnMoves(r, c, moves)
                            elif pt == 'R':
                                self._getRookMoves(r, c, moves)
                            elif pt == 'N':
                                self._getKnightMoves(r, c, moves)
                            elif pt == 'B':
                                self._getBishopMoves(r, c, moves)
                            elif pt == 'Q':
                                self._getQueenMoves(r, c, moves)
                            elif pt == 'K':
                                self._getKingMoves(r, c, moves)
                return moves

            def _getPawnMoves(self, r, c, moves):
                piece = self.board[r][c]
                if piece[0] == 'w':
                    if r-1 >= 0 and self.board[r-1][c] == '--':
                        moves.append(Move((r,c),(r-1,c), self.board))
                        if r == 6 and self.board[r-2][c] == '--':
                            moves.append(Move((r,c),(r-2,c), self.board))
                    for dc in (-1,1):
                        if 0 <= c+dc < 8 and r-1 >= 0 and self.board[r-1][c+dc] != '--' and self.board[r-1][c+dc][0] == 'b':
                            moves.append(Move((r,c),(r-1,c+dc), self.board))
                else:
                    if r+1 < 8 and self.board[r+1][c] == '--':
                        moves.append(Move((r,c),(r+1,c), self.board))
                        if r == 1 and self.board[r+2][c] == '--':
                            moves.append(Move((r,c),(r+2,c), self.board))
                    for dc in (-1,1):
                        if 0 <= c+dc < 8 and r+1 < 8 and self.board[r+1][c+dc] != '--' and self.board[r+1][c+dc][0] == 'w':
                            moves.append(Move((r,c),(r+1,c+dc), self.board))

            def _getRookMoves(self, r, c, moves):
                directions = ((-1,0),(0,-1),(1,0),(0,1))
                enemy = 'b' if self.whiteToMove else 'w'
                for d in directions:
                    for i in range(1,8):
                        er = r + d[0]*i
                        ec = c + d[1]*i
                        if 0 <= er < 8 and 0 <= ec < 8:
                            endPiece = self.board[er][ec]
                            if endPiece == '--':
                                moves.append(Move((r,c),(er,ec), self.board))
                            else:
                                if endPiece[0] == enemy:
                                    moves.append(Move((r,c),(er,ec), self.board))
                                break
                        else:
                            break

            def _getBishopMoves(self, r, c, moves):
                directions = ((-1,-1),(-1,1),(1,-1),(1,1))
                enemy = 'b' if self.whiteToMove else 'w'
                for d in directions:
                    for i in range(1,8):
                        er = r + d[0]*i
                        ec = c + d[1]*i
                        if 0 <= er < 8 and 0 <= ec < 8:
                            endPiece = self.board[er][ec]
                            if endPiece == '--':
                                moves.append(Move((r,c),(er,ec), self.board))
                            else:
                                if endPiece[0] == enemy:
                                    moves.append(Move((r,c),(er,ec), self.board))
                                break
                        else:
                            break

            def _getQueenMoves(self, r, c, moves):
                self._getRookMoves(r,c,moves)
                self._getBishopMoves(r,c,moves)

            def _getKnightMoves(self, r, c, moves):
                knightMoves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
                ally = 'w' if self.whiteToMove else 'b'
                for m in knightMoves:
                    er = r + m[0]
                    ec = c + m[1]
                    if 0 <= er < 8 and 0 <= ec < 8:
                        endPiece = self.board[er][ec]
                        if endPiece == '--' or endPiece[0] != ally:
                            moves.append(Move((r,c),(er,ec), self.board))

            def _getKingMoves(self, r, c, moves):
                kingMoves = ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))
                ally = 'w' if self.whiteToMove else 'b'
                for m in kingMoves:
                    er = r + m[0]
                    ec = c + m[1]
                    if 0 <= er < 8 and 0 <= ec < 8:
                        endPiece = self.board[er][ec]
                        if endPiece == '--' or endPiece[0] != ally:
                            moves.append(Move((r,c),(er,ec), self.board))


        class Move:
            ranksToRows = {str(8-i): i for i in range(8)}
            rowsToRanks = {v: k for k, v in ranksToRows.items()}
            filesToCols = {c: i for i, c in enumerate('abcdefgh')}
            colsToFiles = {v: k for k, v in filesToCols.items()}

            def __init__(self, startSq, endSq, board):
                (self.startRow, self.startCol) = startSq
                (self.endRow, self.endCol) = endSq
                self.pieceMoved = board[self.startRow][self.startCol]
                self.pieceCaptured = board[self.endRow][self.endCol]
                self.moveID = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol

            def __eq__(self, other):
                if isinstance(other, Move):
                    return self.moveID == other.moveID
                return False

            def getChessNotation(self):
                return f"{self.pieceMoved}@{self._getRankFile(self.startRow,self.startCol)}->{self._getRankFile(self.endRow,self.endCol)}"

            def _getRankFile(self, r, c):
                return self.colsToFiles[c] + self.rowsToRanks[r]
        """Calculates all possible moves for a pawn at (r, c)"""

        piecePinned = False

        pinDirection = ()


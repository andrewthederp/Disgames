from .board import Board

def edit_board(board, coors, replacment):
    """takes a list of coors and edits them to whatever replacment is"""

    if not isinstance(board, Board):
        raise ValueError("board argument can only be a Board object")
    bord = eval(str(board))
    bord = Board(len(bord)-1, len(bord[0])-1, board.seperator, coors, replacment, bord)
    return bord

def format_board(board):
    """Formats the nested list to make it look pwetty"""
    if not isinstance(board, Board):
        raise ValueError("board argument can only be a Board object")
    lst = []
    bord = eval(str(board))
    for i in bord:
        scn_lst = []
        for thing in i:
            if thing == f"{board.seperator}":
                scn_lst.append(f'{board.seperator} ')
            else:
                scn_lst.append(thing)
        lst.append(''.join(scn_lst))
    return '\n'.join(lst)

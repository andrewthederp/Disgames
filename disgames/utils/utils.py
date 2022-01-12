from ast import literal_eval
from .board import Board
# couldn't bother renaming it

def edit_board(board, coors, replacement):
    """takes a list of coors and edits them to whatever replacement is"""

    if not isinstance(board, Board):
        raise ValueError("board argument can only be a Board object")
    board1 = literal_eval(str(board))
    board1 = Board(
        len(board1) - 1,
        len(board1[0]) - 1,
        board.separator,
        coors,
        replacement,
        board1,
    )
    return board1


def format_board(board):
    """Formats the nested list to make it look pwetty"""
    if not isinstance(board, Board):
        raise ValueError("board argument can only be a Board object")
    lst = []
    board1 = literal_eval(str(board))
    for i in board1:
        scn_lst = []    
        for thing in i:
            if thing == f"{board.separator}":
                scn_lst.append(f"{board.separator} ")
            else:
                scn_lst.append(thing)
        lst.append("".join(scn_lst))
    return "\n".join(lst)

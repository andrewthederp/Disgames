class Board:
    """A board class that gives a nested which is the board"""
    def __init__(self, x, y, default='', coordinates = [], replacment = ' '):
        self.x = x
        self.y = y
        self._default = default
        self.coors = coordinates
        self.replacment = replacment

    def __str__(self):
        lst = []
        g = []
        for i in range(self.x+1):
            g.append(f'{self._default}{i}')
        lst.append(g)
        for i in range(self.x):
            lst.append([f'{self._default}{i+1}'])
            for h in range(self.y):
                lst[i+1].append(f"{self._default}")
        if self.coors:
            for x, y in self.coors:
                lst[int(x)][int(y)] = f"{self._default}{self.replacment}"
        return str(lst)

    @property
    def dimensions(self):
        """Give the dimensions of the board"""
        return self.x, self.y

    @property
    def default(self):
        """TODO: change the name

        Returns the seperator of the board"""

        return self._default

def edit_board(board, coors, replacment):
    """takes a list of coors and edits them to whatever replacment is"""

    if not isinstance(board, Board):
        raise ValueError("board argument can only be a Board object")
        return
    bord = eval(str(board))
    bord = Board(len(bord)-1, len(bord[0])-1, board.default, coors, replacment)
    return bord

def format_board(board):
    """Formats the nested list to make it look pwetty"""
    if not isinstance(board, Board):
        raise ValueError("board argument can only be a Board object")
        return
    lst = []
    bord = eval(str(board))
    for i in bord:
        scn_lst = []
        for thing in i:
            if thing == f"{board.default}":
                scn_lst.append(f'{board.default} ')
            else:
                scn_lst.append(thing)
        lst.append(''.join(scn_lst))
    return '\n'.join(lst)

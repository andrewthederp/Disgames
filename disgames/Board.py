class Board:
    """A board class that gives a nested which is the board"""

    def __init__(
        self, x, y, default="", coordinates=[], replacment=" ", test=[]
    ):
        self.x = x
        self.y = y
        self._default = default
        self.coors = coordinates
        self.replacment = replacment
        self.test = test

    def __str__(self):
        lst = []
        g = [f"{self._default}{i}" for i in range(self.x + 1)]
        lst.append(g)
        for i in range(self.x):
            lst.append([f"{self._default}{i+1}"])
            for _ in range(self.y):
                lst[i + 1].append(f"{self._default}")
        if self.coors:
            for x, i in enumerate(self.test):
                for y, j in enumerate(i):
                    if self.test[x][y] != f"{self._default} ":
                        lst[x][y] = self.test[x][y]
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

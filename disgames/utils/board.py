class Board:
    """A board class that gives a nested list which is the board"""

    def __init__(
        self, x, y, separator="", coordinates=[], replacement=" ", test=[]
    ):
        self.x = x
        self.y = y
        self._seperator = separator
        self.coors = coordinates
        self.replacement = replacement
        self.test = test

    def __str__(self):
        lst = []
        g = [f"{self.separator}{i}" for i in range(self.x + 1)]
        lst.append(g)
        for i in range(self.x):
            lst.append([f"{self.separator}{i+1}"])
            for _ in range(self.y):
                lst[i + 1].append(f"{self.separator}")
        if self.coors:
            for x, i in enumerate(self.test):
                for y, j in enumerate(i):
                    if self.test[x][y] != f"{self.separator} ":
                        lst[x][y] = self.test[x][y]
            for x, y in self.coors:
                lst[int(x)][int(y)] = f"{self.separator}{self.replacement}"
        return str(lst)

    @property
    def dimensions(self):
        """Give the dimensions of the board"""
        return self.x, self.y

    @property
    def separator(self):
        """TODO: change the name

        Returns the separator of the board"""

        return self._seperator

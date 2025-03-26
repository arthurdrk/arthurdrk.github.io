import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from color_grid_game import *

class Grid:
    """
    A class representing a grid with cells that have colors and values.

    Attributes
    ----------
    n : int
        Number of rows in the grid.
    m : int
        Number of columns in the grid.
    color : list[list[int]]
        The color of each grid cell. `color[i][j]` is the color value in the cell (i, j).
        Lines are numbered from 0 to n-1, and columns from 0 to m-1.
    value : list[list[int]]
        The value of each grid cell. `value[i][j]` is the value in the cell (i, j).
        Lines are numbered from 0 to n-1, and columns from 0 to m-1.
    colors_list : list[str]
        The mapping between the value of `color[i][j]` and the corresponding color.
    """

    def __init__(self, n: int, m: int, color: list[list[int]] = None, value: list[list[int]] = None):
        """
        Initializes the grid.

        Parameters
        ----------
        n : int
            Number of rows in the grid.
        m : int
            Number of columns in the grid.
        color : list[list[int]], optional
            The grid cells colors. Default is empty, which initializes each cell with color 0 (white).
        value : list[list[int]], optional
            The grid cells values. Default is empty, which initializes each cell with value 1.

        Raises
        ------
        ValueError
            If `n` or `m` is not a positive integer.
        """
        if n <= 0 or m <= 0:
            raise ValueError("Number of rows and columns must be positive integers.")

        self.n = n
        self.m = m
        if color is None or len(color) == 0:
            color = [[0 for _ in range(m)] for _ in range(n)]
        self.color = color
        if value is None or len(value) == 0:
            value = [[1 for _ in range(m)] for _ in range(n)]
        self.value = value
        self.colors_list = ['w', 'r', 'b', 'g', 'k']

    def _is_within_bounds(self, i: int, j: int) -> bool:
        """
        Checks if a cell index is within the grid boundaries.

        Parameters
        ----------
        i : int
            Row index of the cell.
        j : int
            Column index of the cell.

        Returns
        -------
        bool
            True if the cell (i, j) is within the grid boundaries, False otherwise.
        """
        return 0 <= i < self.n and 0 <= j < self.m

    def __str__(self) -> str:
        """
        Returns a string representation of the grid, including colors and values.

        Returns
        -------
        str
            A string describing the grid's colors and values.
        """
        output = f"The grid is {self.n} x {self.m}. It has the following colors:\n"
        for i in range(self.n):
            output += f"{[self.colors_list[self.color[i][j]] for j in range(self.m)]}\n"
        output += "and the following values:\n"
        for i in range(self.n):
            output += f"{self.value[i]}\n"
        return output

    def __repr__(self) -> str:
        """
        Returns a formal string representation of the grid.

        Returns
        -------
        str
            A string representation of the grid with the number of rows and columns.

        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        return f"<grid.Grid: n={self.n}, m={self.m}>"

    def plot(self) -> None:
        """
        Plots a visual representation of the grid using matplotlib.

        Raises
        ------
        ImportError
            If matplotlib is not installed.
        """
        plt.figure(figsize=(8, 8))
        plt.imshow(self.color, cmap=matplotlib.colors.ListedColormap(self.colors_list), interpolation='nearest')
        for i in range(self.n):
            for j in range(self.m):
                color_idx = self.color[i][j]
                val = self.value[i][j]
                plt.text(j, i, str(val), ha='center', va='center', fontsize=14)
        plt.xticks([])
        plt.yticks([])
        plt.show()

    def is_forbidden(self, i: int, j: int) -> bool:
        """
        Checks if a cell is forbidden (black).

        Parameters
        ----------
        i : int
            Row index of the cell.
        j : int
            Column index of the cell.

        Returns
        -------
        bool
            True if the cell (i, j) is black, False otherwise.

        Raises
        ------
        IndexError
            If the cell (i, j) is out of the grid boundaries.
        """
        if not self._is_within_bounds(i, j):
            raise IndexError("Cell index out of grid boundaries.")
        return self.color[i][j] == 4

    def cost(self, pair: tuple[tuple[int, int], tuple[int, int]]) -> int:
        """
        Returns the cost of a pair of cells.

        Parameters
        ----------
        pair : tuple[tuple[int, int], tuple[int, int]]
            A pair of cells in the format ((i1, j1), (i2, j2)).

        Returns
        -------
        int
            The cost of the pair, defined as the absolute value of the difference between their values.

        Raises
        ------
        ValueError
            If the pair does not contain valid cell indices.
        """
        (i1, j1), (i2, j2) = pair
        if not (self._is_within_bounds(i1, j1) and self._is_within_bounds(i2, j2)):
            raise ValueError("Pair contains invalid cell indices.")
        return abs(self.value[i1][j1] - self.value[i2][j2])

    def all_pairs(self, rules="original rules") -> list[tuple[tuple[int, int], tuple[int, int]]]:
        """
        Returns all allowed pairs of neighboring cells.

        Parameters
        ----------
        rules : str, optional
            The rules to apply for determining allowed pairs. Default is "original rules".

        Returns
        -------
        list[tuple[tuple[int, int], tuple[int, int]]]
            A list of pairs of neighboring cells that are allowed to be paired.

        Raises
        ------
        ValueError
            If the rules parameter is not recognized.
        """
        if rules not in ["original rules", "new rules"]:
            raise ValueError("Unrecognized rules parameter.")

        res = []
        allowed = {
            0: {0, 1, 2, 3},  # white can pair with all except black
            1: {0, 1, 2},     # red can pair with white, blue, red
            2: {0, 1, 2},     # blue can pair with white, blue, red
            3: {0, 3}         # green can pair with white, green
        }
        directions = [(0, 1), (1, 0)]
        if rules == "original rules":
            for i in range(self.n):
                for j in range(self.m):
                    if self.is_forbidden(i, j):
                        continue
                    c1 = self.color[i][j]
                    for dx, dy in directions:
                        k, l = i + dx, j + dy
                        if self._is_within_bounds(k, l):  # Check grid boundaries
                            if self.is_forbidden(k, l):
                                continue
                            c2 = self.color[k][l]
                            if c2 in allowed[c1] and c1 in allowed[c2]:
                                res.append(((i, j), (k, l)))
            return sorted(res)

        elif rules == "new rules":
            for i in range(self.n):
                for j in range(self.m):
                    if self.is_forbidden(i, j):
                        continue
                    c1 = self.color[i][j]
                    if c1 == 0:  # White cell can pair with any non-forbidden cell
                        for k in range(self.n):
                            for l in range(self.m):
                                if (i == k and j == l) or self.is_forbidden(k, l):
                                    continue
                                if (i, j) < (k, l):
                                    res.append(((i, j), (k, l)))
                    else:  # Non-white cells follow original adjacency rules
                        for dx, dy in directions:
                            k, l = i + dx, j + dy
                            if self._is_within_bounds(k, l):
                                if self.is_forbidden(k, l):
                                    continue
                                c2 = self.color[k][l]
                                if c2 in allowed[c1] and c1 in allowed[c2]:
                                    res.append(((i, j), (k, l)))
            return sorted(res)

    def vois(self, i: int, j: int) -> list[tuple[int, int]]:
        """
        Returns the list of neighbors of the cell (i, j).

        Parameters
        ----------
        i : int
            Row index of the cell.
        j : int
            Column index of the cell.

        Returns
        -------
        list[tuple[int, int]]
            A list of neighboring cell coordinates.

        Raises
        ------
        IndexError
            If the cell (i, j) is out of the grid boundaries.
        """
        if not self._is_within_bounds(i, j):
            raise IndexError("Cell index out of grid boundaries.")

        res = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            k, l = i + dx, j + dy
            if self._is_within_bounds(k, l):  # Check grid boundaries
                res.append((k, l))
        return res

    @classmethod
    def grid_from_file(cls, file_name: str, read_values: bool = False) -> 'Grid':
        """
        Creates a Grid object from a file.

        Parameters
        ----------
        file_name : str
            Name of the file to load. The file must be formatted as follows:
            - The first line contains "n m".
            - The next n lines contain m integers representing the colors of the corresponding cells.
            - The next n lines contain m integers representing the values of the corresponding cells.
        read_values : bool, optional
            Indicates whether to read values after reading the colors. Requires the file to have 2n+1 lines.

        Returns
        -------
        Grid
            The initialized Grid object.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        ValueError
            If the file format is incorrect or contains invalid color values.
        """
        try:
            with open(file_name, "r") as file:
                n, m = map(int, file.readline().split())
                color = [[] for _ in range(n)]
                for i_line in range(n):
                    line_color = list(map(int, file.readline().split()))
                    if len(line_color) != m:
                        raise ValueError("Incorrect format")
                    for j in range(m):
                        if line_color[j] not in range(5):
                            raise ValueError("Invalid color")
                    color[i_line] = line_color

                if read_values:
                    value = [[] for _ in range(n)]
                    for i_line in range(n):
                        line_value = list(map(int, file.readline().split()))
                        if len(line_value) != m:
                            raise ValueError("Incorrect format")
                        value[i_line] = line_value
                else:
                    value = []

                grid = Grid(n, m, color, value)
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {file_name} does not exist.")

        return grid

    def bipartite_graph(self) -> dict:
        """
        Returns a bipartite graph version of the grid, i.e., creates a graph of the grid with two sets of even cells, odd cells.
        The graph already contains the valid pairs as edges.

        Returns
        -------
        dict
            A graph G stored as a dict type with two underdicts 'even' and 'odd' edges.

        Raises
        ------
        ValueError
            If the grid contains no valid pairs.
        """
        G = {
            'even': {},
            'odd': {}
        }  # Preparing the two sets of edges.
        pairs = self.all_pairs()

        if not pairs:
            raise ValueError("The grid contains no valid pairs.")

        # Adding edges with color and adjacency constraints
        for i in range(self.n):
            for j in range(self.m):
                if self.color[i][j] != 4:  # Ignoring black cells
                    cell = (i, j)
                    if (i + j) % 2 == 0:
                        cell_parity = "even"
                    else:
                        cell_parity = "odd"  # Needed to access the Graph set
                    neighbor_parity = "even" if cell_parity == "odd" else "odd"
                    for i2, j2 in [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]:  # Checking all the valid neighbors
                        if self._is_within_bounds(i2, j2) and not self.is_forbidden(i2, j2):  # In the grid and not black
                            if (cell, (i2, j2)) in pairs or ((i2, j2), cell) in pairs:
                                if cell not in G[cell_parity]:  # If the cell is not already in the dictionary
                                    G[cell_parity][cell] = []
                                if (i2, j2) not in G[neighbor_parity]:
                                    G[neighbor_parity][(i2, j2)] = []
                                if (i2, j2) not in G[cell_parity][cell]:  # To avoid redundancy
                                    G[cell_parity][cell].append((i2, j2))
                                    G[neighbor_parity][(i2, j2)].append(cell)

        return G

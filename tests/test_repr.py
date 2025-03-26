import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from color_grid_game import *
import unittest

class Test_Repr(unittest.TestCase):
    
    def test_repr_grid00(self):
        grid = Grid.grid_from_file("input/grid00.in", read_values=True)
        self.assertEqual(repr(grid), "<grid.Grid: n=2, m=3>")
        
    def test_repr_grid03(self):
        grid = Grid.grid_from_file("input/grid03.in", read_values=False)
        self.assertEqual(repr(grid), "<grid.Grid: n=4, m=8>")
        
    def test_repr_grid11(self):
        grid = Grid.grid_from_file("input/grid11.in", read_values=True)
        self.assertEqual(repr(grid), "<grid.Grid: n=10, m=20>")
        
if __name__ == '__main__':
    unittest.main()

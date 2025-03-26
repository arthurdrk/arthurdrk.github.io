import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from color_grid_game import *
import unittest

class TestAllPairs(unittest.TestCase):
    
    def test_simple_grid(self):
        grid = Grid.grid_from_file("input/grid00.in", read_values=True)
        expected_pairs = [((0, 0), (0, 1)), ((0, 0), (0, 2)), ((0, 0), (1, 0)), 
                          ((0, 0), (1, 1)), ((0, 0), (1, 2)), ((0, 1), (0, 2)), 
                          ((0, 1), (1, 0)), ((0, 1), (1, 1)), ((0, 1), (1, 2)), 
                          ((0, 2), (1, 0)), ((0, 2), (1, 1)), ((0, 2), (1, 2)), 
                          ((1, 0), (1, 1)), ((1, 0), (1, 2)), ((1, 1), (1, 2))]
        self.assertEqual(sorted(grid.all_pairs("new rules")), sorted(expected_pairs))

    def test_with_forbidden_cells(self):
        grid = Grid.grid_from_file("input/grid01.in", read_values=True)
        expected_pairs = [((0, 0), (0, 2)), ((0, 0), (1, 0)), ((0, 0), (1, 1)), 
                          ((0, 0), (1, 2)), ((0, 2), (1, 2)), ((1, 0), (1, 1)), 
                          ((1, 1), (1, 2))]
        self.assertEqual(sorted(grid.all_pairs("new rules")), sorted(expected_pairs))
        
    def test_with_forbidden_cells2(self):
        grid = Grid.grid_from_file("input/grid02.in", read_values=True)
        expected_pairs = [((0, 0), (0, 2)), ((0, 0), (1, 0)), ((0, 0), (1, 1)), 
                          ((0, 0), (1, 2)), ((0, 2), (1, 2)), ((1, 0), (1, 1)), 
                          ((1, 1), (1, 2))]
        self.assertEqual(sorted(grid.all_pairs("new rules")), sorted(expected_pairs))
        
if __name__ == '__main__':
    unittest.main()


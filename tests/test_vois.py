import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from color_grid_game import *
import unittest

class TestVois(unittest.TestCase):
    
    def test_grid00_center_cell(self):
        grid = Grid.grid_from_file("input/grid00.in", read_values=True)
        expected_neighbors = [(0, 0), (0, 2), (1, 1)]
        self.assertEqual(sorted(grid.vois(0, 1)), sorted(expected_neighbors))

    def test_grid00_corner_cell(self):
        grid = Grid.grid_from_file("input/grid00.in", read_values=True)
        expected_neighbors = [(0, 1), (1, 0)]
        self.assertEqual(sorted(grid.vois(0, 0)), sorted(expected_neighbors))
    
    def test_grid01_corner_cell(self):
        grid = Grid.grid_from_file("input/grid01.in", read_values=True)
        expected_neighbors = [(0, 1), (1, 0), (1, 2)]
        self.assertEqual(sorted(grid.vois(1, 1)), sorted(expected_neighbors))

    def test_grid05_center_cell(self):
        grid = Grid.grid_from_file("input/grid05.in", read_values=True)
        expected_neighbors = [(2, 4), (3, 3), (3, 5)]
        self.assertEqual(sorted(grid.vois(3, 4)), sorted(expected_neighbors))

    def test_grid05_corner_cell(self):
        grid = Grid.grid_from_file("input/grid05.in", read_values=True)
        expected_neighbors = [(0, 1), (1, 0)]
        self.assertEqual(sorted(grid.vois(0, 0)), sorted(expected_neighbors))

    def test_grid05_edge_cell(self):
        grid = Grid.grid_from_file("input/grid05.in", read_values=True)
        expected_neighbors = [(0, 0), (2, 0), (1, 1)]
        self.assertEqual(sorted(grid.vois(1, 0)), sorted(expected_neighbors))

if __name__ == '__main__':
    unittest.main()

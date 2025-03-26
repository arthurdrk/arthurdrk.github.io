import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from color_grid_game import *
import unittest

class TestSolverFordFulkersonRun(unittest.TestCase):
    
    def test_fordfulkerson_run_grid00(self):
        grid = Grid.grid_from_file("input/grid00.in", read_values=False)
        solver = SolverFordFulkerson(grid)
        pairs = solver.run()
        expected_pairs = [((0, 0), (1, 0)), ((0, 2), (1, 2)), ((1, 1), (0, 1))] #Calculated by hand
        self.assertEqual(sorted(pairs), sorted(expected_pairs))

    def test_fordfulkerson_run_grid01(self):
        grid = Grid.grid_from_file("input/grid01.in", read_values=False)
        solver = SolverFordFulkerson(grid)
        pairs = solver.run()
        expected_pairs = [((0, 2), (1, 2)), ((1, 1), (1, 0))] #Calculated by hand
        self.assertEqual(sorted(pairs), sorted(expected_pairs))

    def test_fordfulkerson_run_grid02(self):
        grid = Grid.grid_from_file("input/grid02.in", read_values=False)
        solver = SolverFordFulkerson(grid)
        pairs = solver.run()
        expected_pairs = [((0, 2), (1, 2)), ((1, 1), (1, 0))] #Calculated by hand
        self.assertEqual(sorted(pairs), sorted(expected_pairs))

if __name__ == '__main__':
    unittest.main()

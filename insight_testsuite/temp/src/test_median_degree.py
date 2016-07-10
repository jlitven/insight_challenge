#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-07-08 15:02:27
# @Author  : Joshua Litven (jlitven@gmail.com)
# @Link    : https://github.com/jlitven
# @Version : $Id$
"""
Unit tests for median_degree.
"""

import unittest
from datetime import datetime
from median_degree import Edge, VenmoGraph

class TestEdge(unittest.TestCase):
    """Unit tests for the Edge class."""

    def create_test_edge(self, date_str):
        """Create an edge with a given date string."""
        return Edge('v1', 'v2', date_str)

    def test_create_edge_basic(self):
        """Test creating a basic edge."""
        edge = self.create_test_edge('2016-03-28T23:25:21Z')

        self.assertEqual(edge.v1, 'v1')
        self.assertEqual(edge.v2, 'v2')
        correct_date = datetime(2016, 3, 28, 23, 25, 21)
        self.assertEqual(edge.created_time, correct_date)

    def test_create_edge_bad_dates(self):
        """Test creating an edge with an incorrect date."""
        with self.assertRaises(ValueError):
            self.create_test_edge('bad_date')

        with self.assertRaises(ValueError):
            self.create_test_edge('2016-13-28T23:25:21Z')

        with self.assertRaises(ValueError):
            self.create_test_edge('2016-03-28T-1:25:21Z')

        with self.assertRaises(ValueError):
            self.create_test_edge('2016-03-28T23:25:100Z')

class TestVenmoGraph(unittest.TestCase):
    """Unit tests for VenmoGraph class."""

if __name__ == '__main__':
    unittest.main()

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
import copy
from datetime import datetime, timedelta
from median_degree import Edge, VenmoGraph, create_edge

def create_basic_edge(date_str='2016-03-28T23:25:21Z'):
    """Create an edge with a given date string."""
    return Edge('v1', 'v2', date_str)

def create_basic_venmograph():
    """Create a venmo graph with one edge and two vertices."""
    edge = create_basic_edge()
    graph = VenmoGraph()
    graph.add_edge(edge)
    return graph

class TestEdge(unittest.TestCase):
    """Unit tests for the Edge class."""

    def test_create_edge_basic(self):
        """Test creating a basic edge."""
        edge = create_basic_edge()

        self.assertEqual(edge.v1, 'v1')
        self.assertEqual(edge.v2, 'v2')
        correct_date = datetime(2016, 3, 28, 23, 25, 21)
        self.assertEqual(edge.created_time, correct_date)

    def test_create_edge_bad_dates(self):
        """Test creating an edge with an incorrect date."""
        with self.assertRaises(ValueError):
            create_basic_edge('bad_date')

        with self.assertRaises(ValueError):
            create_basic_edge('2016-13-28T23:25:21Z')

        with self.assertRaises(ValueError):
            create_basic_edge('2016-03-28T-1:25:21Z')

        with self.assertRaises(ValueError):
            create_basic_edge('2016-03-28T23:25:100Z')

class TestVenmoGraph(unittest.TestCase):
    """Unit tests for VenmoGraph class."""

    def test_empty_venmograph(self):
        """Test creating an empty Venmo graph."""
        graph = VenmoGraph()
        edge = create_basic_edge()

        self.assertIsNone(graph.get_degree(0))
        self.assertIsInstance(graph.newest_time(), datetime)
        self.assertIsNone(graph.get_median_degree())
        self.assertTrue(graph.within_time_window(edge))

    def test_add_edge_after_window(self):
        """Test adding an edge after the current time window."""
        graph = create_basic_venmograph()

        # add edge so previous edge stays inside time window
        edge = create_basic_edge()
        time_delta = timedelta(seconds=graph.window_seconds - 1)
        edge.created_time = edge.created_time + time_delta
        graph.add_edge(edge)
        self.assertEqual(len(graph.edges), 2)
        self.assertEqual(graph.degrees['v1'], 2)
        self.assertEqual(graph.degrees['v2'], 2)

        # add edge so previous edges are outside time window
        newest_time = graph.newest_time()
        time_delta = timedelta(seconds=graph.window_seconds + 1)
        edge = create_basic_edge()
        edge.created_time = newest_time + time_delta
        graph.add_edge(edge)

        self.assertEqual(len(graph.edges), 1)
        self.assertEqual(graph.degrees['v1'], 1)
        self.assertEqual(graph.degrees['v2'], 1)

    def test_add_edge_inside_window(self):
        """Test adding an edge inside the current time window."""
        graph = create_basic_venmograph()
        edge = create_basic_edge()
        newest_time = graph.newest_time()
        time_delta = timedelta(seconds=graph.window_seconds)
        edge.created_time = newest_time - time_delta
        graph.add_edge(edge)

        self.assertEqual(len(graph.edges), 2)
        self.assertEqual(graph.degrees['v1'], 2)
        self.assertEqual(graph.degrees['v2'], 2)
        self.assertLess(graph.edges[0].created_time, graph.edges[1].created_time)

    def test_add_edge_before_window(self):
        """Test adding an edge before the current time window."""
        graph = create_basic_venmograph()
        edge = create_basic_edge()
        newest_time = graph.newest_time()
        time_delta = timedelta(seconds=graph.window_seconds + 1)
        edge.created_time = newest_time - time_delta

        self.assertEqual(len(graph.edges), 1)
        self.assertEqual(graph.degrees['v1'], 1)
        self.assertEqual(graph.degrees['v2'], 1)

    def test_get_degree(self):
        """Test get_degree with different graphs."""
        graph = create_basic_venmograph()

        self.assertEqual(graph.get_degree(0), 1)
        self.assertEqual(graph.get_degree(1), 1)

        edge = create_basic_edge()
        graph.add_edge(edge)

        self.assertEqual(graph.get_degree(0), 2)
        self.assertEqual(graph.get_degree(1), 2)

        edge = create_basic_edge()
        edge.v1 = 'v3'
        graph.add_edge(edge)

        self.assertEqual(graph.get_degree(0), 1)
        self.assertEqual(graph.get_degree(1), 2)
        self.assertEqual(graph.get_degree(2), 3)

    def test_newest_time(self):
        """Test newest_time with different graphs."""
        graph = create_basic_venmograph()

        self.assertEqual(graph.newest_time(),
                         graph.edges[0].created_time)

        # add edge so newest time does NOT change
        edge = create_basic_edge()
        newest_time = graph.edges[0].created_time
        time_delta = timedelta(seconds=1)
        edge.created_time = newest_time - time_delta
        graph.add_edge(edge)

        self.assertEqual(graph.newest_time(), newest_time)

        # add edge so newest time does change
        edge = create_basic_edge()
        newest_time = graph.edges[0].created_time
        time_delta = timedelta(seconds=1)
        edge.created_time = newest_time + time_delta
        graph.add_edge(edge)

        self.assertNotEqual(graph.newest_time(), newest_time)

    def test_within_time_window(self):
        """Test within_time_window with different graphs."""
        graph = create_basic_venmograph()
        edge = create_basic_edge()

        self.assertTrue(graph.within_time_window(edge))

        # this edge is most definitely within the time window
        edge = create_basic_edge()
        time_delta = timedelta(seconds=graph.window_seconds + 1000)
        edge.created_time = graph.newest_time() + time_delta

        self.assertTrue(graph.within_time_window(edge))

        # this edge is most definitely NOT within the time window
        edge = create_basic_edge()
        edge.created_time = graph.newest_time() - time_delta

        self.assertFalse(graph.within_time_window(edge))

    def test_get_median_degree(self):
        """Test get_median_degree with different graphs."""
        graph = create_basic_venmograph()

        self.assertEqual(graph.get_median_degree(), 1)

        edge = create_basic_edge()
        graph.add_edge(edge)

        self.assertEqual(graph.get_median_degree(), 2)

        edge = create_basic_edge()
        edge.v1 = 'v3'
        graph.add_edge(edge)

        self.assertEqual(graph.get_median_degree(), 2)

        edge = create_basic_edge()
        edge.v1 = 'v4'
        graph.add_edge(edge)

        self.assertEqual(graph.get_median_degree(), 1.5)

        edge = create_basic_edge()
        edge.v1 = 'v5'
        edge.v2 = 'v6'
        graph.add_edge(edge)

        self.assertEqual(graph.get_median_degree(), 1)

        edge = create_basic_edge()
        edge.v1 = 'v5'
        edge.v2 = 'v1'
        graph.add_edge(edge)

        self.assertEqual(graph.get_median_degree(), 1.5)

class TestMisc(unittest.TestCase):
    """Unit tests for misc functions."""

    def test_create_edge(self):
        """Test creating an edge from a Venmo transaction."""
        trans = {
            "created_time": "2016-03-28T23:25:12Z",
            "target": "Santa Claus",
            "actor": "Easter Bunny"}
        edge = create_edge(trans)
        self.assertEqual(edge.v1, trans['actor'])
        self.assertEqual(edge.v2, trans['target'])
        self.assertEqual(edge.created_time, datetime(2016, 3, 28, 23, 25, 12))

if __name__ == '__main__':
    unittest.main()

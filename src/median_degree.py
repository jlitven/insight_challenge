#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-07-08 09:55:37
# @Author  : Joshua Litven (jlitven@gmail.com)
# @Link    : https://github.com/jlitven
# @Version : $Id$

"""
Find the median degree of a graph generated by Venmo payment data.
"""
import sys
from collections import defaultdict
from datetime import datetime
from datetime import timedelta
import json

class Edge():
    """Represent an edge in a venmo graph."""
    def __init__(self, v1, v2, date_str):
        """
        Create an Edge.
        Input:
        v1 - A vertex in the graph
        v2 - A vertex in the graph
        date_str - A time stamp, with format YYYY-MM-DDThh:mm:ssZ
                    e.g. 2016-03-28T23:25:21Z
        Output:
            An edge
        """
        self.v1 = v1
        self.v2 = v2
        self.created_time = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')

    def vertices(self):
        """Return the vertices."""
        return self.v1, self.v2

class VenmoGraph():
    """
    A Venmo graph G = (V, E) with vertices (V) and edges (E). The degrees
    of the vertices are stored to efficiently compute the rolling median of
    the degrees.

    The edges are stored as a list and a set:
        edges - stores the edges, sorted by time
        edges_dict - stores the edges as a dict

    The degrees of the vertices are stored as two dicts:
        degrees - stores the degrees by vertex name
        degree_buckets - stores the degree count by degree
    """
    def __init__(self):
        """Create a Venmo Graph."""
        self.edges = []
        self.edge_dict = {}
        self.degrees = {}
        self.degree_buckets = defaultdict(int)
        self.window_seconds = 60

    def __str__(self):
        """Format the graph's edges as a string."""
        result = 'Edges:\n'
        for e in self.edges:
            result += '{} - {} ({})\n'.format(e.v1, e.v2, e.created_time)
        return result

    def add_edge(self, edge):
        """
        Add the edge to the graph, and update the vertex degrees.
        """
        if not self.within_time_window(edge):
            return

        if edge.created_time > self.newest_time():
            time_delta = timedelta(seconds=self.window_seconds)
            threshold_time = edge.created_time - time_delta
            self._remove_edges(threshold_time)

        self._insert_edge(edge)
        self._update_degrees_add(edge)

    def _insert_edge(self, edge):
        """
        Insert edge into the correct position, ordered by time.
        """
        insert_index = len(self.edges)
        for g_edge in reversed(self.edges):
            if edge.created_time > g_edge.created_time or insert_index == 0:
                break
            insert_index -= 1
        self.edges.insert(insert_index, edge)

    def _update_degrees_add(self, edge):
        """
        Update the degrees of the vertices connected to the edge
        once it is added.

        If a vertex is not in the graph, add it to the graph with degree 1.
        Otherwise increase the degree by 1.
        """
        for vertex in edge.vertices():
            if vertex not in self.degrees:
                self.degrees[vertex] = 1
                self.degree_buckets[1] += 1
            else:
                degree = self.degrees[vertex]
                self.degree_buckets[degree] -= 1
                self.degree_buckets[degree + 1] += 1
                self.degrees[vertex] += 1

    def _remove_edges(self, threshold_time):
        """
        Remove all edges below and including the threshold time and
        update vertex degrees.
        """
        start_index = 0
        for index, edge in enumerate(self.edges):
            if edge.created_time <= threshold_time:
                self._update_degrees_remove(edge)
                start_index = index + 1

        self.edges = self.edges[start_index:]

    def _update_degrees_remove(self, edge):
        """
        Update the degrees of the vertices connected to the edge
        once it is removed.
        """
        for vertex in edge.vertices():
            degree = self.degrees[vertex]
            self.degree_buckets[degree] -= 1
            self.degrees[vertex] -= 1
            if self.degrees[vertex] == 0:
                del self.degrees[vertex]
            else:
                self.degree_buckets[degree - 1] += 1

    def get_degree(self, index):
        """Return the degree from the buckets."""
        bucket_index = 0
        for degree, bucket_size in self.degree_buckets.iteritems():
            if bucket_index + bucket_size > index:
                return degree
            else:
                bucket_index += bucket_size

    def newest_time(self):
        """Return the newest created time of an edge."""
        if not self.edges:
            return datetime.min
        return self.edges[-1].created_time

    def within_time_window(self, edge):
        """Return True if the time is within the graph's 60-second
        window or newer.
        """
        if not self.edges:
            return True

        newest_time = self.edges[-1].created_time
        window_start = newest_time - timedelta(seconds=self.window_seconds)
        return edge.created_time > window_start

    def get_median_degree(self):
        """
        Calculate the median degree of the vertices. Assumes the
        vertices are sorted.
        """
        length = len(self.degrees)
        if not length:
            return None

        if length % 2 == 0:
            index = length / 2
            median = (self.get_degree(index) + self.get_degree(index - 1)) / 2.0
        else:
            index = (length - 1) / 2
            median = float(self.get_degree(index))
        return median

def create_edge(transaction):
    """Create an edge from a Venmo transaction."""
    edge = Edge(transaction['actor'],
                transaction['target'],
                transaction['created_time'])
    return edge

def gen_median_degrees(input_file):
    """
    Generate the median degrees of a graph generated from
    input taken from the Venmo API.
    """
    graph = VenmoGraph()

    with open(input_file, 'r') as source:
        for i, line in enumerate(source):
            transaction = json.loads(line)
            try:
                edge = create_edge(transaction)
                graph.add_edge(edge)
            except:
                print ('WARNING: Transaction on line {} '
                       'could not be processed:{}'.format(i, transaction))
            else:
                yield graph.get_median_degree()

def main():
    """Write the degree median of a source Venmo Graph to file."""
    if len(sys.argv) < 3:
        print 'Usage: {} input.txt output.txt'.format(sys.argv[0])
        return
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(output_file, 'w') as output:
        for median in gen_median_degrees(input_file):
            output.write("{:.2f}".format(median) + '\n')

if __name__ == '__main__':
    sys.exit(main())

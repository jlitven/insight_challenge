# Insight Coding Challenge
Joshua Litven

11.07.2016

## Description
This is my solution to the Insight coding challenge.

The challenge is described as follows:

Given a data stream containing Venmo user payment activity, represent the dynamic graph in a 60-second sliding window and compute the rolling median of the vertices' degrees.

For more details check out their [Github page](https://github.com/InsightDataScience/coding-challenge).

## Implementation
To solve this challenge we define a VenmoGraph object, which stores the state of the Venmo user's relationships in the 60-second time window.  When a transaction between users is processed, the corresponding edge is added to the graph if it falls within the time window. Edges outside the time window are then removed. The degrees of the vertices are updated and the rolling median is computed.

To ensure efficiency, the edge lists are ordered by time so the oldest edges are easily found and removed. Each edge list is hashed by its vertices for fast lookup and checking for duplicates. Additionally, vertex degrees are stored in buckets counting the number of vertices with a given degree. This results in efficient updates and calculation of the median.

My solution is implemented in Python.
## Testing
Unit tests can be found in the `src` folder, called `test_median_degree.py`.

Unit tests can be run with the following from the `insight_testsuite` folder:

insight_testsuite$ ./run_unit_tests.sh

To run both unit tests and simulation tests, use:

insight_testsuite$ ./run_tests.sh

## Required Libraries
All libraries are built-in Python libraries. The following packages were used:

`sys`, `collection`, `datetime`, `json`, `unittest`

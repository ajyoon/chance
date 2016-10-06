# blur
#### 0.4 (development branch)

[![Build Status](https://travis-ci.org/ajyoon/blur.svg?branch=dev)](https://travis-ci.org/ajyoon/blur)  [![Documentation Status](https://readthedocs.org/projects/blur/badge/?version=latest)](http://blur.readthedocs.io/en/latest/?badge=latest)

blur is a suite of tools for Python to help make using chance operations in
algorithmic art easier.

```python
>>> from blur.markov.graph import Graph
>>> word_distance_weights = {-5: 1, -1: 2, 1: 8, 3: 3}
>>> graph = Graph.from_string('blur is a suite of tools '
... 'to help make using chance operations in algorithmic '
... 'art easier', word_distance_weights)
>>> print(' '.join(graph.pick().value for i in range(8)))
using chance algorithmic in algorithmic art easier blur
```

*blur* allows you to easily implement complex chance generated elements
in your works without getting bogged down in the boilerplate and the
nitty-gritty math. Besides [Python](https://www.python.org/) (version 2.7 or 3.x),
it has no dependencies, making it easy to incorporate into your project.

### Installation

To install *blur* use pip from the command line:

    pip install blur

You can read the latest (unstable) documentation for *blur* online [here](http://blur.readthedocs.io/en/latest/).

***

### Contributing
Feature requests, bug reports, and pull requests are all welcomed!
Head on over to https://github.com/ajyoon/blur and get in touch.

See CONTRIBUTING.md for help getting started.

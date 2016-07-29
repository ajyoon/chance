# blur
#### 0.2dev (unstable)

[![Build Status](https://travis-ci.org/ajyoon/blur.svg?branch=0.2dev)](https://travis-ci.org/ajyoon/blur)  [![Documentation Status](https://readthedocs.org/projects/blur/badge/?version=latest)](http://blur.readthedocs.io/en/latest/?badge=latest)

blur is a suite of tools for Python to help make using chance operations in
algorithmic art easier.

```python
>>> from blur.markov.graph import Graph
>>> word_distance_weights = {-5: 1, -1: 2, 1: 8, 3: 3}
>>> graph = Graph.from_string('blur is a suite of tools '
... 'to help make using chance operations in algorithmic '
... 'art easier', word_distance_weights)
>>> print(' '.join(graph.pick().name for i in range(8)))
using chance algorithmic in algorithmic art easier blur
```

Naive implementations of chance operations in algorithmic art often rely
on uniform probability distributions.

```python
# [Imaginary examples of uniform random solutions]
# The standard library random number generation module
import random
# Add oscillators with random frequencies between 220Hz and 880Hz
for i in range(100):
    add_oscillator(frequency=random.randint(220, 880))
# --------------------------------------------------------------
# Pick a random color for an object
apple.fill_color_rgb = (random.randint(200, 255),
                        random.randint(180, 230),
                        random.randint(20, 60))
# --------------------------------------------------------------
# Choose a word
print('I have {0} to say and I am saying it and that is poetry.'.format(
    random.choice(['nothing', 'something', 'everything'])))
```
While for many situations these types of uniform random processes are perfectly
suitable, they are limited in scope and run the risk of causing chance output
to feel static or arbitrarily uniform. What if you want to add a hundred
oscillators whose frequencies tend toward, but aren't limited to, 440Hz? What
if you want to color an apple somewhere between bright red and a natural green?
What if you have a large field of words that might appear in your poem but you
slightly prefer some over others?

*blur* allows you to easily implement complex chance generated elements
in your works without getting bogged down in the boilerplate and the
nitty-gritty math.

```python
from blur import soft, rand
frequency_profile = rand.normal_distribution(mean=440, variance=50)
for i in range(100):
    add_oscillator(frequency=weighted_rand(frequency_profile))
# -----------------------------------------------------------------
color = soft.SoftColor(red=([(255, 10), (100, 0)],),
                       green=([(200, 10), (100, 0)],),
                       blue=([(0, 20), (80, 1)],))
apple.fill_color_rgb = color.get()
# -----------------------------------------------------------------
words = soft.SoftOptions([('nothing', 10),
                          ('something', 3),
                          ('everything', 1)])
print('I have {0} to say and I am saying it and that is poetry.'.format(
    words.get())
```

At the heart of *blur* is the ``rand`` module, which contains a series of
functions for finding non-uniform random numbers based on customizable weights.
*blur* also comes with a model markov graph, a tool for deriving markov graphs
from text, a collection of soft objects whose values vary according to
customizable weights and rules, and a model I Ching.

Besides [Python](https://www.python.org/) (version 2.7 or 3.x),
*blur* has no dependencies, making it easy to incorporate into your project.

To install *blur* use pip from the command line:

    pip install blur

You can read the latest official documentation for *blur* online
[here](blur.readthedocs.io/en/latest/).

***

#### Contributing
Feature requests, bug reports, and pull requests are all welcomed!
Head on over to https://github.com/ajyoon/blur and get in touch.


#### Testing
The test suite is located in the `tests` directory. Travis has been
configured to automatically run these tests on any changes in the
git repository, but you can run these tests yourself as well.
Travis tests run on `nose`, but any testing framework compatible
with the built-in Python `Unittest` module should work. To get `nose`
you can install it with `pip`:

    pip install nose

To run the tests, navigate to `tests` and run nose:

    cd blur/tests
    nosetests *.py

or alternatively:

    cd blur
    nosetests tests/*.py

#### Building the documentation
To get the requirements to build the documentation, navigate to
the docs folder and install from doc_requirements.txt

    cd blur/doc
    pip install -r doc_requirements.txt

To build, simply navigate to the ``doc`` folder and call ``make html``

    cd blur/doc
    make html

###### TODO:
* Add examples
* Refine documentation

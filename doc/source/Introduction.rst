Introduction
************

*blur* is a suite of tools for `Python <https://www.python.org/>`_ to help make
using chance operations in algorithmic art easier. ::

    >>> from blur.markov.graph import Graph
    >>> word_distance_weights = {-5: 1, -1: 2, 1: 8, 3: 3}
    >>> graph = Graph.from_string('blur is a suite of tools to help make using '
    ... 'chance operations in algorithmic art easier', word_distance_weights)
    >>> print(' '.join(graph.pick().value for i in range(10)))

using chance algorithmic in algorithmic art easier blur easier blur

Naive implementations of chance operations in algorithmic art often rely
on uniform probability distributions. ::

    # [Imaginary examples of naive solutions]
    # The standard library random number generation module
    >>> import random
    # Add a hundred oscillators with random frequencies between 220Hz and 880Hz
    >>> for i in range(100):
    ...     add_oscillator(frequency=random.randint(220, 880))
    # -------------------------------------------------------------------------
    # Pick a random color for an object
    >>> apple.fill_color_rgb = (random.randint(0, 255),
    ...                         random.randint(0, 255),
    ...                         random.randint(0, 255))
    # -------------------------------------------------------------------------
    # Choose a word
    >>> print('I have {0} to say and I am saying it and that is poetry.'.format(
    ...     random.choice(['nothing', 'something', 'everything'])))

While for many situations these types of uniform random processes are perfectly
suitable, they are limited in scope and run the risk of causing chance output
to feel static or arbitrarily uniform. What if you want to add a hundred
oscillators whose frequencies tend toward, but aren't limited to, 440Hz? What
if you want to color an apple somewhere between bright red and a natural green?
What if you have a large field of words that might appear in your poem but you
slightly prefer some over others?

*blur* allows you to easily implement complex chance generated elements
in your works without getting bogged down in the boilerplate and the
nitty-gritty math. ::

    >>> from blur import soft, rand
    >>> frequency_profile = rand.normal_distribution(mean=440, variance=50)
    >>> for i in range(100):
    ...     add_oscillator(frequency=weighted_rand(frequency_profile))
    # -------------------------------------------------------------------------
    >>> color = soft.SoftColor(red=([(255, 10), (100, 0)],),
    ...                        green=([(200, 10), (100, 0)],),
    ...                        blue=([(0, 20), (80, 1)],))
    >>> apple.fill_color_rgb = color.get()
    # -------------------------------------------------------------------------
    >>> words = soft.SoftOptions([('nothing', 10),
    ...                           ('something', 3),
    ...                           ('everything', 1)])
    >>> print('I have {0} to say and I am saying it and that is poetry.'.format(
    ...     words.get())

At the heart of *blur* is the ``rand`` module, which contains a series of
functions for finding non-uniform random numbers based on customizable weights.
*blur* also comes with a model markov graph, a tool for deriving markov graphs
from text, a collection of soft objects whose values vary according to
customizable weights and rules, and a model I Ching.

Besides `Python <https://www.python.org/>`_ (version 2.7 or 3.x),
*blur* has no dependencies, making it easy to incorporate into your project.

To install *blur* use pip from the command line: ::

    $ pip install blur

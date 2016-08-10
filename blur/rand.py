"""
A collection of functions for performing non-uniform random operations.

Many functions rely of weight ``tuple`` 's of the form ``(outcome, weight)``
where ``weight`` is a number and ``outcome`` is either a number
or any type depending on the function.
"""

from __future__ import division
import copy
import random
import math

from warnings import warn


###############################################################################
#   Module-specific Exception classes
###############################################################################
class ProbabilityUndefinedError(Exception):
    """Exception raised when the probability of a system is undefined."""
    pass


###############################################################################
#   Local utility functions
###############################################################################
def _linear_interp(curve, test_x, round_result=False):
    """
    Take a series of points and interpolate between them at ``test_x``.

    Args:
        curve (list[tuple]): A list of ``(x, y)`` points sorted in
            nondecreasing ``x`` value. If multiple points have the same
            ``x`` value, all but the last occuring will be ignored.
        test_x (float): The ``x`` value to find the ``y`` value of

    Returns:
        float: The ``y`` value of the curve at ``test_x``

    Raises:
        ValueError if ``test_x`` is out of the domain of ``curve``
    """
    index = 0
    for index in range(len(curve) - 1):
        # Ignore points which share an x value with the following point
        if curve[index][0] == curve[index + 1][0]:
            continue
        if curve[index][0] <= test_x <= curve[index + 1][0]:
            slope = ((curve[index + 1][1] - curve[index][1]) /
                     (curve[index + 1][0] - curve[index][0]))
            y_intercept = curve[index][1] - (slope * curve[index][0])
            result = (slope * test_x) + y_intercept
            if round_result:
                return int(round(result))
            else:
                return result
    else:
        raise ValueError


def _point_under_curve(curve, point):
    """
    Determine if a point is under a piecewise curve.

    Points within ``curve`` must be sorted in nondecreasing order by x value.
    If multiple points in ``curve`` have the same x value, all but the last
    will be ignored.

    Args:
        curve [(x, y)]:
        point (x, y):

    Returns:
        bool: Whether the point is under the curve
    """
    try:
        return _linear_interp(curve, point[0]) > point[1]
    except ValueError:
        return False


def _clamp_value(value, minimum, maximum):
    """
    Clamp a value to fit between a minimum and a maximum.

    * If ``value`` is between ``minimum`` and ``maximum``, return ``value``
    * If ``value`` is below ``minimum``, return ``minimum``
    * If ``value is above ``maximum``, return ``maximum``

    Args:
        value (float or int): The number to clamp
        minimum (float or int): The lowest allowed return value
        maximum (float or int): The highest allowed return value

    Returns:
        float or int: the clamped value

    Raises:
        ValueError: if maximum < minimum
    """
    if maximum < minimum:
        raise ValueError
    if value < minimum:
        return minimum
    elif value > maximum:
        return maximum
    else:
        return value


def _normal_function(x, mean, variance):
    """
    Find a value in the cumulative distribution function of a normal curve.

    See https://en.wikipedia.org/wiki/Normal_distribution

    Args:
        x (float):
        mean (float):
        variance (float):
    """
    e_power = -1 * (((x - mean) ** 2) / (2 * variance))
    return (1 / math.sqrt(2 * variance * math.pi)) * (math.e ** e_power)


###############################################################################
# Methods
###############################################################################
def bound_weights(weights, minimum=None, maximum=None):
    """
    Bound a weight list so that all outcomes fit within specified bounds.

    The probability distribution within the minimum and maximum values remains
    the same. Weights in the list with outcomes outside of ``minimum`` and
    ``maximum`` are removed. If weights are removed from either end, attach
    weights at the modified edges at the same weight (y-axis) position they
    had interpolated in the original list.

    At least one of ``minimum`` and ``maximum`` must be set.
    If both are set, minimum must be less than maximum.

    Args:
        weights (List[(float, float)]): the list of weights where each weight
            is a ``tuple`` of form ``(float, float)`` corresponding to
            ``(outcome, weight)``. Must be sorted in increasing order
            of outcomes
        minimum (float): Lowest allowed outcome for the weight list
        maximum (float): Highest allowed outcome for the weight list

    Returns:
        List: A ``list`` of ``tuple`` 's of form ``(float, float)``,
        the bounded weight list.

    Raises:
        TypeError: if both ``minimum`` and ``maximum`` are ``None``
        ValueError: if ``maximum < minimum``
    """
    # Copy weights to avoid side-effects
    bounded_weights = weights[:]
    # Remove weights outside of minimum and maximum
    if minimum is not None and maximum is not None:
        if maximum < minimum:
            raise ValueError
        bounded_weights = [bw for bw in bounded_weights
                           if minimum <= bw[0] <= maximum]
    elif minimum is not None:
        bounded_weights = [bw for bw in bounded_weights
                           if minimum <= bw[0]]
    elif maximum is not None:
        bounded_weights = [bw for bw in bounded_weights
                           if bw[0] <= maximum]
    else:
        # Both minimum and maximum are not defined
        raise TypeError
    # If weights were removed, attach new endpoints where they would have
    # appeared in the original curve
    if (bounded_weights[0][0] > weights[0][0] and
            bounded_weights[0][0] != minimum):
        bounded_weights.insert(0, (minimum, _linear_interp(weights, minimum)))
    if (bounded_weights[-1][0] < weights[-1][0] and
            bounded_weights[-1][0] != maximum):
        bounded_weights.append((maximum, _linear_interp(weights, maximum)))
    return bounded_weights


def normal_distribution(mean, variance,
                        minimum=None, maximum=None, weight_count=23):
    """
    Return a list of weights approximating a normal distribution.

    Args:
        mean (float): The mean of the distribution
        variance (float): The variance of the distribution
        minimum (float): The minimum outcome possible to
            bound the output distribution to
        maximum (float): The maximum outcome possible to
            bound the output distribution to
        weight_count (Optional[int]): The number of weights that will
            be used to approximate the distribution

    Returns:
        list[(float, float)]: a list of weights approximating
            a normal distribution.

    Raises:
        ValueError: ``if maximum < minimum``
        TypeError: if both ``minimum`` and ``maximum`` are ``None``
    """
    # Pin 0 to +- 5 sigma as bounds, or minimum and maximum
    # if they cross +/- sigma
    standard_deviation = math.sqrt(variance)
    min_x = (standard_deviation * -5) + mean
    max_x = (standard_deviation * 5) + mean
    step = (max_x - min_x) / weight_count
    current_x = min_x
    weights = []
    while current_x < max_x:
        weights.append((current_x,
                        _normal_function(current_x, mean, variance)))
        current_x += step
    if minimum is not None or maximum is not None:
        return bound_weights(weights, minimum, maximum)
    else:
        return weights


def prob_bool(probability):
    """
    Return ``True`` or ``False`` depending on ``probability``.

    Args:
        probability (float): Probability between ``0`` and ``1``
            to return ``True`` where ``0`` is guaranteed to return
            ``False`` and ``1`` is guaranteed to return ``True``.

    Returns:
        bool: ``True`` or ``False`` depending on ``probability``.
    """
    return random.uniform(0, 1) < probability


def percent_possible(percent):
    """
    Return True ``percent`` / 100 times.

    Args:
        percent (int or float): percent possibility to return True

    Returns:
        bool: Either ``True`` or ``False`` depending on ``percent``
    """
    return random.uniform(0, 100) < percent


def pos_or_neg(value, prob_pos=0.5):
    """
    Return either positive or negative ``value`` based on ``prob_pos``.

    This is equivalent to ``abs(value) * pos_or_neg_1(prob_pos)``.

    Args:
        value (int or float): the value to operate on
        prob_pos (Optional[float]): The probability to return positive.
            where ``prob_pos = 0`` is guaranteed to return negative and
            ``prob_pos = 1`` is guaranteed to return positive.
            Default value is ``0.5``.

    Returns:
        int or float: ``value`` either positive or negative
    """
    return abs(value) * pos_or_neg_1(prob_pos)


def pos_or_neg_1(prob_pos=0.5):
    """
    Return either ``1`` with probability of ``prob_pos``, otherwise ``-1``.

    Args:
        prob_pos (Optional[float]): The probability to return positive ``1``
            where ``prob_pos = 0`` is guaranteed to return negative and
            ``prob_pos = 1`` is guaranteed to return positive.
            Default value is ``0.5``.

    Returns:
        int: either ``1`` or ``-1``
    """
    if random.uniform(0, 1) < prob_pos:
        return 1
    else:
        return -1


def weighted_rand(weights, round_result=False):
    """
    Generate a non-uniform random value based on a list of tuple weights.

    Treats weights as coordinates for a probability distribution curve and
    rolls accordingly. Constructs a piece-wise linear curve according to
    coordinates given in input_weights and rolls random values in the
    curve's bounding box until a value is found under the curve

    Weight tuples should be of the form: (outcome, weight).

    Args:
        weights: (List[(float, float)]): the list of weights where each weight
            is a ``tuple`` of form ``(float, float)`` corresponding to
            ``(outcome, weight)``. All weights outcome values must be numbers.
            Weights with weight ``0`` or less will have no chance to be
            rolled. Must be sorted in increasing order of outcomes.
        round_result (Optional[Bool])):

    Returns:
        float or int: A number between the smallest and largest outcomes
            in ``weights``
    """
    # If just one weight is passed, simply return the weight's name
    if len(weights) == 1:
        return weights[0][0]

    # Is there a way to do this more efficiently? Maybe even require that
    # ``weights`` already be sorted?
    weights = sorted(weights, key=lambda w: w[0])

    x_min = weights[0][0]
    x_max = weights[-1][0]
    y_min = 0
    y_max = max([point[1] for point in weights])

    # Roll random numbers until a valid one is found
    attempt_count = 0
    while attempt_count < 500000:
        # Get sample point
        sample = (random.uniform(x_min, x_max), random.uniform(y_min, y_max))
        if _point_under_curve(weights, sample):
            # The sample point is under the curve
            if round_result:
                return int(round(sample[0]))
            else:
                return sample[0]
        attempt_count += 1
    else:
        warn('Point not being found in weighted_rand() after 500000 '
             'attempts, defaulting to a random weight point. '
             'If this happens often, it is probably a bug, so please let us '
             'know with a bug report at https://github.com/ajyoon/blur')
        return random.choice(weights)[0]


def weighted_choice(weights, as_index_and_value_tuple=False):
    """
    Generate a non-uniform random choice based on a list of option tuples.

    Treats each outcome as a discreet unit with a chance to occur.

    Args:
        weights: (List[(Any, float)]): a list of options where each option
            is a ``tuple`` of form ``(Any, float)`` corresponding to
            ``(outcome, weight)``. Outcome values may be of any type.
            Options with weight ``0`` or less will have no chance to be
            rolled - if this is the case in every item of ``weights``,
            a ``ValueError`` is raised.
        as_index_and_value_tuple (bool): Option to return an ``(index, value)``
            tuple instead of just a single ``value``. This is useful when
            multiple values in ``weights`` are the same and you need to know
            exactly which one was picked.

    Returns:
        Any: If as_index_and_value_tuple == False, any one of the items in
            the outcomes of ``weights``
        tuple (int, Any): If as_index_and_value_tuple == True, a tuple of
            the index as well as value of the item that was picked.

    Raises:
        ValueError: if ``weights`` is an empty list.
        ProbabilityUndefinedError: if no item weights in
            ``weights`` are greater than 0.
        AssertionError: if something in the function is broken.
    """
    if not len(weights):
        raise ValueError('List passed to weighted_choice() cannot be empty.')
    # Construct a line segment where each weight outcome is
    # allotted a length equal to the outcome's weight,
    # pick a uniformally random point along the line, and take
    # the outcome that point corresponds to
    prob_sum = sum(w[1] for w in weights)
    if prob_sum <= 0:
        raise ProbabilityUndefinedError(
            'No item weights in weighted_choice() are greater than 0. '
            'Probability distribution is undefined.')
    sample = random.uniform(0, prob_sum)
    current_pos = 0
    i = 0
    while i < len(weights):
        if current_pos <= sample <= (current_pos + weights[i][1]):
            if as_index_and_value_tuple:
                return (i, weights[i][0])
            else:
                return weights[i][0]
        current_pos += weights[i][1]
        i += 1
    else:
        raise AssertionError('Something went wrong in weighted_choice(). '
                             'Please submit a bug report!')


def weighted_order(weights):
    """
    Non-uniformally order a list according to weighted priorities.

    ``weights`` is a list of tuples of the form ``(item, weight)`` of
    types ``(Any, float or int)``. The output list is constructed by repeatedly
    calling ``weighted_choice()`` on the weights, adding items to the end of
    the list as the are picked.

    Higher value weights will have a higher chance of appearing near the
    beginning of the output list.

    A list of all uniform weights is equivalent to calling ``random.shuffle()``
    on the list of values.

    All weight values must be greater than 0
    or a ``ProbabilityUndefinedError`` will be raised.

    Passing an empty list will return an empty list.

    Args:
        weights (list[(Any, float or int)]):

    Returns:
        list: the newly ordered list

    Raises:
        ProbabilityUndefinedError: if any weight value is below 0.
    """
    if not len(weights):
        return []
    if any(w[1] <= 0 for w in weights):
        raise ProbabilityUndefinedError(
            'All weight values must be greater than 0.')
    working_list = weights[:]
    output_list = []
    while working_list:
        picked_item = weighted_choice(working_list,
                                      as_index_and_value_tuple=True)
        output_list.append(picked_item[1])
        del working_list[picked_item[0]]
    return output_list

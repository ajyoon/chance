#!/usr/bin/env python3

import copy
import random


class Weight:
    def __init__(self, outcome, weight):
        self.x = outcome
        self.y = weight


class PointNotFoundError(Exception):
    pass


def _linear_interp(x1, y1, x2, y2, x3, round_result=False):
    """Take two points and interpolate between them at x3"""
    slope = (y2 - y1) / (x2 - x1)
    y_int = y1 - (slope * x1)
    result = (slope * x3) + y_int
    if round_result:
        return int(round(result))
    else:
        return result


def markov_weights_dict(min_key, max_key):
    """
    Generate a dictionary of {distance, weight} pairs for use in
    network.word_mine()
    """
    pairs = random_weight_list(min_key, max_key, 1)
    return dict((weight.x, weight.y) for weight in pairs)


# TODO: Test me!
def merge_markov_weights_dicts(dict_1, dict_2, ratio):
    """Merge two markov_weights_dict's
    where ratio the weight of dict_1 to dict_2.
    Ratio must be greater than 0 and less than or equal to 1"""
    min_key = min(list(dict_1.keys()) + list(dict_2.keys()))
    max_key = max(list(dict_1.keys()) + list(dict_2.keys()))

    def interp_dict(in_dict):
        """Return a copy of in_dict with interpolated values for every
        integer key within the range of in_dict's keys"""
        out_dict = {}
        min_key = min(list(in_dict.keys()))
        max_key = max(list(in_dict.keys()))
        for key in range(min_key, max_key):
            if key in in_dict:
                out_dict[key] = in_dict[key]
            else:
                # We need to interpolate this key in out_dict
                # Find the nearest key to the left and right
                # (because the min and max keys are defined,
                # we have no edge case to deal with)
                lower_key = max([k for k in in_dict.keys() if k < key])
                lower_value = in_dict[lower_key]
                higher_key = min([k for k in in_dict.keys() if k > key])
                higher_value = in_dict[lower_key]
                out_dict[key] = _linear_interp(lower_key, lower_value,
                                               higher_key, higher_value,
                                               key)
        return out_dict

    interp_dict_1 = interp_dict(dict_1)
    interp_dict_2 = interp_dict(dict_2)
    # Merge the two dicts
    merged_dict = {}
    for key in range(min_key, max_key):
        if key in interp_dict_1 and key not in interp_dict_2:
            merged_dict[key] = interp_dict_1[key]
        elif key in interp_dict_2 and key not in interp_dict_1:
            merged_dict[key] = interp_dict_2[key]
        else:
            # Merge the values
            # If KeyError occurs, fix something above
            # There is probably some 4th grade algebra way to simplify this
            weighted_value = ((interp_dict_1[key] * ratio) +
                              (interp_dict_2[key] * (1 / ratio))) / 2
            merged_dict[key] = weighted_value

    return merged_dict


def weighted_curve_rand(weights, round_result=False):
    """
    Generate a non-uniform random value based on a list of input_weights or
    tuples. Treats input_weights as coordinates for a probability
    distribution curve and rolls accordingly. Constructs a piece-wise linear
    curve according to coordinates given in input_weights and rolls random
    values in the curve's bounding box until a value is found under the curve
    All input_weights outcome values must be numbers.

    Args:
        weights [(outcome, weight)]:
        round_result (Bool):

    Returns: float or int

    """
    if not isinstance(weights, list):
        weights = [weights]

    # TODO: Is it really necessary to copy the weights?
    weights = copy.copy(weights)

    # Loop through every weight in weights[] and make sure that they are
    # Weight objects, converting if not
    i = 0
    while i < len(weights):
        if isinstance(weights[i], Weight):
            pass
        elif isinstance(weights[i], tuple):
            weights[i] = Weight(weights[i][0], weights[i][1])
        else:
            raise TypeError(
                    "Weight at index {0} is not a valid type".format(str(i)))
        i += 1

    # TODO: Sort through all weight objects,
    # averaging the y value of objects with the same x
    """
    cleaned_weights = []
    for index in range(0, len(weights)):
        for test_index in range(0, len(weights)):
            if index == test_index:
                continue
            if weights[index].x == weights[test_index].x:
                mean_y = (weights[index].y + weights[test_index].y) / 2.0
                cleaned_weights.append((weights[index].x, mean_y))
    """

    # If just one weight is passed, simply return the weight's name
    if len(weights) == 1:
        return weights[0].x

    # Sort list so that weights are listed in order of ascending X name
    weights = sorted(weights, key=lambda this_weight: this_weight.x)

    # TODO: Refactor this to use the newly defined _linear_interp()
    x_min = min([point.x for point in weights])
    x_max = max([point.x for point in weights])
    y_min = min([point.y for point in weights])
    y_max = max([point.y for point in weights])
    # Roll random numbers until a valid one is found
    point_found = False
    attempt_count = 0
    while not point_found:
        # Get sample point
        sample = Weight(random.uniform(x_min, x_max),
                        random.uniform(y_min, y_max))
        for i in range(0, len(weights) - 1):
            if weights[i].x <= sample.x <= weights[i + 1].x:
                slope = ((weights[i + 1].y - weights[i].y) /
                         (weights[i + 1].x - weights[i].x))
                y_int = weights[i].y - (slope * weights[i].x)
                curve_y = (slope * sample.x) + y_int
                if sample.y <= curve_y:
                    # The sample point is under the curve
                    if round_result:
                        return int(round(sample.x))
                    else:
                        return sample.x
        attempt_count += 1
        if attempt_count == 10000:
            print("WARNING: Point in weighted_curve_rand() not being"
                  "found after over 10000 attempts,"
                  "something is probably wrong")


def weighted_option_rand(weights):
    """
    Generate a non-uniform random value based on a list of input_weights or
    tuples. treats each outcome (Weight.x) as a discreet unit with a chance
    to occur. Constructs a line segment where each weight is outcome is
    alloted a length and rolls a random point. input_weights outcomes may be
    of any type, including instances

    Args:
        input_weights [(outcome, weight)]:

    Returns: a random name based on the weights

    """

    if not isinstance(weights, list):
        weights = [weights]

    # TODO: Is it really necessary to copy the weights?
    weights = copy.copy(weights)

    # Loop through every weight in weights[] and make sure that they are
    # Weight objects, converting if not
    i = 0
    while i < len(weights):
        if isinstance(weights[i], Weight):
            pass
        # Could cause issues with older code, but nodes really should be cast
        #  to Weights outside of this module
        # elif isinstance(weights[i], nodes.Node):
        #     weights[i] = Weight(weights[i].name, weights[i].use_weight)
        elif isinstance(weights[i], tuple):
            weights[i] = Weight(weights[i][0], weights[i][1])
        else:
            raise TypeError(
                    "Weight at index {0} is not a valid type".format(str(i)))

        i += 1

    # If just one weight is passed, simply return the weight's x value
    if len(weights) == 1:
        return weights[0].x

    # Find total name of points y coords
    prob_sum = 0
    for current_point in weights:
        prob_sum += current_point.y
    rand_num = random.uniform(0, prob_sum)
    current_pos = 0
    index = 0
    while index < len(weights):
        if current_pos <= rand_num <= (current_pos + weights[index].y):
            return weights[index].x
        current_pos += weights[index].y
        index += 1
    # If we have made it this far,
    # the point was not found and something is wrong
    raise PointNotFoundError("Point at %s was not found in "
                             "discreet_weighted_rand!" % rand_num)


def random_weight_list(min_outcome, max_outcome, max_weight_density=0.1,
                       max_possible_weights=None):
    """
    Generate a list of Weight within a given min_outcome and max_outcome bound.

    Args:
        min_outcome (int or float):
        max_outcome (int or float):
        max_weight_density (float):  the maximum density of resulting weights
        max_possible_weights (int):

    Returns: [Weight]

    """

    # TODO: get rid of max_weight_density, its use is confusing and redundant

    # Prevent sneaky errors
    # Add resolution multiplier if either min_outcome or max_outcome are floats
    resolution_multiplier = None
    if ((not isinstance(min_outcome, int)) or
            (not isinstance(max_outcome, int))):
        resolution_multiplier = 1000.0
        min_outcome = int(round(min_outcome * resolution_multiplier))
        max_outcome = int(round(max_outcome * resolution_multiplier))
    if min_outcome > max_outcome:
        swapper = min_outcome
        min_outcome = max_outcome
        max_outcome = swapper

    # Set max_weights according to max_weight_density
    max_weights = int(round((max_outcome - min_outcome) * max_weight_density))

    if (max_possible_weights is not None) and (
            max_weights > max_possible_weights):
        max_weights = max_possible_weights

    # Create and populate weight_list

    # Pin down random weights at min_outcome and max_outcome to keep the
    # weight_list properly bounded
    weight_list = [Weight(min_outcome, random.randint(1, 100)),
                   Weight(max_outcome, random.randint(1, 100))]

    # Main population loop. Subtract 2 from max_weights to account for
    # already inserted start and end caps
    for i in range(0, max_weights - 2):
        outcome = random.randint(min_outcome, max_outcome)
        is_duplicate_outcome = False
        # Test contents in weight_list to make sure
        # none of them have the same outcome
        for index in range(0, len(weight_list)):
            if weight_list[index].x == outcome:
                is_duplicate_outcome = True
                break
        if not is_duplicate_outcome:
            weight_list.append(Weight(outcome, random.randint(1, 100)))

    # Sort the list
    weight_list = sorted(weight_list, key=lambda z: z.x)

    # Undo resolution multiplication if necessary
    if resolution_multiplier is not None:
        resolved_weight_list = []
        for old_weight in weight_list:
            resolved_weight_list.append(Weight(
                round((old_weight.x / resolution_multiplier), 3),
                old_weight.y))
        weight_list = resolved_weight_list

    return weight_list

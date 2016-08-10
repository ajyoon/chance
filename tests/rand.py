"""
Tests for functions in the ``rand`` module.

Due to the stochastic nature of many of these functions,
this is not absolute proof that the functions are working as expected.
False failures, while highly unlikely, are possible.

If something fails and you aren't sure why, try re-running
the tests a few times before going bug-hunting.
"""

from __future__ import division

import unittest
import math
import random

from blur import rand


class TestRand(unittest.TestCase):
    """Tests for all methods in the ``rand`` module."""
    def test__linear_interp(self):
        # Positive integer slope with and without rounding
        self.assertAlmostEqual(
            rand._linear_interp([(0, 0), (2, 2)], 1, round_result=False),
            1)
        self.assertAlmostEqual(
            rand._linear_interp([(0, 0), (2, 2)], 1, round_result=True),
            1)
        # Negative integer slope with and without rounding
        self.assertAlmostEqual(
            rand._linear_interp([(-2, -2), (0, 0)], -1, round_result=False),
            -1)
        self.assertAlmostEqual(
            rand._linear_interp([(-2, -2), (0, 0)], -1, round_result=True),
            -1)
        # Positive non-integer slope with and without rounding
        self.assertAlmostEqual(
            rand._linear_interp([(0, 0), (4, 1)], 1, round_result=True),
            0)
        self.assertAlmostEqual(
            rand._linear_interp([(0, 0), (4, 1)], 1, round_result=False),
            0.25)
        # Negative non-integer slope with and without rounding
        self.assertAlmostEqual(
            rand._linear_interp([(-4, -1), (0, 0)], -1, round_result=True),
            0)
        self.assertAlmostEqual(
            rand._linear_interp([(-4, -1), (0, 0)], -1, round_result=False),
            -0.25)
        # Three points in curve with and without rounding
        self.assertAlmostEqual(
            rand._linear_interp([(0, 0), (2, 2), (18, 7)],
                                1, round_result=False), 1)
        self.assertAlmostEqual(
            rand._linear_interp([(0, 0), (2, 2), (18, 7)],
                                1, round_result=True), 1)
        # test_x out of the domain of the curve
        with self.assertRaises(ValueError):
            rand._linear_interp([(0, 0), (2, 2)], -1, round_result=False)

    def test__point_under_curve(self):
        # Build several random curves and test points below the minimum
        # and above the maximum
        MIN_X = -100
        MIN_Y = -100
        MAX_X = 100
        MAX_Y = 100
        curve = [(random.randint(-100, 100), random.randint(-100, 100))
                 for i in range(30)]
        # Attach points to domain bounds at MIN_Y
        curve.append((MIN_X, MIN_Y))
        curve.append((MAX_X, MIN_Y))
        # Sort the points in the curve as this is a requirement of the function
        curve.sort(key=lambda p: p[0])

        # Point guaranteed to be under the random curve
        point_under = ((MIN_X + MAX_X) / 2, MIN_Y - 1)
        self.assertTrue(rand._point_under_curve(curve, point_under))
        # Point guaranteed to be over the random curve
        point_over = ((MIN_X + MAX_X) / 2, MAX_Y + 1)
        self.assertFalse(rand._point_under_curve(curve, point_over))
        # Points outside the x domain of the random curve
        point_out_of_lower_x_bound = (MIN_X - 1, MIN_Y - 1)
        self.assertFalse(rand._point_under_curve(
            curve, point_out_of_lower_x_bound))
        point_out_of_upper_x_bound = (MAX_X + 1, MIN_Y - 1)
        self.assertFalse(rand._point_under_curve(
            curve, point_out_of_upper_x_bound))
        # Points under the curve but on the curve bounds
        point_on_lower_x_bound = (MIN_X, MIN_Y - 1)
        self.assertTrue(rand._point_under_curve(
            curve, point_on_lower_x_bound))
        point_on_upper_x_bound = (MAX_X, MIN_Y - 1)
        self.assertTrue(rand._point_under_curve(
            curve, point_on_upper_x_bound))

    def test__clamp_value(self):
        # value between minimum and maximum returns value
        self.assertEqual(rand._clamp_value(value=5, minimum=4, maximum=6), 5)
        # value on minimum returns value
        self.assertEqual(rand._clamp_value(value=5, minimum=5, maximum=6), 5)
        # value on maximum returns value
        self.assertEqual(rand._clamp_value(value=6, minimum=4, maximum=6), 6)
        # value below minimum returns minimum
        self.assertEqual(rand._clamp_value(value=3, minimum=4, maximum=6), 4)
        # value above maximum returns maximum
        self.assertEqual(rand._clamp_value(value=7, minimum=4, maximum=6), 6)
        # maximum below minimum raises ValueError
        with self.assertRaises(ValueError):
            rand._clamp_value(value=5, minimum=3, maximum=2)

    def test_bound_weights_with_bad_bounds_raises_ValueError(self):
        weights = [(0, 0), (2, 2), (4, 2), (6, 0)]
        with self.assertRaises(ValueError):
            rand.bound_weights(weights, 10, 5)

    def test_bound_weights_without_bounds_raises_TypeError(self):
        weights = [(0, 0), (2, 2), (4, 2), (6, 0)]
        with self.assertRaises(TypeError):
            rand.bound_weights(weights)

    def test_bound_weights_doesnt_modify_input(self):
        weights = [(0, 0), (2, 2), (4, 2), (6, 0)]
        original_weights = weights[:]
        modified = rand.bound_weights(weights, 2, 4)
        self.assertEqual(weights, original_weights)

    def test_bound_weights_with_weights_already_inside_bounds(self):
        # When all weights are already inside bounds,
        # rand.bound_weights() should have no effect
        weights = [(0, 0), (2, 2), (4, 2), (6, 0)]
        modified = rand.bound_weights(weights, -2, 8)
        self.assertEqual(weights, modified)

    def test_bound_weights_clipping_on_existing_weights(self):
        weights = [(0, 0), (2, 2), (4, 2), (6, 0)]
        self.assertEqual(rand.bound_weights(weights, 2, 4),
                         [(2, 2), (4, 2)])

    def test_bound_weights_clipping_between_existing_weights(self):
        weights = [(0, 0), (2, 2), (4, 2), (6, 0)]
        self.assertEqual(rand.bound_weights(weights, 1, 5),
                         [(1, 1), (2, 2), (4, 2), (5, 1)])

    def test_bound_weights_with_only_one_bound(self):
        weights = [(0, 0), (2, 2), (4, 2), (6, 0)]
        # With only minimum
        self.assertEqual(rand.bound_weights(weights, minimum=1),
                         [(1, 1), (2, 2), (4, 2), (6, 0)])
        # With only maximum
        self.assertEqual(rand.bound_weights(weights, maximum=5),
                         [(0, 0), (2, 2), (4, 2), (5, 1)])

    def test_normal_distribution(self):
        """
        Test the accuracy of ``rand.normal_distribution()``.

        Use the curve it creates to generate a large number of samples,
        and then calculate the real variance and mean of the resulting
        sample group and compare the two within a comfortable margin.
        """
        MEAN = -12
        VARIANCE = 2.5
        STANDARD_DEVIATION = math.sqrt(VARIANCE)
        SAMPLE_COUNT = 1000
        curve = rand.normal_distribution(MEAN, VARIANCE, weight_count=30)
        samples = [rand.weighted_rand(curve) for i in range(SAMPLE_COUNT)]
        samples_mean = sum(samples) / len(samples)
        samples_variance = (
            sum((s - samples_mean) ** 2 for s in samples) /
            len(samples)
        )
        mean_diff = abs(MEAN - samples_mean)
        variance_diff = abs(VARIANCE - samples_variance)
        self.assertLess(mean_diff, abs(MEAN / 4))
        self.assertLess(variance_diff, abs(VARIANCE / 4))

    def test_normal_distribution_with_bounds(self):
        MEAN = -12
        VARIANCE = 20
        MIN_X = -15
        MAX_X = 5
        curve = rand.normal_distribution(MEAN, VARIANCE, MIN_X, MAX_X)
        self.assertEqual(min(weight[0] for weight in curve), MIN_X)
        self.assertEqual(max(weight[0] for weight in curve), MAX_X)

    def test_prob_bool(self):
        # Test guaranteed outcomes
        self.assertTrue(rand.prob_bool(100))
        self.assertTrue(rand.prob_bool(1))
        self.assertFalse(rand.prob_bool(0))
        self.assertFalse(rand.prob_bool(-100))
        # Test that probabilties are working as expected
        true_count = 0
        for i in range(1000):
            if rand.prob_bool(0.2):
                true_count += 1
        self.assertTrue(5 <= true_count <= 400)

    def test_percent_possible(self):
        # Test guaranteed outcomes
        self.assertTrue(rand.prob_bool(1000))
        self.assertTrue(rand.prob_bool(100))
        self.assertFalse(rand.prob_bool(0))
        self.assertFalse(rand.prob_bool(-1000))
        # Test that probabilties are working as expected
        true_count = 0
        for i in range(1000):
            if rand.percent_possible(20):
                true_count += 1
        self.assertTrue(5 <= true_count <= 400)

    def test_pos_or_neg_with_given_prob(self):
        # Test guaranteed outcomes
        self.assertEqual(rand.pos_or_neg(5, 10), 5)
        self.assertEqual(rand.pos_or_neg(5, 1), 5)
        self.assertEqual(rand.pos_or_neg(5, 0), -5)
        self.assertEqual(rand.pos_or_neg(5, -10), -5)
        # Test that probabilties are working as expected
        pos_count = 0
        for i in range(1000):
            if rand.pos_or_neg(5, 0.2) == 5:
                pos_count += 1
        self.assertTrue(5 <= pos_count <= 400)

    def test_pos_or_neg_without_given_prob(self):
        # Test that probabilties are working as expected
        pos_count = 0
        for i in range(1000):
            if rand.pos_or_neg(5) == 5:
                pos_count += 1
        self.assertTrue(300 <= pos_count <= 700)

    def test_pos_or_neg_1_with_given_prob(self):
        # Test guaranteed outcomes
        self.assertEqual(rand.pos_or_neg_1(10), 1)
        self.assertEqual(rand.pos_or_neg_1(1), 1)
        self.assertEqual(rand.pos_or_neg_1(0), -1)
        self.assertEqual(rand.pos_or_neg_1(-10), -1)
        # Test that probabilties are working as expected
        pos_count = 0
        for i in range(1000):
            if rand.pos_or_neg_1(0.2) == 1:
                pos_count += 1
        self.assertTrue(5 <= pos_count <= 400)

    def test_pos_or_neg_1_without_given_prob(self):
        # Test that probabilties are working as expected
        pos_count = 0
        for i in range(1000):
            if rand.pos_or_neg_1() == 1:
                pos_count += 1
        self.assertTrue(300 <= pos_count <= 700)

    def test_weighted_choice(self):
        options = [(0, 1), (5, 2), (10, 5)]
        zero_count = 0
        five_count = 0
        ten_count = 0
        for i in range(1000):
            result = rand.weighted_choice(options)
            if result == 0:
                zero_count += 1
            elif result == 5:
                five_count += 1
            elif result == 10:
                ten_count += 1
            else:
                self.fail('Unexpected weighted_choice'
                          'result {0}'.format(result))
        self.assertTrue(25 <= zero_count <= 250)
        self.assertTrue(50 <= five_count <= 600)
        self.assertTrue(300 <= ten_count <= 900)

    def test_weighted_choice_as_tuple(self):
        options = [(1, 0), (5, -1), (10, 5), (19, 1)]
        for i in range(25):
            result = rand.weighted_choice(options, True)
            expected_index = next(
                i for i, option in enumerate(options)
                if option[0] == result[1])
            self.assertEqual(expected_index, result[0])

    def test_weighted_choice_with_empty_list(self):
        with self.assertRaises(ValueError):
            foo = rand.weighted_choice([])

    def test_weighted_choice_with_all_non_pos_weights(self):
        with self.assertRaises(rand.ProbabilityUndefinedError):
            foo = rand.weighted_choice([(1, 0), (5, 0), (10, 0)])

    def test_weighted_choice_with_mixed_pos_neg_weights(self):
        options = [(1, 0), (5, -1), (10, 5), (19, 1)]
        for i in range(25):
            self.assertIn(rand.weighted_choice(options),
                          [10, 19])

    def test_weighted_choice_with_one_weight_returns_it(self):
        weight_list = [('The Only Weight', 2)]
        expected_result = weight_list[0][0]
        self.assertEqual(rand.weighted_choice(weight_list), expected_result)

    def test_weighted_rand_with_one_weight_returns_it(self):
        weight_list = [('The Only Weight', 2)]
        expected_result = weight_list[0][0]
        self.assertEqual(rand.weighted_rand(weight_list), expected_result)

    def test_weighted_rand_and_choice_with_one_weight_equivalent(self):
        weight_list = [('The Only Weight', 2)]
        self.assertEqual(rand.weighted_rand(weight_list),
                         rand.weighted_choice(weight_list))

    def test_weighted_rand_with_arbitrary_curve(self):
        """
        Test ``rand.weighted_rand()``.

        Find a large number of points from a randomly built weight distribution
        and comparing the distribution against the expectation using a crude
        histogram model.
        """
        MIN_X = -1000
        MIN_Y = 0
        MAX_X = 1000
        MAX_Y = 1000
        curve = [(random.randint(MIN_X, MAX_X), random.randint(MIN_Y, MAX_Y))
                 for i in range(30)]
        # Attach points to domain bounds at MIN_Y
        curve.append((MIN_X, MIN_Y))
        curve.append((MAX_X, MIN_Y))
        # Sort the points in the curve as this is a
        # requirement of _linear_interp()
        curve.sort(key=lambda p: p[0])

        BIN_WIDTH = 1
        bins = {b: 0 for b in range(MIN_X, MAX_X, BIN_WIDTH)}
        TEST_COUNT = 1000
        for i in range(TEST_COUNT):
            point = rand.weighted_rand(curve, round_result=False)
            # Match the found point to the closest bin to the left
            bins[int(math.floor(point / BIN_WIDTH) * BIN_WIDTH)] += 1
        # Make sure the binning is working as expected
        self.assertEqual(sum(values for i, values in bins.items()), TEST_COUNT,
                         msg='This test itself is broken! '
                             'Not all rolled points were matched to a bin.')
        sum_probability = 0
        for bin_x in bins.keys():
            sum_probability += rand._linear_interp(curve, bin_x)
        for bin_x, count in bins.items():
            bin_probability = rand._linear_interp(curve, bin_x)
            expected_count = (bin_probability / sum_probability) * TEST_COUNT
            self.assertLess(abs(count - expected_count), TEST_COUNT / 10)

    def test_weighted_order_doesnt_modify_original(self):
        original_list = [('Something', 10),
                         ('Another',   5),
                         ('Again',     1),
                         ('And',       700),
                         ('More',      5)]
        input_list = original_list[:]
        shuffled = rand.weighted_order(input_list)
        self.assertEqual(input_list, original_list)

    def test_weighted_order_output_type(self):
        original_list = [('Something', 10),
                         ('Another',   5),
                         ('Again',     1),
                         ('And',       700),
                         ('More',      5)]
        shuffled = rand.weighted_order(original_list)
        for item in shuffled:
            self.assertIsInstance(item, str)

    def test_weighted_order_doesnt_lose_or_add_items(self):
        original_list = [('Something', 10),
                         ('Another',   5),
                         ('Again',     1),
                         ('And',       700),
                         ('More',      5)]
        shuffled = rand.weighted_order(original_list)
        self.assertEqual(len(original_list), len(shuffled))
        for item in original_list:
            self.assertIn(item[0], shuffled)

    def test_weighted_order_with_extremely_strong_weight(self):
        original_list = [('Something', 10),
                         ('Another',   5),
                         ('Again',     1),
                         ('And',       7000),
                         ('More',      5)]
        success_count = 0
        TRIALS = 500
        for i in range(TRIALS):
            shuffled = rand.weighted_order(original_list)
            if shuffled.index('And') == 0:
                success_count += 1
        self.assertGreater(success_count, TRIALS * 0.75)

    def test_weighted_order_with_all_1_weights(self):
        # When every weight is 0, the probability spread should be uniform
        original_list = [('Something', 1),
                         ('Another',   1),
                         ('Again',     1),
                         ('And',       1),
                         ('More',      1)]
        landing_positions = {'Something': [],
                             'Another': [],
                             'Again': [],
                             'And': [],
                             'More': []}
        for i in range(1000):
            shuffled_list = rand.weighted_order(original_list)
            for index, value in enumerate(shuffled_list):
                landing_positions[value].append(index)
        # With an even distribution, landing indices should average near 2.5
        for positions in landing_positions.values():
            average = sum(positions) / len(positions)
            self.assertLess(abs(average - 2.5), 1)

    def test_weighted_order_with_invalid_weight(self):
        with self.assertRaises(rand.ProbabilityUndefinedError):
            foo = rand.weighted_order([('bar', 0), ('baz', 5), ('buzz', -3)])

    def test_weighted_order_with_empty_list_returns_empty_list(self):
        self.assertEqual(rand.weighted_order([]), [])

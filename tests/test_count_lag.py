"""Test counting serial position transition lag."""

import pytest
import numpy as np
from psifr import transitions


@pytest.fixture()
def data():
    """Create list data with position and category."""
    test_list = {
        'list_length': 8,
        'n_block': 4,
        'pool_position': [1, 2, 3, 4, 5, 6, 7, 8],
        'pool_category': [1, 1, 2, 2, 1, 1, 2, 2],
        'pool_block': [1, 1, 2, 2, 3, 3, 4, 4],
        'output_position': [1, 3, 4, 8, 5, 4, 7, 6],
        'output_category': [1, 2, 2, 2, 1, 2, 2, 1],
        'output_block': [1, 2, 2, 4, 3, 2, 4, 3],
    }
    return test_list


def test_lag_count(data):
    """Test transition counts by serial position lag."""
    actual, possible = transitions.count_lags(
        data['list_length'], [data['pool_position']], [data['output_position']]
    )
    np.testing.assert_array_equal(
        actual.to_numpy(), np.array([0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0])
    )
    np.testing.assert_array_equal(
        possible.to_numpy(), np.array([0, 1, 1, 0, 1, 2, 3, 0, 3, 3, 3, 3, 2, 1, 1])
    )


def test_lag_count_category(data):
    """Test transition counts by lag for within-category transitions."""
    # within category
    actual, possible = transitions.count_lags(
        data['list_length'],
        [data['pool_position']],
        [data['output_position']],
        pool_test=[data['pool_category']],
        recall_test=[data['output_category']],
        test=lambda x, y: x == y,
    )
    np.testing.assert_array_equal(
        actual.to_numpy(), np.array([0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0])
    )
    np.testing.assert_array_equal(
        possible.to_numpy(), np.array([0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 2, 1, 0, 0])
    )

    # across category
    actual, possible = transitions.count_lags(
        data['list_length'],
        [data['pool_position']],
        [data['output_position']],
        pool_test=[data['pool_category']],
        recall_test=[data['output_category']],
        test=lambda x, y: x != y,
    )
    np.testing.assert_array_equal(
        actual.to_numpy(), np.array([0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0])
    )
    np.testing.assert_array_equal(
        possible.to_numpy(), np.array([0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1])
    )


def test_lag_count_block(data):
    """Test transition counts by block lag."""
    actual, possible = transitions.count_lags(
        data['n_block'],
        [data['pool_block']],
        [data['output_block']],
        count_unique=False,
    )
    np.testing.assert_array_equal(actual.to_numpy(), np.array([0, 0, 2, 1, 1, 1, 0]))
    np.testing.assert_array_equal(possible.to_numpy(), np.array([2, 0, 5, 3, 6, 6, 2]))


def test_lag_count_block_unique(data):
    """Test transition counts by unique block lag."""
    actual, possible = transitions.count_lags(
        data['n_block'], [data['pool_block']], [data['output_block']], count_unique=True
    )
    np.testing.assert_array_equal(actual.to_numpy(), np.array([0, 0, 2, 1, 1, 1, 0]))
    np.testing.assert_array_equal(possible.to_numpy(), np.array([2, 0, 4, 3, 3, 3, 1]))


def test_compound_lag_count():
    """Test transition lag count conditional on prior lag."""
    list_length = 4
    pool_position = [[1, 2, 3, 4]]
    output_position = [[4, 1, 2, 3]]
    # -3: +1 (+1, +2)
    # +1: +1 (+1)
    # -3:-3, -3:-2, -3:-1, -3:0, -3:+1, -3:+2, -3:+3, ...
    expected_actual = np.hstack(
        (
            [0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
        )
    )
    expected_possible = np.hstack(
        (
            [0, 0, 0, 0, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
        )
    )
    actual, possible = transitions.count_lags_compound(
        list_length, pool_position, output_position
    )
    np.testing.assert_array_equal(actual, expected_actual)
    np.testing.assert_array_equal(possible, expected_possible)

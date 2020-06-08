"""Test rank-based measures of clustering."""

import numpy as np
import pytest
from psifr import transitions


@pytest.fixture()
def list_data():
    data = {
        'pool_items': [[1, 2, 3, 4, 5, 6]],
        'recall_items': [[6, 2, 1, 5, 4]],
        'pool_test': [[1, 1, 1, 2, 2, 2]],
        'recall_test': [[2, 1, 1, 2, 2]]
    }
    return data


def test_rank_lags(list_data):
    ranks = transitions.rank_lags(
        list_data['pool_items'], list_data['recall_items'],
        list_data['pool_items'], list_data['recall_items'],
    )
    expected = np.array([1 / 4, 5 / 6, 0, 1])
    np.testing.assert_allclose(ranks, expected)


def test_rank_lags_short(list_data):
    ranks = transitions.rank_lags(
        list_data['pool_items'], list_data['recall_items'],
    )
    expected = np.array([1 / 4, 5 / 6, 0, 1])
    np.testing.assert_allclose(ranks, expected)

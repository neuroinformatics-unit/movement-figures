"""Shared test fixtures.

Selecting the ``Agg`` backend here (before ``matplotlib.pyplot`` is imported
anywhere) makes the suite headless regardless of test collection order, and the
autouse fixture resets matplotlib's global state after every test so tests stay
order-independent.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest


@pytest.fixture(autouse=True)
def reset_matplotlib_state():
    """Restore matplotlib defaults and close figures after each test."""
    yield
    plt.close("all")
    matplotlib.rcdefaults()

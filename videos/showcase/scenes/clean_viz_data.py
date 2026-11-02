"""EPM data choices for the clean_viz segment."""

EPM = "DLC_single-mouse_EPM.predictions.h5"

WINDOW = (240, 260)  # s; as the movement applications poster, covers the maze
MAZE_CROP = (320, 1050)  # x range (px) of the EPM frame holding the maze
OCCUPANCY_BIN = 30  # px


def clean_epm(position, confidence):
    """The movement applications poster's cleaning pipeline."""
    from movement.filtering import (
        filter_by_confidence,
        interpolate_over_time,
        rolling_filter,
    )

    position = filter_by_confidence(position, confidence, threshold=0.99)
    position = rolling_filter(position, window=9, statistic="median", min_periods=3)
    return interpolate_over_time(position, method="linear", max_gap=5)

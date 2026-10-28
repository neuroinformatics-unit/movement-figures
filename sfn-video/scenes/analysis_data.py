"""Data for the downstream-analysis panels, computed with movement and cached."""

from pathlib import Path

import numpy as np

CACHE = Path(__file__).resolve().parent.parent / "cache"

EPM = "SLEAP_single-mouse_EPM.analysis.h5"
OCTAGON = "SLEAP_two-mice_octagon.analysis.h5"

OCTAGON_WINDOW = (60, 85)  # s; the mice approach, stay in contact, separate
TRAJECTORY_SECONDS = 60
MAZE_CROP = (320, 1050)  # x range (px) of the EPM frame holding the maze
OCCUPANCY_BIN = 30  # px


def _clean(position, confidence):
    from movement.filtering import (
        filter_by_confidence,
        interpolate_over_time,
        rolling_filter,
        savgol_filter,
    )

    position = filter_by_confidence(position, confidence, threshold=0.6)
    position = rolling_filter(position, window=5, statistic="median", min_periods=2)
    position = interpolate_over_time(position, max_gap=40)
    # SciPy >= 1.17 rejects NaNs in edge windows with the default mode
    return savgol_filter(position, window=7, polyorder=2, mode="nearest")


def _cached(name, build):
    path = CACHE / f"{name}.npz"
    if not path.exists():
        CACHE.mkdir(exist_ok=True)
        np.savez(path, **build())
    return dict(np.load(path))


def octagon_motion():
    """Body speed of both mice and the distance between them."""

    def build():
        from movement import sample_data
        from movement.kinematics import compute_speed

        ds = sample_data.fetch_dataset(OCTAGON)
        position = _clean(ds.position, ds.confidence)
        body = position.sel(keypoint=["Neck", "BodyUpper", "BodyLower"]).mean(
            "keypoint"
        )
        speed = compute_speed(body).rolling(time=10, center=True).mean()
        distance = np.sqrt(
            ((body.isel(individual=0) - body.isel(individual=1)) ** 2).sum("space")
        )
        window = {"time": slice(*OCTAGON_WINDOW)}
        speed, distance = speed.sel(window), distance.sel(window)
        return {
            "t": speed.time.values - OCTAGON_WINDOW[0],
            "speed": speed.transpose("individual", "time").values,
            "distance": distance.values,
        }

    return _cached("octagon_motion", build)

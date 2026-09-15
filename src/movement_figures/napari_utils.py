"""Helpers for capturing napari canvas screenshots of movement datasets."""

import tempfile
from pathlib import Path

import numpy as np
import xarray as xr


def napari_canvas_screenshot(
    ds: xr.Dataset,
    video_path: str | Path,
    frame_index: int,
    tail_length: int = 10,
) -> np.ndarray:
    """Screenshot a single frame of a dataset as shown in the napari GUI.

    Opens the video (via the ``napari-video`` plugin) as an image layer, then
    drives the ``movement`` napari plugin's own data-loading widget
    to add the corresponding points and tracks layers, exactly as a user would
    through the GUI. Jumps to ``frame_index`` and captures the canvas only.

    Parameters
    ----------
    ds
        A ``movement`` poses dataset (already filtered/smoothed as desired).
        Must be a GUI-loadable dataset, i.e. it is written to a temporary
        netCDF file and reloaded exactly as ``DataLoader`` expects (see the
        ``movement`` `GUI guide <target-gui-compatible-netcdf>`_).
    video_path
        Path to the video the dataset was tracked from.
    frame_index
        Frame at which to display the video image and the points/tracks.
    tail_length
        Number of past frames shown as the tracks layer's tail.

    Returns
    -------
    numpy.ndarray
        RGBA screenshot array (height, width, 4) of the napari canvas.

    Notes
    -----
    This opens a real (visible) napari window, since headless/offscreen Qt
    platforms do not reliably provide the OpenGL context that napari's
    canvas needs to render—the window is closed again before returning.
    In CI, run under a virtual display (e.g. ``xvfb-run``).

    """
    import napari
    from movement.napari.loader_widgets import DataLoader

    viewer = napari.Viewer(show=True)
    try:
        viewer.open(str(video_path), plugin="napari_video")

        # DataLoader only accepts data from a file on disk, so round-trip
        # the (already cleaned) dataset through a temporary netCDF file.
        loader = DataLoader(viewer)
        with tempfile.TemporaryDirectory() as tmp_dir:
            nc_path = Path(tmp_dir) / "dataset.nc"
            ds.to_netcdf(nc_path)
            loader.source_software_combo.setCurrentText("movement (netCDF)")
            loader.file_path_edit.setText(str(nc_path))
            loader.load_button.click()

        # DataLoader always sets the tail length to span the whole
        # recording; override it on the layer it just created.
        tracks_layer = next(
            layer
            for layer in reversed(viewer.layers)
            if isinstance(layer, napari.layers.Tracks)
        )
        tracks_layer.tail_length = tail_length

        viewer.dims.current_step = (
            frame_index,
            *viewer.dims.current_step[1:],
        )
        viewer.reset_view()
        screenshot = viewer.screenshot(canvas_only=True)
    finally:
        viewer.close()

    return screenshot

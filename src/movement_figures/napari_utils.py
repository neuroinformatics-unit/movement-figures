"""Helpers for capturing napari canvas screenshots of movement datasets."""

import tempfile
from pathlib import Path

import numpy as np
import xarray as xr

# Buffer (in pixels) added around the points' bounding box when zooming.
_ZOOM_BUFFER_PX = 50.0
# Tail width of the tracks layer
_TAIL_WIDTH = 4.0
# Width (in pixels) the napari canvas is resized to before capture
_CANVAS_WIDTH_PX = 800


def napari_canvas_screenshot(
    ds: xr.Dataset,
    video_path: str | Path,
    frame_index: int,
    tail_length: int = 10,
    zoom: bool = False,
    display_text: bool = True,
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
    zoom
        If ``True``, zoom the camera in on the bounding box of the points
        and tail tracks shown at ``frame_index`` (plus a small buffer),
        instead of fitting the whole video frame in view. Default is ``False``.
    display_text
        If ``True``, show the keypoint point labels

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
        video_layer = viewer.open(str(video_path), plugin="napari_video")[0]
        frame_height, frame_width = video_layer.data.shape[1:3]

        # DataLoader only accepts data from a file on disk, so round-trip
        # the (already cleaned) dataset through a temporary netCDF file.
        loader = DataLoader(viewer)
        with tempfile.TemporaryDirectory() as tmp_dir:
            nc_path = Path(tmp_dir) / "dataset.nc"
            ds.to_netcdf(nc_path)
            loader.source_software_combo.setCurrentText("movement (netCDF)")
            loader.file_path_edit.setText(str(nc_path))
            loader.load_button.click()

        # Configure points layer
        if display_text:
            points_layer = _get_layer_by_type(viewer, napari.layers.Points)
            points_layer.text.visible = True
            points_layer.text.size = 16

        # Configure tracks layer
        tracks_layer = _get_layer_by_type(viewer, napari.layers.Tracks)
        tracks_layer.tail_length = tail_length
        tracks_layer.tail_width = _TAIL_WIDTH

        # Match the canvas aspect ratio to the video frame's, so this screenshot
        # lines up visually with other panels built from the same frame
        canvas_height_px = round(_CANVAS_WIDTH_PX * frame_height / frame_width)
        canvas = viewer.window._qt_viewer.canvas
        canvas.native.resize(_CANVAS_WIDTH_PX, canvas_height_px)

        # Jump to the requested frame
        viewer.dims.current_step = (
            frame_index,
            *viewer.dims.current_step[1:],
        )

        # Zoom if requested, otherwise fit the whole video frame in view
        zoomed = False
        if zoom:
            visible_data = _get_visible_data(
                loader, tracks_layer, frame_index, tail_length
            )
            if visible_data.size:
                _zoom_to_data(viewer, visible_data, buffer=_ZOOM_BUFFER_PX)
                zoomed = True
        if not zoomed:
            viewer.reset_view()

        screenshot = viewer.screenshot(canvas_only=True)
    finally:
        viewer.close()

    return screenshot


def _get_visible_data(
    loader,
    tracks_layer,
    frame_index: int,
    tail_length: int,
) -> np.ndarray:
    """Return the (y, x) coordinates of points and tracks visible on a given frame."""
    points_data = loader.points_layer.data  # (frame_idx, y, x)
    current_points = points_data[points_data[:, 0] == frame_index, 1:]

    tracks_data = tracks_layer.data  # (track_id, frame_idx, y, x)
    tail_mask = (tracks_data[:, 1] <= frame_index) & (
        tracks_data[:, 1] >= frame_index - tail_length
    )
    tail_points = tracks_data[tail_mask, 2:]

    return np.concatenate([current_points, tail_points])


def _get_layer_by_type(viewer, layer_type):
    """Return the first layer of a given type in a napari viewer."""
    return next(
        (layer for layer in reversed(viewer.layers) if isinstance(layer, layer_type)),
        None,
    )


def _zoom_to_data(
    viewer,
    data: np.ndarray,
    buffer: float,
) -> None:
    """Centre and zoom a 2D napari viewer's camera on a set of coordinates.

    Parameters
    ----------
    viewer
        The napari viewer whose camera to adjust.
    data
        Array of shape (N, 2) with (y, x) coordinates to fit in view.
    buffer
        Buffer, in pixels, added around the data's bounding box on every
        side.

    """
    lower = data.min(axis=0) - buffer
    upper = data.max(axis=0) + buffer
    size = upper - lower
    size[size <= 0] = 1.0  # avoid division by zero for degenerate boxes

    viewer.camera.center = tuple((lower + upper) / 2)
    canvas_size = viewer.window._qt_viewer.canvas.size
    viewer.camera.zoom = np.min(np.array(canvas_size) / size)

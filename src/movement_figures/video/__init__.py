"""Tools for making manim videos about movement.

A video lives in its own folder under ``videos/``, described by a
``video.yml`` (see :mod:`movement_figures.video.project`) and rendered with
the ``movement-video`` command. Scenes build on :mod:`.brand` and
:mod:`.elements`, which need the ``video`` dependency group (manim); this
package itself imports without it.
"""

"""Title card, formats converging into the data cube, and export."""

import numpy as np
from common import (
    BLUE,
    FONT,
    GREEN,
    GREY,
    LIGHT_GREY,
    MONO,
    ORANGE,
    badge,
    chip,
    data_cube,
    image,
    show_caption,
    slab_corners,
)
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    ArcBetweenPoints,
    Arrow,
    Dot,
    FadeIn,
    FadeOut,
    Group,
    GrowArrow,
    LaggedStart,
    MoveAlongPath,
    Scene,
    Text,
    VGroup,
    always_redraw,
    linear,
    smooth,
)
from mouse import INDIVIDUALS, Herd

FORMATS = [
    ("DeepLabCut", ".h5 .csv"),
    ("SLEAP", ".slp .h5"),
    ("LightningPose", ".csv"),
    ("Anipose", ".csv"),
    ("COCO", ".json"),
    ("VIA-tracks", ".csv"),
    ("NWB", ".nwb"),
]


def _along(text, a, b, normal_shift):
    """Place text parallel to segment a->b, offset perpendicular to it."""
    d = b - a
    text.rotate(np.arctan2(d[1], d[0]))
    n = np.array([-d[1], d[0], 0]) / np.linalg.norm(d)
    return text.move_to((a + b) / 2 + normal_shift * n)


def cube_labels(cube):
    """Dimension labels around the data cube, as in the overview figure."""
    back, _, front = cube
    bc, fc = slab_corners(back), slab_corners(front)
    style = {"font": MONO, "font_size": 24, "color": LIGHT_GREY}
    time = _along(Text("time", **style), bc["front_bl"], bc["front_tl"], 0.25)
    space = _along(Text("space", **style), fc["front_bl"], fc["front_br"], -0.25)
    keypoints = _along(
        Text("keypoints", **style), fc["front_br"], fc["far_bottom"], -0.28
    )
    individuals = Text("individuals", font=MONO, font_size=24)
    individuals.set_color_by_gradient(GREEN, BLUE, ORANGE)
    _along(individuals, bc["far_top"], fc["far_top"], 0.3)
    return VGroup(time, space, keypoints, individuals)


class Formats(Scene):
    def construct(self):
        # --- Title card -----------------------------------------------------
        logo = image("movement_logo_on-transparent.png", 4.2).shift(0.5 * UP)
        tagline = Text(
            "Python tools for analysing animal motion",
            font=FONT,
            font_size=52,
            color=GREY,
        ).next_to(logo, DOWN, buff=0.3)
        self.play(FadeIn(logo, scale=0.85), run_time=1.2)
        self.play(FadeIn(tagline, shift=0.2 * UP), run_time=0.8)
        self.wait(3.5)

        corner = badge()
        corner_logo, corner_url = corner
        self.play(
            FadeOut(tagline),
            logo.animate.scale(corner_logo.height / logo.height).move_to(corner_logo),
            run_time=1.2,
        )
        self.remove(logo)
        self.add(corner_logo)
        self.play(FadeIn(corner_url), run_time=0.5)

        # --- Formats in -----------------------------------------------------
        chips = Group(*[chip(name, extensions=ext) for name, ext in FORMATS])
        chips.arrange(DOWN, buff=0.13).to_edge(LEFT, buff=0.6).shift(0.35 * UP)
        cap = show_caption(self, "Bring tracks from your favourite tool or format…", 0)
        self.play(
            LaggedStart(*[FadeIn(c, shift=0.4 * RIGHT) for c in chips], lag_ratio=0.15),
            run_time=2.2,
        )
        self.wait(1.2)

        # --- Coalesce into tracked mice ------------------------------------
        herd = Herd(scale=0.0055, centre=(2.6, 0.2), spacing=1.3)
        dots, paths = [], []
        for lane in range(len(INDIVIDUALS)):
            for end in herd.keypoints(lane, 0):
                i = len(dots)
                start = chips[i % len(chips)][0].get_right()
                paths.append(ArcBetweenPoints(start, end, angle=-0.6 + 0.017 * i))
                dots.append(Dot(start, radius=0.07, color=herd.colour(lane)))
        self.play(
            LaggedStart(
                *[
                    MoveAlongPath(d, p, rate_func=smooth)
                    for d, p in zip(dots, paths, strict=True)
                ],
                lag_ratio=0.02,
            ),
            run_time=3.0,
        )
        skeletons = always_redraw(herd.skeletons)
        backdrop = always_redraw(lambda: herd.backdrop(half_width=4.6))
        self.remove(*dots)
        self.add(backdrop, skeletons)
        cap = show_caption(self, "…as keypoints on each animal's body", 0, previous=cap)
        self.play(herd.lines.animate.set_value(1), run_time=1.0)
        self.wait(1.5)

        # --- Walk -----------------------------------------------------------
        self.play(
            FadeOut(chips, shift=0.4 * LEFT),
            herd.scale.animate.set_value(0.011),
            herd.cx.animate.set_value(0.3),
            herd.cy.animate.set_value(0.15),
            herd.spacing.animate.set_value(1.85),
            herd.grid.animate.set_value(1),
            run_time=1.5,
        )
        cap = show_caption(self, "…tracked frame by frame", 0, previous=cap)
        self.play(
            herd.frame.animate.set_value(herd.n_frames - 1),
            run_time=4.5,
            rate_func=linear,
        )

        # --- Data structure -------------------------------------------------
        cube = data_cube().scale(1.05).move_to(2.6 * RIGHT + 0.1 * DOWN)
        self.play(
            herd.grid.animate.set_value(0),
            herd.scale.animate.set_value(0.0052),
            herd.cx.animate.set_value(-3.6),
            herd.cy.animate.set_value(0.0),
            herd.spacing.animate.set_value(1.25),
            run_time=1.4,
        )
        cap = show_caption(self, "…into one tidy dataset", 0, previous=cap)
        self.play(
            LaggedStart(*[FadeIn(s, shift=0.3 * DOWN) for s in cube], lag_ratio=0.35),
            run_time=1.6,
        )
        labels = cube_labels(cube)
        self.play(LaggedStart(*[FadeIn(lb) for lb in labels], lag_ratio=0.2))
        self.wait(1.0)
        cap = show_caption(
            self, "Every animal, every keypoint, every frame", 2.5, previous=cap
        )
        cap = show_caption(
            self,
            "Same tools for every species, every tracker",
            2.5,
            previous=cap,
        )

        # --- Export ---------------------------------------------------------
        skeletons.clear_updaters()
        backdrop.clear_updaters()
        self.remove(backdrop)
        self.play(
            FadeOut(skeletons, shift=0.4 * LEFT),
            FadeOut(cap),
            VGroup(cube, labels).animate.move_to(3.0 * LEFT + 0.2 * UP),
            run_time=1.4,
        )
        nwb = image("NWB_logo.png", 1.5)
        nc = image("netcdf_icon.png", 1.5)
        targets = Group(nwb, nc).arrange(DOWN, buff=1.0).move_to(3.6 * RIGHT + 0.3 * UP)
        names = VGroup(
            Text("NWB", font=FONT, font_size=34, color=GREY),
            Text("netCDF", font=FONT, font_size=34, color=GREY),
        )
        for name, t in zip(names, targets, strict=True):
            name.next_to(t, RIGHT, buff=0.35)
        arrows = VGroup(
            *[
                Arrow(
                    cube.get_right() + 0.3 * RIGHT,
                    t.get_left() + 0.2 * LEFT,
                    color=LIGHT_GREY,
                    stroke_width=5,
                    buff=0,
                )
                for t in targets
            ]
        )
        cap = show_caption(self, "Save to open scientific data standards", 0)
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.3))
        self.play(
            LaggedStart(
                *[
                    FadeIn(Group(t, n), shift=0.2 * LEFT)
                    for t, n in zip(targets, names, strict=True)
                ],
                lag_ratio=0.3,
            )
        )
        self.wait(3.0)
        self.play(
            *[FadeOut(m) for m in self.mobjects if m not in (corner_logo, corner_url)]
        )
        self.wait(0.5)

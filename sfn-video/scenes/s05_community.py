"""Free and open source, who makes and supports movement, and its contributors.

The last segment: it ends on the title card's first frame, so the video
loops seamlessly.
"""

from common import (
    FONT,
    GREY,
    LIGHT_GREY,
    TITLE_LOGO_CENTRE,
    TITLE_LOGO_HEIGHT,
    badge,
    caption,
    image,
    svg_icon,
)
from community import contributors
from manim import (
    DOWN,
    RIGHT,
    UP,
    FadeIn,
    FadeOut,
    Group,
    Rectangle,
    Scene,
    Text,
    VGroup,
    config,
    linear,
)

# Rolling credits: names scroll up in three columns between header and caption
CREDITS_TOP, CREDITS_BOTTOM = 2.85, -2.75
CREDITS_FADE = 0.6  # height of the soft edges at the top and bottom
CREDITS_SIZE = 26
CREDITS_COLUMN = 4.4  # spacing between columns
CREDITS_ROW = 0.5
CREDITS_SPEED = 1.6  # scene units per second
# Host institutes, then funders, left to right; heights balance their weight.
# SWC, the other host, is credited with the team in the row above.
SUPPORTERS = [
    ("UCL-logo-white-simple.png", 0.6),
    ("PDN_logo_white_0.png", 1.3),
    ("wellcome-logo-black.png", 1.0),
    ("GATSBY_Logo_CO-BRANDING_(WCB)_RGB.JPG", 0.95),
]
# The logo slide's rows, top to bottom
ROW_CENTRES = [1.85, 0.0, -1.8]
ROW_ICON = 1.2  # height of the icons in the top two rows
ON_TOP = 2  # z-index of the header and captions, above the credits' masks


def credit(name, x, y):
    """A contributor's name centred at ``x``, on a baseline set by ``y``.

    Centring each name on its own glyphs would shift those with descenders;
    a "|" spans the full line height, so names are placed by it, then it is
    dropped.
    """
    line = Text("|" + name, font=FONT, font_size=CREDITS_SIZE, color=GREY)
    line.shift((y - line[0].get_y()) * UP)
    line.remove(line[0])
    return line.shift((x - line.get_x()) * RIGHT)


def labelled(icon, label):
    """An icon with its name beside it."""
    text = Text(label, font=FONT, font_size=44, color=GREY)
    return Group(icon, text).arrange(RIGHT, buff=0.3)


def credits_mask():
    """White over everything outside the credits window, softening its edges."""
    width = config.frame_width
    mask = VGroup()
    for top, bottom in ((config.frame_height / 2, CREDITS_TOP), (CREDITS_BOTTOM, -4)):
        mask.add(
            Rectangle(
                width=width,
                height=top - bottom,
                fill_color="#ffffff",
                fill_opacity=1,
                stroke_width=0,
            ).move_to([0, (top + bottom) / 2, 0])
        )
    n = 12
    step = CREDITS_FADE / n
    for k in range(n):
        opacity = 1 - (k + 0.5) / n
        for edge, inward in ((CREDITS_TOP, -1), (CREDITS_BOTTOM, 1)):
            mask.add(
                Rectangle(
                    width=width,
                    height=step,
                    fill_color="#ffffff",
                    fill_opacity=opacity,
                    stroke_width=0,
                ).move_to([0, edge + inward * (k + 0.5) * step, 0])
            )
    return mask.set_z_index(1)


class Community(Scene):
    def say(self, text, previous=None):
        """Caption ``text``, kept above the credits' masks."""
        new = caption(text).set_z_index(ON_TOP)
        anims = [FadeIn(new, shift=0.15 * UP)]
        if previous is not None:
            anims.append(FadeOut(previous))
        return new, anims

    def construct(self):
        corner = badge().set_z_index(ON_TOP)
        corner_logo, _ = corner
        # Picks up where the GUI segment ends: the header alone
        self.add(corner)

        # --- One slide, built up row by row ----------------------------------
        open_source = Group(
            labelled(svg_icon("github-brands.svg", ROW_ICON), "GitHub"),
            # The scales read heavier than the GitHub mark at the same height
            labelled(svg_icon("octicon-law-24.svg", 0.8 * ROW_ICON), "BSD-3-Clause"),
        ).arrange(RIGHT, buff=1.5)
        team = Group(
            labelled(
                image("NIU_logo_transparent.png", ROW_ICON), "Neuroinformatics Unit"
            ),
            image("SWC_Logo_4C_Blue.png", 1.1),
        ).arrange(RIGHT, buff=1.5)
        supporters = Group(*[image(name, h) for name, h in SUPPORTERS])
        supporters.arrange(RIGHT, buff=1.0)
        icons_credit = Text(
            "Icons: Font Awesome (CC BY 4.0), Octicons (MIT)",
            font=FONT,
            font_size=16,
            color=LIGHT_GREY,
        ).to_corner(DOWN + RIGHT, buff=0.15)
        rows = [
            (open_source, "Free and open source", [icons_credit]),
            (team, "Developed by a dedicated team of engineers", []),
            (supporters, "Supported by our host institutes and funders", []),
        ]
        cap = None
        for (row, text, extras), y in zip(rows, ROW_CENTRES):
            row.move_to(y * UP)
            cap, anims = self.say(text, cap)
            self.play(*anims, FadeIn(row), *[FadeIn(m) for m in extras], run_time=0.6)
            self.wait(3.0)
        slide = [row for row, _, _ in rows] + [icons_credit]

        # --- The community: rolling credits -----------------------------------
        names = contributors()
        credits = VGroup(
            *[
                credit(name, (i % 3 - 1) * CREDITS_COLUMN, -(i // 3) * CREDITS_ROW)
                for i, name in enumerate(names)
            ]
        )
        # Start just below the window, end with the last row mid-window
        credits.shift((CREDITS_BOTTOM - credits.get_top()[1]) * UP)
        distance = credits.height + (CREDITS_TOP - CREDITS_BOTTOM) / 2
        mask = credits_mask()
        self.add(credits, mask)
        cap, anims = self.say("…and a growing community of contributors", cap)
        self.play(*anims, *[FadeOut(m) for m in slide], run_time=0.6)
        self.play(
            credits.animate.shift(distance * UP),
            run_time=distance / CREDITS_SPEED,
            rate_func=linear,
        )

        # --- Back to the title card: the logo returns to the centre -----------
        # The full-size bitmap, shrunk onto the header logo, so the final frame
        # matches the title card's first frame exactly
        logo = image("movement_logo_on-transparent.png", TITLE_LOGO_HEIGHT)
        logo.move_to(TITLE_LOGO_CENTRE).set_z_index(ON_TOP)
        title = logo.copy()
        logo.scale(corner_logo.height / logo.height).move_to(corner_logo)
        self.remove(corner_logo)
        self.add(logo)
        self.play(
            FadeOut(credits),
            FadeOut(cap),
            logo.animate.scale(title.height / logo.height).move_to(title),
            run_time=1.2,
        )
        # Swap in the untouched copy, free of rounding from the scaling
        self.remove(logo, mask)
        self.add(title)
        self.wait(0.5)

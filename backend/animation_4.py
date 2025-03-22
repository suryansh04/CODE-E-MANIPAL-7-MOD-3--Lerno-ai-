# To run this animation, use the following command:
# manim -pql <filename>.py Scene4
# or for higher quality:
# manim -pqh <filename>.py Scene4
from manim import *

class Scene4(Scene):
    def construct(self):
        # Create axes
        axes = ThreeDAxes(x_range=[-3, 3, 1], y_range=[-3, 3, 1], z_range=[-3, 3, 1])

        # Create vectors
        v = Arrow3D(start=ORIGIN, end=[2, 0, 0], color=RED)
        w = Arrow3D(start=ORIGIN, end=[0, 2, 0], color=BLUE)
        u = Arrow3D(start=ORIGIN, end=[0, 0, 2], color=GREEN)

        # Create parallelepiped
        parallelepiped = Prism(dimensions=[2, 2, 2], fill_opacity=0.2)

        # Create formula
        formula = MathTex(r"|\vec{v} \wedge \vec{w} \wedge \vec{u}| = \text{Volume}", font_size=24)
        formula.to_edge(DOWN)

        # Animation sequence
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
        self.play(Create(axes))
        self.play(GrowArrow(v), GrowArrow(w), GrowArrow(u))
        self.wait(0.5)
        self.play(Create(parallelepiped))
        self.play(Write(formula))
        self.wait(1)

        # Rearrange vectors
        new_w = Arrow3D(start=[2, 0, 0], end=[2, 2, 0], color=BLUE)
        new_formula = MathTex(r"\vec{v} \wedge \vec{w} = -\vec{w} \wedge \vec{v}", font_size=24)
        new_formula.to_edge(DOWN)

        self.play(Transform(w, new_w), Transform(formula, new_formula))
        self.play(parallelepiped.animate.flip())
        self.wait(1)

        # Add title
        title = Text("3-Vector Wedge Product", font_size=24)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)
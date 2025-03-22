# To run this animation, use the following command:
# manim -pql <filename>.py Scene2
# or for higher quality:
# manim -pqh <filename>.py Scene2
from manim import *

class Scene2(Scene):
    def construct(self):
        # Create axes
        axes = Axes(
            x_range=[-1, 6, 1],
            y_range=[-1, 6, 1],
            axis_config={"color": WHITE}
        )

        # Create vectors
        vector_a = Arrow(start=ORIGIN, end=[3, 2, 0], buff=0, color=RED)
        vector_b = Arrow(start=ORIGIN, end=[2, 3, 0], buff=0, color=BLUE)
        vector_b_moved = Arrow(start=[3, 2, 0], end=[5, 5, 0], buff=0, color=BLUE)
        vector_r = Arrow(start=ORIGIN, end=[5, 5, 0], buff=0, color=GREEN)

        # Create labels
        label_a = MathTex(r"\vec{A}", color=RED).next_to(vector_a, UP)
        label_b = MathTex(r"\vec{B}", color=BLUE).next_to(vector_b, LEFT)
        label_r = MathTex(r"\vec{R}", color=GREEN).next_to(vector_r, RIGHT)

        # Create title
        title = Text("Vector Addition: Tip-to-Tail Method", font_size=24).to_edge(DOWN)

        # Animation sequence
        self.play(Create(axes), Write(title))
        self.play(GrowArrow(vector_a), Write(label_a))
        self.play(GrowArrow(vector_b), Write(label_b))
        self.wait(0.5)
        self.play(Transform(vector_b, vector_b_moved))
        self.play(GrowArrow(vector_r), Write(label_r))
        self.wait(1)

        # Description
        description = Text("Resultant vector R = A + B", font_size=20).next_to(title, UP)
        self.play(Write(description))
        self.wait(2)
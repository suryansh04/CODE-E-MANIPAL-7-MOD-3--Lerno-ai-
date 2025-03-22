# To run this animation, use the following command:
# manim -pql <filename>.py Scene1
# or for higher quality:
# manim -pqh <filename>.py Scene1
from manim import *

class Scene1(Scene):
    def construct(self):
        # Create axes
        axes = Axes(
            x_range=[-5, 5, 1],
            y_range=[-5, 5, 1],
            axis_config={"color": BLUE}
        )

        # Create vector
        vector = Arrow(start=ORIGIN, end=[3, 4, 0], buff=0, color=YELLOW)
        vector_label = MathTex(r"\vec{v} = (3,4)").next_to(vector.get_end(), UR, buff=0.1)

        # Create components
        x_component = DashedLine(start=ORIGIN, end=[3, 0, 0], color=RED)
        y_component = DashedLine(start=[3, 0, 0], end=[3, 4, 0], color=GREEN)

        x_label = MathTex("3").next_to(x_component, DOWN)
        y_label = MathTex("4").next_to(y_component, RIGHT)

        # Create title
        title = Text("Introduction to Vector Algebra", font_size=24).to_edge(DOWN)

        # Animation sequence
        self.play(Create(axes))
        self.wait(0.5)
        self.play(GrowArrow(vector), Write(vector_label))
        self.wait(0.5)
        self.play(Create(x_component), Write(x_label))
        self.wait(0.5)
        self.play(Create(y_component), Write(y_label))
        self.wait(0.5)
        self.play(Write(title))
        self.wait(1)
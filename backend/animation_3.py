# To run this animation, use the following command:
# manim -pql <filename>.py Scene3
# or for higher quality:
# manim -pqh <filename>.py Scene3
from manim import *

class Scene3(Scene):
    def construct(self):
        # Create axes
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            axis_config={"color": WHITE}
        )

        # Create vectors
        v1 = Arrow(start=ORIGIN, end=[2, 1, 0], buff=0, color=BLUE)
        v2 = Arrow(start=ORIGIN, end=[1, 2, 0], buff=0, color=RED)

        # Create labels
        v1_label = MathTex(r"\vec{v_1}").next_to(v1.get_end(), RIGHT).scale(0.7)
        v2_label = MathTex(r"\vec{v_2}").next_to(v2.get_end(), UP).scale(0.7)

        # Create parallelogram
        parallelogram = Polygon(
            ORIGIN, v1.get_end(), v1.get_end() + v2.get_end(), v2.get_end(),
            fill_opacity=0.2,
            fill_color=GREEN,
            stroke_width=0
        )

        # Create text for wedge product
        wedge_text = Text("Wedge Product: v₁ ∧ v₂", font_size=24).to_edge(DOWN)

        # Animation sequence
        self.play(Create(axes))
        self.play(GrowArrow(v1), GrowArrow(v2))
        self.play(Write(v1_label), Write(v2_label))
        self.play(Create(parallelogram))
        self.play(Write(wedge_text))
        self.wait(1)

        # Demonstrate v ∧ v = 0
        v3 = Arrow(start=ORIGIN, end=[1.5, 1.5, 0], buff=0, color=PURPLE)
        v3_label = MathTex(r"\vec{v}").next_to(v3.get_end(), UP + RIGHT).scale(0.7)
        zero_text = Text("v ∧ v = 0", font_size=24).to_edge(DOWN)

        self.play(
            FadeOut(v1), FadeOut(v2), FadeOut(v1_label), FadeOut(v2_label),
            FadeOut(parallelogram), FadeOut(wedge_text)
        )
        self.play(GrowArrow(v3), Write(v3_label))
        self.play(Transform(wedge_text, zero_text))
        self.wait(1)
# To run this animation, use the following command:
# manim -pql <filename>.py Scene5
# or for higher quality:
# manim -pqh <filename>.py Scene5
from manim import *

class Scene5(Scene):
    def construct(self):
        # Create split screen
        left_rect = Rectangle(width=6, height=6, color=WHITE)
        right_rect = Rectangle(width=6, height=6, color=WHITE)
        left_rect.shift(LEFT * 3.5)
        right_rect.shift(RIGHT * 3.5)

        # Create 3D cube for left side
        cube = Cube(side_length=2, fill_opacity=0.1)
        cube.shift(LEFT * 3.5)
        face = Square(side_length=2, fill_opacity=0.3, color=YELLOW)
        face.shift(LEFT * 3.5 + OUT)

        # Create surface normal vector
        normal = Arrow(start=[0, 0, 1], end=[0, 0, 2], buff=0, color=GREEN)
        normal.shift(LEFT * 3.5)
        normal_label = Text("Surface Normal", font_size=20).next_to(normal, UP)

        # Create electromagnetic field representation for right side
        e_field = VGroup(*[Arrow(start=[x, -1, 0], end=[x, 1, 0], buff=0, color=RED) for x in [-0.5, 0, 0.5]])
        m_field = VGroup(*[Arrow(start=[-1, y, 0], end=[1, y, 0], buff=0, color=BLUE) for y in [-0.5, 0, 0.5]])
        em_field = VGroup(e_field, m_field)
        em_field.shift(RIGHT * 3.5)

        # Create dividing line and title
        divider = Line(start=[0, -3, 0], end=[0, 3, 0])
        title = Text("Exterior Algebra", font_size=24).to_edge(DOWN)

        # Animation sequence
        self.play(Create(left_rect), Create(right_rect))
        self.play(Create(cube), Create(face))
        self.play(GrowArrow(normal), Write(normal_label))
        self.play(Create(em_field))
        self.play(Create(divider), Write(title))
        
        # Add description
        description = Text("Exterior algebra in graphics and physics", font_size=20)
        description.to_edge(UP)
        self.play(Write(description))
        
        self.wait(2)
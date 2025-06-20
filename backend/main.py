import json
import re
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain_community.utilities import WikipediaAPIWrapper
import subprocess
import firebase_admin
from firebase_admin import credentials, storage
import uuid
load_dotenv()
cred = credentials.Certificate("lerno-cd286-firebase-adminsdk-fbsvc-222d396b1f.json")
firebase_admin.initialize_app(cred, {"storageBucket": "lerno-cd286.firebasestorage.app"})

bucket = storage.bucket()

anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")

if not anthropic_api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables or .env file")

model = ChatAnthropic(
    model_name="claude-3-7-sonnet-20250219",
    anthropic_api_key=anthropic_api_key,
    temperature=0.7,
    max_tokens=4000
)

wikipedia = WikipediaAPIWrapper(top_k_results=2)

use_gemini = False
if google_api_key:
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        gemini_model = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=google_api_key)
        use_gemini = True
    except (ImportError, Exception) as e:
        print(f"Failed to initialize Gemini: {e}")
        print("Will use Claude for classification instead.")

STORYBOARD_PROMPT_TEMPLATE = PromptTemplate(
    input_variables=["audience", "topic", "wikipedia_info"],
    template="""For an audience of a {audience}, generate a series of 5 frames to explain {topic}. Each frame should be a single animation point, such as visualizing squaring a number visually or adding a vector tip to tail. It should not take longer than 15 seconds.
    Also use this wikipedia information to help create the frames {wikipedia_info}, but it is not necessary only for reference.

For example, explaining vector addition would be:
1. Frame showing 2 vectors from the origin explaining that these can be any arbitrary vector.
2. Moving the second vector to the tip of the first vector and draw a resulting vector.
3. Showing vector addition numerically, adding each component numerically.
4. Explain a simple practical example of vector addition, how 2 forces can combine together into a larger force.
5. Example question with answer.

Do not include a frame for a quiz.

Each frame should come with a short description of what it will talk about. This is meant to be the storyboard for an animated video explaining this concept.

Format the frames in the following JSON format:

{{ "frames": 
[
{{
"title": "xxxx",
"description": "xxxx"
}},
{{
"title": "xxxx",
"description": "xxxx"
}},
{{
"title": "xxxx",
"description": "xxxx"
}},
{{
"title": "xxxx",
"description": "xxxx"
}},
{{
"title": "xxxx",
"description": "xxxx"
}}
]
}}

Ensure that the JSON is valid.

The title should be short, limit of 5 words.
The description should be a few sentences, enough for someone to understand what to do and how to animate and explain this frame.

Output only the plaintext JSON format of the frames. DO NOT OUTPUT MARKDOWN. DO NOT INCLUDE A PREAMBLE OR POSTAMBLE."""
)

SCENE_AGENT_PROMPT_TEMPLATE = PromptTemplate(
    input_variables=["frame"],
    template="""Given the following, generate a script and animation description in the style of 3Blue1Brown.

{frame}

The script will be read orally to the student. This should not take longer than 10-15 seconds.
The animation description should be descriptive of what should be shown on the screen along with relevant positional information. (e.g., The number line should be centered vertically on the screen with a range of -10 to 10 with ticks for every 0.2, there is a blue arrow above the number line pointing from 0 to +5. The arrow will then shrink until it points to +2.)

IMPORTANT: Do NOT include ANY REFERENCE to 'scale_tips' parameter in the animation description, as this parameter is not supported in Manim CE 0.19.0.

In addition, generate a 4-choice multiple-choice question and a free-response question that can be asked at the end of the video.

Instead of always putting the correct answer first in the multiple-choice array, randomly place it at any position, and then specify which index (0, 1, 2, or 3) contains the correct answer in the "correct-index" field.

The answer for the free response should be a string.

Return the data in the following format:

{{
"narration": "string",
"animation-description": "string",
"free-response-question": "string",
"free-response-answer": "string",
"multiple-choice-question": "string",
"multiple-choice-choices": ["choice1 - string", "choice2 - string", "choice3 - string", "choice4 - string"],
"correct-index": integer (0-3)
}}

THE RESPONSE SHOULD ONLY BE A VALID PLAINTEXT JSON FORMAT. DO NOT OUTPUT MARKDOWN. DO NOT INCLUDE A PREAMBLE OR POSTAMBLE."""
)

EXAMPLE_CODE = r'''
from manim import *

class IntroductionToVector(Scene):
    def construct(self):
        axes = Axes(
            x_range=[-5, 5, 1], y_range=[-3, 3, 1],
            axis_config={"color": BLUE}
        )
        
        vector = Arrow(ORIGIN, [2, 1, 0], buff=0, color=YELLOW)
        vector_label = MathTex(r"\vec{{v}} = (2,1)").next_to(vector, UP)
        
        x_component = DashedLine(start=ORIGIN, end=[2, 0, 0], color=RED)
        y_component = DashedLine(start=[2, 0, 0], end=[2, 1, 0], color=GREEN)
        
        x_label = MathTex("2").next_to(x_component, DOWN)
        y_label = MathTex("1").next_to(y_component, RIGHT)
        
        self.play(Create(axes))
        self.play(GrowArrow(vector), Write(vector_label))
        self.play(Create(x_component), Write(x_label))
        self.play(Create(y_component), Write(y_label))
        
        self.wait(2)
        
        vector2 = Arrow([2, 1, 0], [4, 3, 0], buff=0, color=ORANGE)
        vector2_label = MathTex(r"\vec{{w}} = (2,2)").next_to(vector2, UP)
        
        result_vector = Arrow(ORIGIN, [4, 3, 0], buff=0, color=PURPLE)
        result_label = MathTex(r"\vec{{v}} + \vec{{w}} = (4,3)").next_to(result_vector, UP)
        
        self.play(GrowArrow(vector2), Write(vector2_label))
        self.wait(1)
        self.play(GrowArrow(result_vector), Write(result_label))
        
        self.wait(2)
'''

def generate_response(prompt):
    """Extract JSON from Claude's response"""
    message = model.invoke(prompt)
    text = message.content
    json_match = re.search(r"\{.*\}", text, re.DOTALL)
    if json_match:
        return json_match.group(0)
    else:
        return ""

def generate_response_raw(prompt):
    """Get raw text response from Claude"""
    message = model.invoke(prompt)
    return message.content.strip()

def classify_input(user_input):
    """Classifies user input into topic and audience using Gemini if available, otherwise uses Claude."""
    if use_gemini:
        try:
            prompt = f"""Classify the following input into a topic and audience. If no audience is provided, default to college student.
            Return the response as a JSON object with "topic" and "audience" as keys.

            Input: {user_input}
            Output:
            """
            response = gemini_model.invoke(prompt)
            result = json.loads(response.content)
            return result
        except Exception as e:
            print(f"Error using Gemini for classification: {e}")
    
    prompt = f"""Classify the following input into a topic to explain and an audience level. If no audience level is explicitly mentioned, default to "college student".

    Input: "{user_input}"

    Return ONLY a JSON object with "topic" and "audience" as keys. For example:
    {{
        "topic": "quantum physics",
        "audience": "high school students"
    }}
    """
    
    try:
        response = model.invoke(prompt)
        text = response.content
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(0))
            return result
        else:
            return {"topic": user_input, "audience": "college student"}
    except Exception as e:
        print(f"Error classifying input: {e}")
        return {"topic": user_input, "audience": "college student"}

def create_storyboard(audience, topic):
    """Generate a storyboard of frames to explain the topic"""
    wikipedia_info = wikipedia.run(topic)
    prompt = STORYBOARD_PROMPT_TEMPLATE.format(audience=audience, topic=topic, wikipedia_info=wikipedia_info)
    storyboard_json = generate_response(prompt)
    try:
        return json.loads(storyboard_json)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Received JSON: {storyboard_json}")
        return None

def generate_scene(frame):
    """Generate a scene description from a frame"""
    prompt = SCENE_AGENT_PROMPT_TEMPLATE.format(frame=frame)
    scene_json = generate_response(prompt)
    try:
        return json.loads(scene_json)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Received JSON: {scene_json}")
        return None

def generate_animation_code(narration, animation_description, title, scene_number=None):
    """Generate Manim animation code for a scene"""
    if scene_number:
        scene_class_name = f"Scene{scene_number}"
    else:
        scene_class_name = ''.join(c for c in title if c.isalnum())
        if not scene_class_name:
            scene_class_name = "AnimationScene"
    
    prompt = """
0. Make the animation as simple as possible and just use the basic Manim functions.
1.Instead of "outer_radius" use "radius" 
2. Given the scene description and title, write COMPLETE, READY-TO-RUN Manim code for this scene in 3Blue1Brown style. This scene should be between 5 and 10 seconds and contain a short text blurb describing the scene.
3. USE EXCLUSIVELY MANIM COMMUNITY EDITION (ManimCE) VERSION 0.19.0 SYNTAX.
4. Always include this import statement at the top: from manim import *
5. Define a complete Manim Scene class. The name of the class should be "{0}" (NOT "Scene" as this would shadow the base Scene class).
6. DO NOT USE ANY CLASSES OR FUNCTIONS THAT DON'T EXIST IN MANIM CE 0.19.0. Specifically:
   - DO NOT use ThoughtBubble (not built-in) - use Text, MathTex, SurroundingRectangle, or Circle instead
   - DO NOT use deprecated methods like add_tip() or parameters like scale_tips
   - DO NOT create constructor conflicts (e.g., avoid multiple values for parameters like 'outer_radius' in AnnularSector)
   - DO NOT use Brace.get_text() (deprecated) - use Tex or MathTex and position manually
   - DO NOT use custom functions without defining them
7. For arrows/vectors, ALWAYS use: Arrow(start=ORIGIN, end=[x,y,0], buff=0, color=YELLOW)
8. For axes, use: axes = Axes(x_range=[-5, 5, 1], y_range=[-3, 3, 1]) format.
9. For text, use Text() or MathTex() for math equations. Ensure that font_size is small (< 24pt).
10. Use these standard animations: Create(), Write(), FadeIn(), FadeOut(), Transform(), GrowArrow(), etc.
11. Always use the explicit coordinate system [x, y, 0] for 2D points (Manim works in 3D space).
12. Every scene must have animations using self.play() followed by self.wait() commands.
13. Ensure any text, diagrams, or formulas fit fully on the screen.
14. Use default Manim colors: RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE, WHITE.
15. ALWAYS USE 2-AXIS DIAGRAMS for mathematical concepts.
16. DO NOT CREATE PARAMETERS THAT DON'T EXIST for Manim objects.
17. Text should be concise and to the point, no more than 10 words.
18. If the description is vague, create a scene that is related to the title.
19. Every scene must have an animation. Also if you add topic name/headline, ALWAYS ADD IT TO THE BOTTOM OF THE ANIMATION.
20. There should be just manim code with the necessary import and class definition, no other comment or text.
21. IF YOU NEED A THOUGHT BUBBLE, create one using Circle and Polygon objects, DO NOT use any ThoughtBubble class.
22. For AnnularSector, use only the parameters that exist in version 0.19.0, and avoid duplicate parameters.
23. NEVER USE THE PARAMETER 'scale_tips' - IT DOES NOT EXIST IN MANIM CE 0.19.0
24.DON'T DO THIS "```python" IN THE CODE BLOCK, JUST WRITE THE MANIM CODE.
Here is an example of valid Manim CE 0.19.0 code:

from manim import *

class VectorExample(Scene):
    def construct(self):
        # Create axes
        axes = Axes(
            x_range=[-5, 5, 1], 
            y_range=[-3, 3, 1],
            axis_config={{"color": BLUE}}
        )
        
        # Create a vector as an arrow
        vector = Arrow(start=ORIGIN, end=[2, 1, 0], buff=0, color=YELLOW)
        vector_label = MathTex(r"\\vec{{v}} = (2,1)").next_to(vector, UP)
        
        # Create components
        x_component = DashedLine(start=ORIGIN, end=[2, 0, 0], color=RED)
        y_component = DashedLine(start=[2, 0, 0], end=[2, 1, 0], color=GREEN)
        
        x_label = MathTex("2").next_to(x_component, DOWN)
        y_label = MathTex("1").next_to(y_component, RIGHT)
        
        # Animation sequence
        self.play(Create(axes))
        self.wait(0.5)
        self.play(GrowArrow(vector), Write(vector_label))
        self.wait(0.5)
        self.play(Create(x_component), Write(x_label))
        self.wait(0.5)
        self.play(Create(y_component), Write(y_label))
        self.wait(1)

Narration: 
{1}

Animation Description:
{2}

Title:
{3}

ONLY RETURN THE COMPLETE MANIM CODE FOR THE SCENE. DO NOT INCLUDE A PREAMBLE OR POSTAMBLE.
""".format(scene_class_name, narration, animation_description, title) 
    
    response = generate_response_raw(prompt)
    if not response:
        response = f"""from manim import *
class {scene_class_name}(Scene):
    def construct(self):
        text = Text("No animation generated", font_size=48)
        self.play(Write(text))
        self.wait(1)
        """

    response = response.replace("scale_tips=True", "")
    response = response.replace("scale_tips=False", "")
    response = response.replace("scale_tips = True", "")
    response = response.replace("scale_tips = False", "")
    response = response.replace(", scale_tips", "")
    response = response.replace(",scale_tips", "")

    run_instructions = """# To run this animation, use the following command:
# manim -pql <filename>.py {0}
# or for higher quality:
# manim -pqh <filename>.py {0}
""".format(scene_class_name)

    return run_instructions + response

def generate_educational_content(user_input):
    """Generate complete educational content from a user input"""
    classification = classify_input(user_input)
    audience = classification.get("audience", "college student")
    topic = classification.get("topic", user_input)
    
    storyboard = create_storyboard(audience, topic)
    result = {
        "metadata": {
            "topic": topic,
            "audience": audience
        },
        "success": False,
        "scenes": []
    }
    
    if storyboard and "frames" in storyboard:
        result["success"] = True
        
        for i, frame in enumerate(storyboard["frames"]):
            if i >= 5:
                break
            
            scene_number = i + 1
            scene_data = {
                "scene_number": scene_number,
                "title": frame["title"],
                "description": frame["description"]
            }
            
            scene = generate_scene(frame["description"])
            if scene:
                if "narration" in scene:
                    scene_data["narration"] = scene["narration"]
                if "animation-description" in scene:
                    scene_data["animation_description"] = scene["animation-description"]
                
                scene_data["assessment"] = {
                    "multiple_choice": {
                        "question": scene.get("multiple-choice-question", ""),
                        "choices": scene.get("multiple-choice-choices", []),
                        "correct_index": scene.get("correct-index", 0)
                    },
                    "free_response": {
                        "question": scene.get("free-response-question", ""),
                        "answer": scene.get("free-response-answer", "")
                    }
                }
                
                scene_data["manim_code"] = generate_animation_code(
                    scene.get("narration", ""), 
                    scene.get("animation-description", ""), 
                    frame["title"],
                    scene_number
                )
            
            result["scenes"].append(scene_data)
    
    return result

app = FastAPI()

class prompt(BaseModel):
    prompt:str

@app.post("/process-data")
async def index(item:prompt):
    """API endpoint to generate educational content"""
    try:
        # Generate educational content from the prompt
        result = generate_educational_content(item.prompt)
        video_urls=[]
        for scene in result.get("scenes", []):
            manim_code = scene.get("manim_code", "No Manim code generated")
            scene_number = scene.get("scene_number",1)
            animation_file = f"animation_{scene_number}.py"
            with open(animation_file, "w", encoding="utf-8") as f:
                f.write(manim_code)
            print(f"Wrote file: {animation_file}")

            print(f"Starting Manim rendering for Scene{scene_number}...")
            process = subprocess.run(
                ["manim", "-pql", "--progress_bar", "none", animation_file, f"Scene{scene_number}"],
                capture_output=True,
                text=True,
                check=False 
            )
            
            mp4_path= f"media/videos/animation_{scene_number}/480p15/Scene{scene_number}.mp4"

            if os.path.exists(mp4_path):
                file_name = f"{uuid.uuid4()}_Scene{scene_number}.mp4"
                blob = bucket.blob(file_name)
                blob.upload_from_filename(mp4_path, content_type="video/mp4")
                blob.make_public()
                video_urls.append(blob.public_url)
                print(f"Successfully uploaded {mp4_path} to Firebase")
            else:
                print(f"Rendered video not found at {mp4_path}")

        return {
            "status": "success",
            "data": result,
            "video_urls": video_urls,
            "message": "Educational content generated successfully"
        }
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR: {str(e)}")
        print(f"TRACEBACK: {error_details}")
        
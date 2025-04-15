# custom_tool.py
import os
# import google.generativeai as genai,Content, Part

from google import genai
from google.genai import types
from PIL import Image
import json
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from IPython.display import display, Markdown

load_dotenv()  # Load environment variables from .env file

class GeminiFeedbackExtractionInput(BaseModel):
    """Input schema for GeminiFeedbackExtractionTool."""

    image_path: str = Field(..., description="Path to the image file containing the feedback form.")
    prompt: str = Field(..., description="A prompt to guide the LLM in extracting the information in JSON format.")


class GeminiFeedbackExtractionTool(BaseTool):
    """Tool that uses the Gemini API to extract feedback data from an image."""

    name: str = "gemini_feedback_extraction"
    description: str = (
        "Extracts structured feedback data from an image using the Gemini API. "
        "The image should be a feedback form, and the prompt should guide the extraction process. "
        "The output will be a JSON string containing the extracted feedback data."
    )
    args_schema: Type[BaseModel] = GeminiFeedbackExtractionInput

    def _run(self, image_path: str, prompt="extract the feedback data from uploaded image") -> str:
        """Extracts feedback from an image using the Gemini API."""
        try:
            # Configure the Gemini API
            client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
            # genai.configure(api_key=os.environ["GEMINI_API_KEY"])
            model_name = os.getenv("LLM_MODEL", "gemini-2.0-flash")  # Get model name from .env
            model = genai.GenerativeModel(model_name)

            # Load the image using Pillow
            img = Image.open(image_path)

            # # Send the image and prompt to the Gemini API
            # response = model.generate_content(contents= [img])
            
            response = client.models.generate_content(
                model=model_name,
                contents=[
                    img,
                    prompt
                ]
            )


            # Extract the JSON data from the response
            json_string = response.text.strip()

            # Check if the response contains valid JSON
            try:
                data = json.loads(json_string)
                return json_string
            except json.JSONDecodeError:
                return f"Error: Invalid JSON response from Gemini API: {json_string}"

        except Exception as e:
            return f"Error: Could not extract feedback using Gemini API: {e}"
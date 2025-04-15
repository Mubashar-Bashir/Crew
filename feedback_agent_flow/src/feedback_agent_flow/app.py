# import datetime
# import os
# import chainlit as cl
# from pathlib import Path
# import shutil
# import traceback
# import asyncio
# from feedback_agent_flow.main1 import kickoff
# from dotenv import load_dotenv, find_dotenv

# # Load environment variables from .env file
# load_dotenv(find_dotenv())

# # Access the API key from the environment
# api_key = os.getenv("GEMINI_API_KEY")

# if not api_key:
#     raise ValueError("GEMINI_API_KEY is not set in the environment or .env file")

# os.environ["GEMINI_API_KEY"] = api_key  # Set the key explicitly for the library

# # Define the base directory and ensure the upload directory exists
# BASE_DIR = Path(__file__).parent
# UPLOAD_DIR = BASE_DIR / "uploads"
# FILES_DIR = BASE_DIR / ".files"  # Chainlit's default temp directory

# # Ensure both directories exist
# UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
# FILES_DIR.mkdir(parents=True, exist_ok=True)


# def get_latest_uploaded_file():
#     """Fetch the latest file from the uploads directory."""
#     files = list(UPLOAD_DIR.glob("*"))

#     if not files:
#         print("⚠️ No uploaded files found.")
#         return None

#     latest_file = max(files, key=os.path.getmtime)
#     return str(latest_file)


# @cl.on_chat_start
# async def on_chat_start():
#     await cl.Message("🚀 **WELCOME TO AI-HUB FEEDBACK IMAGE AGENT**\nUpload an image for processing.").send()

#     files = None
#     while files is None:
#         files = await cl.AskFileMessage(
#             content="📂 Please upload a file (CSV, PDF, or JPG).",
#             accept=["text/csv", "application/pdf", "image/jpeg"],
#             max_size_mb=20,
#             timeout=180,
#         ).send()

#     file = files[0]
#     file_path = UPLOAD_DIR / file.name

#     # Check if the file already exists
#     if file_path.exists():
#         # Add a timestamp to the filename to avoid collisions
#         timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
#         # Assuming `file` is the AskFileResponse object
#         new_file_name = f"{os.path.splitext(file.name)[0]}_{timestamp}{os.path.splitext(file.name)[1]}"        
#         file_path = UPLOAD_DIR / new_file_name

#     try:
#         shutil.move(file.path, file_path)
#         await cl.Message(f"✅ File `{file.name}` uploaded successfully!").send()
#     except Exception as e:
#         await cl.Message(f"❌ Error moving file: {str(e)}").send()
#         return  # Exit if file move fails

#     # ✅ Show a button inside a message
#     actions = [
#         cl.Action(
#             name="extract_feedback",
#             icon="file-text",
#             payload={},
#             label="🚀 Process Feedback"
#         )
#     ]

#     await cl.Message(content="Click the button to process the feedback:", actions=actions).send()


# @cl.action_callback("extract_feedback")
# async def process_feedback(action: cl.Action):
#     """Handles button click and triggers feedback extraction."""
#     try:
#         # Run kickoff() in a separate thread to avoid blocking the event loop
#         result = await asyncio.to_thread(kickoff)
#         await cl.Message(result).send()
#     except Exception as e:
#         traceback_str = traceback.format_exc()
#         await cl.Message(f"❌ Error processing feedback: {str(e)}\n{traceback_str}").send()
import os
import datetime
import chainlit as cl
from pathlib import Path
import traceback
from feedback_agent_flow.main1 import kickoff  # Ensure this function extracts JSON from an image/PDF
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

# Set API Key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY is missing! Set it in .env file.")
os.environ["GEMINI_API_KEY"] = api_key

# Define Upload Directory
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # Ensure folder exists

@cl.on_chat_start
async def on_chat_start():
    """Start chat session & prompt user to upload a file."""
    await cl.Message("🚀 **Welcome! Upload a Feedback Form (Image/PDF) for Processing.**").send()

    file_msg = await cl.AskFileMessage(
        content="📂 Upload a file (JPG, PNG, or PDF):",
        accept=["image/jpeg", "image/png", "application/pdf"],
        max_size_mb=20,
        timeout=180,
    ).send()

    if not file_msg:
        await cl.Message("⚠️ No file uploaded. Try again!").send()
        return

    # Save file with a timestamp to prevent conflicts
    file = file_msg[0]
    file_ext = Path(file.name).suffix.lower()
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    file_path = UPLOAD_DIR / f"{Path(file.name).stem}_{timestamp}{file_ext}"

    try:
        Path(file.path).rename(file_path)
        cl.user_session.set("current_file", str(file_path))  # ✅ Store file path in user session
        await cl.Message(f"✅ File `{file.name}` uploaded successfully!").send()

        # ✅ Use action_callback correctly
        actions = [
            cl.Action(
                name="extract_feedback",
                icon="document-text",
                payload={"file_path": str(file_path)},
                label="🚀 Process Feedback"
            )
        ]

        await cl.Message(content="Click the button to extract feedback:", actions=actions).send()

    except Exception as e:
        await cl.Message(f"❌ Error uploading file: {str(e)}").send()

@cl.action_callback("extract_feedback")
async def process_feedback(action: cl.Action):
    """Triggered when user clicks 'Process Feedback' button."""
    file_path = action.payload.get("file_path")  # ✅ Retrieve file path

    if not file_path or not Path(file_path).exists():
        await cl.Message("❌ No file found. Please upload a file first.").send()
        return

    try:
        print(f"📥 Debug - Received file_path: {file_path}")  # ✅ Debugging
        print(f"🔄 Processing file: {file_path}")

        # ✅ Pass file_path as an argument to FeedbackCrew
        response = kickoff(file_path)

        await cl.Message(content=f"✅ Feedback extracted successfully!\n\n```json\n{response}\n```").send()

    except Exception as e:
        await cl.Message(f"❌ Error processing feedback:\n```{traceback.format_exc()}```").send()


if __name__ == "__main__":
    cl.run()

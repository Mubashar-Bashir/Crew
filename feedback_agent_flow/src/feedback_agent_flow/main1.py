#!/usr/bin/env python
# from pydantic import BaseModel, EmailStr, Field, ValidationError
# from typing import Optional
# import os
# import chainlit as cl
# from pathlib import Path
# from feedback_agent_flow.crews.feedback_crew.feedback_crew import FeedbackCrew
# # from crewai.flow.flow import Flow, listen, start
# import json  # Ensure json is imported



# class FeedbackFormState(BaseModel):
#     # Personal Information
#     full_name: str = Field(..., description="Full name of the attendee")  # Required
#     email: str = Field(..., description="Email address of the attendee")  # Required
#     phone_number: str = Field(..., description="Phone number of the attendee")  # Required
#     city: Optional[str] = None  # Example: "Lahore" (Optional)
#     education_level: Optional[str] = None  # Example: "Bachelor's", "Master's", "PhD" (Optional)
#     field_of_study: Optional[str] = None  # Example: "Computer Science" (Optional)
#     institute_name: Optional[str] = None  # Example: "Punjab University" (Optional)

#     # Seminar Feedback
#     seminar_attended: bool  # True if attended, False otherwise
#     seminar_rating: Optional[int] = None  # Example: 1 - 5 (Optional)
#     speaker_feedback: Optional[str] = None  # Example: "Very informative session" (Optional)
#     interest_in_course: bool  # True if interested in enrolling
#     preferred_course: Optional[str] = None  # Example: "AI & Machine Learning" (Optional)

#     # Admission & Preferences
#     admission_plans: Optional[str] = None  # Example: "Immediate", "Next Semester" (Optional)
#     financial_assistance_needed: Optional[bool] = None  # True if aid is needed (Optional)
#     preferred_batch_timing: Optional[str] = None  # Example: "Morning", "Evening" (Optional)
#     referral_source: Optional[str] = None  # Example: "Facebook", "Friend" (Optional)

#     # Additional Feedback
#     expectations_from_course: Optional[str] = None  # Example: "Hands-on AI projects" (Optional)
#     additional_comments: Optional[str] = None  # Example: "Great initiative by AI-HUB" (Optional)

# class FeedbackFormState(BaseModel):
#     full_name: Optional[str] = Field(None, description="User's full name")
#     email: Optional[str] = Field(None, description="User's email address")
#     phone_number: Optional[str] = Field(None, description="User's phone number")
#     seminar_attended: Optional[str] = Field(None, description="Seminar attended by user")
#     interest_in_course: Optional[str] = Field(None, description="Course of interest")
    
# class FeedbackFlow(Flow[FeedbackFormState]):
#     @start()
#     def receive_input(self, input_file):  # Take image/PDF as input
#         print(f"Receiving feedback form: {input_file} ...")

#         # Step 1: Pass file to FeedbackCrew for processing
#         result = (
#             FeedbackCrew()
#             .crew()
#             .kickoff(inputs={"input_file": input_file})  # Process Image/PDF
#         )

#         # Step 2: Extracted Data from agent result
#         extracted_data = result.raw  # Assume raw data is a dictionary
#         # 🚨 Debugging: Print the raw extracted data
#         print(f"🛠️ Debugging - Raw extracted_data: {extracted_data}")
        
#          # 🛑 Check if extracted_data is empty
#         if not extracted_data or extracted_data.strip() == "":
#             print("❌ Error: Received empty JSON response from OCR or Extraction Process.")
#             return  # Stop execution to avoid crashing

#         # ✅ Ensure extracted_data is a dictionary
#         try:
#             extracted_data = json.loads(extracted_data)  # Convert JSON string to dict
#         except json.JSONDecodeError as e:
#             print(f"❌ JSON Decode Error: {e}")
#             return  # Stop execution if JSON is invalid

#         # 🚨 If it's still not a dictionary, raise an error
#         if not isinstance(extracted_data, dict):
#             raise TypeError(f"❌ Invalid extracted_data type: {type(extracted_data)}. Expected dict.")


#         # Fix mapping of names if necessary
#         full_name = extracted_data.get("name", None)  # Use "name" instead of "full_name"
#         email = extracted_data.get("email", None)
#         phone_number = extracted_data.get("phone_number", None)

#         # Initialize state with extracted values (use None if missing)
#         self.state = FeedbackFormState(
#             full_name=full_name,
#             email=email,
#             phone_number=phone_number,
#             seminar_attended=extracted_data.get("seminar_attended", None),
#             interest_in_course=extracted_data.get("interest_in_course", None)
#         )

#         # Check for missing values
#         missing_fields = [field for field, value in self.state.model_dump().items() if value is None]

#         if missing_fields:
#             print(f"⚠️ Missing fields detected: {missing_fields}")
#             request_missing_info(missing_fields)  # Ask the user via Chainlit



#         # Step 3: Store extracted values into state
#         self.state = FeedbackFormState.model_validate(extracted_data)

#         print("✅ Feedback successfully extracted & stored in state!")
    
#     @listen(receive_input)
#     def save_feedback(self):
#         print(f"""Saving extracted feedback...{self.state.full_name}""")
#         with open("feedback_data.json", "w") as f:
#             f.write(self.state.model_dump_json(indent=4))

# async def request_missing_info(missing_fields):
#     """
#     Asks the user for missing parameters via Chainlit.
#     """
#     for field in missing_fields:
#         user_input = await cl.AskUserMessage(
#             content=f"📝 Missing `{field}`. Please enter the value:",
#             timeout=60
#         ).send()

#         # Update the state with user-provided values
#         setattr(FeedbackFlow.state, field, user_input["value"] if user_input else None)

#     print(f"✅ Updated state with user input: {FeedbackFlow.state}")

#     # @listen(receive_input)
#     # def extract_feedback(self):
#     #     print("Extracting data from the form...")
#     #     result = (
#     #         FeedbackCrew()
#     #         .crew()
#     #         .kickoff(inputs={"input_file": "form.pdf"})  # Pass the actual file
#     #     )

#     #     print("Extracted Feedback Data:", result.raw)
#     #     self.state = FeedbackFormState.model_validate(result.raw)  # Validate with Pydantic

    


# # def kickoff(input_file: str):
# #     """Runs the FeedbackFlow process with the uploaded image."""
# #     file_path = os.path.abspath(input_file)  # Ensure absolute path

# #     feedback_flow = FeedbackFlow()  # Initialize FeedbackFlow
# #     result = feedback_flow.kickoff(inputs={"input_file": file_path})  # Pass image

# #     return result

# def get_latest_uploaded_file():
#     """Fetch the latest file from the uploads directory."""
#     upload_dir = Path(__file__).parent / "uploads"
#     files = list(upload_dir.glob("*"))  # Get all files

#     if not files:
#         print("⚠️ No uploaded files found.")
#         return None

#     latest_file = max(files, key=os.path.getmtime)  # Get the newest file
#     return str(latest_file)

# def kickoff():
#     """Run feedback extraction manually via button."""
#     latest_file = get_latest_uploaded_file()
    
#     if latest_file:
#         feedback_flow = FeedbackFlow()
#         feedback_flow.receive_input(latest_file)  # Pass the latest uploaded file
#         return f"✅ Processing completed for `{latest_file}`."
#     else:
#         return "⚠️ No uploaded file found. Please upload one."

# def plot():
#     feedback_flow = FeedbackFormState()
#     feedback_flow.plot()


# # if __name__ == "__main__":
# #     kickoff(input_file:str)
#!/usr/bin/env python
# from typing import Optional
# import os
# import json
# import re
# import asyncio
# from pathlib import Path
# from feedback_agent_flow.crews.feedback_crew.feedback_crew import FeedbackCrew
# from crewai.flow.flow import Flow, listen, start
# from pydantic import BaseModel, Field, ValidationError

# # ✅ Flexible Schema (Allows Missing Fields)
# class RespondentInformation(BaseModel):
#     name: Optional[str] = ""
#     institution_name: Optional[str] = ""
#     contact_number: Optional[str] = None
#     designation: Optional[str] = None

#     class Config:
#         extra = "allow"  # Allows unexpected fields

# class ContentFeedback(BaseModel):
#     relevance: Optional[str] = ""
#     clarity: Optional[str] = ""

#     class Config:
#         extra = "allow"

# class DeliveryFeedback(BaseModel):
#     presenter_engagement: Optional[str] = ""
#     communication_effectiveness: Optional[str] = ""

#     class Config:
#         extra = "allow"

# class OverallFeedback(BaseModel):
#     rating: Optional[str] = ""
#     suggestions: Optional[str] = ""

#     class Config:
#         extra = "allow"

# class FutureInterests(BaseModel):
#     interest_in_more_sessions: Optional[bool] = False
#     preferred_topics: Optional[str] = ""

#     class Config:
#         extra = "allow"

# # ✅ Unified Schema with Flexible Handling
# class FeedbackFormState(BaseModel):
#     form_type: str = "Feedback Form for Presentation"
#     respondent_information: Optional[RespondentInformation] = RespondentInformation()
#     content_feedback: Optional[ContentFeedback] = ContentFeedback()
#     delivery_feedback: Optional[DeliveryFeedback] = DeliveryFeedback()
#     overall_feedback: Optional[OverallFeedback] = OverallFeedback()
#     future_interests: Optional[FutureInterests] = FutureInterests()
#     additional_notes: Optional[str] = ""

#     class Config:
#         extra = "allow"

# # ✅ Feedback Extraction Flow
# class FeedbackFlow(Flow[FeedbackFormState]):
#     def __init__(self):
#         super().__init__(initial_state=FeedbackFormState())

#     @start()
#     async def receive_input(self, input_file: str):
#         """Processes the uploaded feedback image and extracts structured data."""
#         print(f"🚀 Processing feedback form: {input_file} ...")

#         try:
#             print(f"📂 Sending file to FeedbackCrew: {input_file}")
#             result = FeedbackCrew().crew().kickoff(file_path=input_file)

#             if not hasattr(result, "raw") or not result.raw.strip():
#                 print("❌ Error: Empty response from OCR/Extraction process.")
#                 return "Error: Empty JSON response."

#             # Extract JSON from markdown
#             json_match = re.search(r'```json\s*(.*?)\s*```', result.raw, re.DOTALL)
#             json_str = json_match.group(1) if json_match else result.raw

#             # ✅ Safe JSON Parsing (Handles Missing Fields)
#             extracted_dict = json.loads(json_str)
#             validated_data = FeedbackFormState(**extracted_dict)  # Flexible parsing

#             print("✅ Feedback successfully extracted & stored!")
#             return validated_data.model_dump()

#         except (json.JSONDecodeError, ValidationError) as e:
#             print(f"⚠️ Flexible Handling: Invalid JSON format or missing fields ({e})")
#             return {}

#         except Exception as e:
#             print(f"❌ Unexpected Error: {e}")
#             return {}

#     @listen(receive_input)
#     def save_feedback(self):
#         """Saves extracted feedback to a JSON file."""
#         if not self.state:
#             print("⚠️ No feedback data to save.")
#             return

#         try:
#             with open("feedback_data.json", "w") as f:
#                 json.dump(self.state.model_dump(), f, indent=4)
#             print("✅ Feedback saved successfully!")
#         except Exception as e:
#             print(f"❌ Error saving feedback: {e}")
import os
import json
from pathlib import Path
from feedback_agent_flow.crews.feedback_crew.feedback_crew import FeedbackCrew

def kickoff(file_path):
    """
    Initialize the FeedbackCrew with the given file path and run the processing.

    Args:
        file_path (str): Path to the input file (image/PDF).

    Returns:
        json: Result of the feedback processing.
    """
    print("input file for kickoff  >>> ",file_path)
    feedback_crew = FeedbackCrew(input_file=file_path)  
    print("FeedbackCrew initialized:", feedback_crew)  # Debugging statement
    result = feedback_crew.run()  # Process the file and get the result
    print('Result of Kickoff>>>>>', result)
    # if feedback_crew is None:
    #     print("FeedbackCrew is None")
    #     return None
    # result = feedback_crew.run()  # Process the file and get the result
    # print('Result of Kickoff>>>>>', result)
     # Convert any sets to lists
    # if isinstance(result, dict):
    #     for key, value in result.items():
    #         if isinstance(value, set):
    #             result[key] = list(value)
    return result

def get_latest_uploaded_file():
    """
    Retrieve the latest uploaded file from the uploads directory.
    
    Returns:
        str: The path to the most recently uploaded file, or None if no files are found.
    """
    upload_dir = Path(__file__).parent / "uploads"
    files = list(upload_dir.glob("*"))
    
    if not files:
        print("⚠️ No uploaded files found.")
        return None

    latest_file = max(files, key=os.path.getmtime)
    print(f"✅ Latest file found: >>>>> \n {latest_file}")
    return str(latest_file)

if __name__ == "__main__":
    # Fetch the latest uploaded file
    #file path
    upload_dir = Path(__file__).parent / "uploads"
    files = list(upload_dir.glob("*"))
    
    if not files:
        print("⚠️ No uploaded files found.")
    

    latest_file = max(files, key=os.path.getmtime)
    print(f"✅ Latest file found: >>>>> \n {latest_file}")

    # file_path = "src/feedback_agent_flow/uploads/test_image.jpeg"
    # latest_file = get_latest_uploaded_file(file_path)
    print(latest_file)
    if latest_file:
        # Process the latest file if present
        result = kickoff(latest_file)
        print(result)
        # print(f"✅ Processing completed. Result:{json.dumps(result.text, indent=4)}")
    else:
        print("⚠️ No files to process.")
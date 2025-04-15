# feedback_crew.py
import os
import yaml
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from PIL import Image
import google.generativeai as genai
from feedback_agent_flow.tools.custom_tool import GeminiFeedbackExtractionTool # Import Gemini API

@CrewBase
class FeedbackCrew():
    """Feedback processing crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self, input_file):
        self.input_file = input_file
        self.agents = []  # Initialize agents list
        self.tasks = []  # Initialize tasks list

        # Load configurations from YAML files
        base_path = os.path.dirname(os.path.abspath(__file__))
        agents_yaml_path = os.path.join(base_path, self.agents_config)
        tasks_yaml_path = os.path.join(base_path, self.tasks_config)

        # with open(agents_yaml_path, "r") as f:
        #     self.agents_config = yaml.safe_load(f)

        # with open(tasks_yaml_path, "r") as f:
        #     self.tasks_config = yaml.safe_load(f)

        # Print the paths for debugging
        print(f"Debug: agents_yaml_path = {agents_yaml_path}")
        print(f"Debug: tasks_yaml_path = {tasks_yaml_path}")

        print(f"Debug: Agents config: {self.agents_config}")
        print(f"Debug: Tasks config: {self.tasks_config}")
        print(f"Debug: Input file: {self.input_file}")

    def feedback_extractor_function(self) -> Agent:
        # gemini_tool = GeminiFeedbackExtractionTool()  # Create instance here
        config = self.agents_config["feedback_extractor"]
        # config["tools"] = [gemini_tool]  # Add the tool
        return Agent(
            **config,
            allow_delegation=False,
            verbose=True,
            # tools=[gemini_tool]
            input_file=self.input_file  # Pass input_file if the agent needs it
        )

    @agent
    def feedback_extractor(self) -> Agent:
        try:
            return self.feedback_extractor_function()
        except Exception as e:
            print(f"Error building feedback_extractor: {e}")
            return None  # Or a placeholder agent

    # def feedback_validator_function(self) -> Agent:
    #     config = self.agents_config["feedback_validator"]
    #     return Agent(
    #         **config,
    #         allow_delegation=False,
    #         verbose=True
    #     )

    # @agent
    # def feedback_validator(self) -> Agent:
    #     try:
    #         return self.feedback_validator_function()
    #     except Exception as e:
    #         print(f"Error building feedback_validator: {e}")
    #         return None  # Or a placeholder agent

    # def feedback_storage_function(self) -> Agent:
    #     config = self.agents_config["feedback_storage"]
    #     return Agent(
    #         **config,
    #         allow_delegation=False,
    #         verbose=True
    #     )

    # @agent
    # def feedback_storage(self) -> Agent:
    #     try:
    #         return self.feedback_storage_function()
    #     except Exception as e:
    #         print(f"Error building feedback_storage: {e}")
    #         return None  # Or a placeholder agent
    # ////////////////////////////////////////
    # def extract_feedback_task_function(self) -> Task:
    #     config = self.tasks_config["extract_feedback"]
    #     print("extract_feedback_task_function>>>",config)
    #     return Task(
    #         # description=config["description"],
    #         agent=self.feedback_extractor(),
    #         # expected_output=config["expexted_output"],
    #     )

    # @task
    # def extract_feedback_task(self) -> Task:
    #     try:
    #         return self.extract_feedback_task_function()
    #     except Exception as e:
    #         print(f"Error building extract_feedback_task: {e}")
    #         return None  # Or a placeholder task
# //////////////////////////////
    def extract_feedback_task_function(self) -> Task:
        config = self.tasks_config["extract_feedback"]
        print("extract_feedback_task_function>>>", config)
        
        # Ensure the config has all required fields
        if not all(key in config for key in ["description", "expected_output"]):
            raise ValueError("Task config missing required fields: description, expected_output")

        return Task(
            description=f"Extract feedback from the file located at {self.input_file}.",
            expected_output=config["expected_output"],
            agent=self.feedback_extractor(),
            # Add other parameters if needed, e.g., output_file, async_execution
            # Wrap the context in a list to match the expected list type
            # context=[{"input_file": self.input_file}]  # Correct by wrapping the dict in a list
        )

    @task
    def extract_feedback_task(self) -> Task:
        try:
            return self.extract_feedback_task_function()
        except Exception as e:
            print(f"Error building extract_feedback_task: {e}")
            raise  # Re-raise the exception for debugging instead of returning None
# ///////////////////////////
    # def validate_feedback_task_function(self) -> Task:
    #     config = self.tasks_config["validate_feedback"]
    #     return Task(
    #         description=config["description"],
    #         agent=self.feedback_validator(),
    #     )

    # @task
    # def validate_feedback_task(self) -> Task:
    #     try:
    #         return self.validate_feedback_task_function()
    #     except Exception as e:
    #         print(f"Error building validate_feedback_task: {e}")
    #         return None  # Or a placeholder task
    
    # def save_feedback_task_function(self) -> Task:
    #     config = self.tasks_config["save_feedback"]
    #     return Task(
    #         description=config["description"],
    #         agent=self.feedback_storage(),
    #     )

    # @task
    # def save_feedback_task(self) -> Task:
    #     try:
    #         return self.save_feedback_task_function()
    #     except Exception as e:
    #         print(f"Error building save_feedback_task: {e}")
    #         return None  # Or a placeholder task

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[
                self.feedback_extractor(),
                # self.feedback_validator(),
                # self.feedback_storage()
            ],
            tasks=[
                self.extract_feedback_task(),
                # self.validate_feedback_task(),
                # self.save_feedback_task()
            ],
            process=Process.sequential,
            verbose=True
        )

    def run(self):
        try:
            result = self.crew().kickoff()  # Remove file_path argument
            return result
        except Exception as e:
            print(f"Error during crew execution: {e}")
            return {"Error in run feedback_crew >>", str(e)}
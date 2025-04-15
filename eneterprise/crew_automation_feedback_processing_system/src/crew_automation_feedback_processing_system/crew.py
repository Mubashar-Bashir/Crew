from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileReadTool
from crewai_tools import DirectoryReadTool
from crewai_tools import PDFSearchTool
from crewai_tools import TXTSearchTool
from crewai_tools import JSONSearchTool

@CrewBase
class CrewAutomationFeedbackProcessingSystemCrew():
    """CrewAutomationFeedbackProcessingSystem crew"""

    @agent
    def file_uploader(self) -> Agent:
        return Agent(
            config=self.agents_config['file_uploader'],
            tools=[FileReadTool(), DirectoryReadTool()],
        )

    @agent
    def json_data_extractor(self) -> Agent:
        return Agent(
            config=self.agents_config['json_data_extractor'],
            tools=[PDFSearchTool(), TXTSearchTool()],
        )

    @agent
    def json_structurer(self) -> Agent:
        return Agent(
            config=self.agents_config['json_structurer'],
            tools=[JSONSearchTool()],
        )

    @agent
    def sheets_integration(self) -> Agent:
        return Agent(
            config=self.agents_config['sheets_integration'],
            tools=[],
        )


    @task
    def validate_and_store_file_task(self) -> Task:
        return Task(
            config=self.tasks_config['validate_and_store_file_task'],
            tools=[FileReadTool(), DirectoryReadTool()],
        )

    @task
    def extract_text_task(self) -> Task:
        return Task(
            config=self.tasks_config['extract_text_task'],
            tools=[PDFSearchTool(), TXTSearchTool()],
        )

    @task
    def format_to_json_task(self) -> Task:
        return Task(
            config=self.tasks_config['format_to_json_task'],
            tools=[JSONSearchTool()],
        )

    @task
    def update_google_sheet_task(self) -> Task:
        return Task(
            config=self.tasks_config['update_google_sheet_task'],
            tools=[],
        )


    @crew
    def crew(self) -> Crew:
        """Creates the CrewAutomationFeedbackProcessingSystem crew"""
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )

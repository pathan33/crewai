# Type annotations and imports
from typing import List
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

# Import AI agent tools for search, scraping, file read/write, etc.
from crewai_tools import SerperDevTool, ScrapeWebsiteTool, DirectoryReadTool, FileWriterTool, FileReadTool

# Pydantic for input/output data structure validation
from pydantic import BaseModel, Field

# Load environment variables (e.g., for API keys)
from dotenv import load_dotenv
_ = load_dotenv()

# Initialize LLM (Gemini Flash 2.0 with moderately creative output)
llm = LLM(
    model="gemini/gemini-2.0-flash",
    temperature=0.7,
)

# Pydantic model to define structured content output format
class Content(BaseModel):
    content_type: str = Field(..., description="The type of content (blog, post, video, etc.)")
    topic: str = Field(..., description="The main topic of the content")
    target_audience: str = Field(..., description="Audience to target")
    tags: List[str] = Field(..., description="Relevant tags for the content")
    content: str = Field(..., description="The actual content body")

# Crew class definition using @CrewBase for marketing workflow
@CrewBase
class TheMarketingCrew():
    "The marketing crew is responsible for creating and executing marketing strategies, content creation, and managing marketing campaigns."

    # YAML configuration file paths
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # Define marketing leader agent
    @agent
    def head_of_marketing(self) -> Agent:
        return Agent(
            config=self.agents_config['head_of_marketing'],
            tools=[
                SerperDevTool(),
                ScrapeWebsiteTool(),
                DirectoryReadTool('resources/drafts'),
                FileWriterTool(),
                FileReadTool()
            ],
            reasoning=True,
            inject_date=True,
            llm=llm,
            allow_delegation=True,
            max_rpm=3
        )
    
    # Define social media content creator agent
    @agent
    def content_creator_social_media(self) -> Agent:
        return Agent(
            config=self.agents_config['content_creator_social_media'],
            tools=[
                SerperDevTool(),
                ScrapeWebsiteTool(),
                DirectoryReadTool('resources/drafts'),
                FileWriterTool(),
                FileReadTool()
            ],
            inject_date=True,
            llm=llm,
            allow_delegation=True,
            max_iter=30,
            max_rpm=3
        )

    # Define blog content writer agent
    @agent
    def content_writer_blogs(self) -> Agent:
        return Agent(
            config=self.agents_config['content_writer_blogs'],
            tools=[
                SerperDevTool(),
                ScrapeWebsiteTool(),
                DirectoryReadTool('resources/drafts/blogs'),
                FileWriterTool(),
                FileReadTool()
            ],
            inject_date=True,
            llm=llm,
            allow_delegation=True,
            max_iter=5,
            max_rpm=3
        )

    # Define SEO specialist agent
    @agent
    def seo_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['seo_specialist'],
            tools=[
                SerperDevTool(),
                ScrapeWebsiteTool(),
                DirectoryReadTool('resources/drafts'),
                FileWriterTool(),
                FileReadTool()
            ],
            inject_date=True,
            llm=llm,
            allow_delegation=True,
            max_iter=3,
            max_rpm=3
        )

    # TASK DEFINITIONS

    @task
    def market_research(self) -> Task:
        return Task(
            config=self.tasks_config['market_research'],
            agent=self.head_of_marketing()
        )

    @task
    def prepare_marketing_strategy(self) -> Task:
        return Task(
            config=self.tasks_config['prepare_marketing_strategy'],
            agent=self.head_of_marketing()
        )

    @task
    def create_content_calendar(self) -> Task:
        return Task(
            config=self.tasks_config['create_content_calendar'],
            agent=self.content_writer_social_media()
        )

    @task
    def prepare_post_drafts(self) -> Task:
        return Task(
            config=self.tasks_config['prepare_post_drafts'],
            agent=self.content_writer_social_media(),
            output_json=Content
        )

    @task
    def prepare_scripts_for_reels(self) -> Task:
        return Task(
            config=self.tasks_config['prepare_scripts_for_reels'],
            agent=self.content_writer_social_media(),
            output_json=Content
        )

    @task
    def content_research_for_blogs(self) -> Task:
        return Task(
            config=self.tasks_config['content_research_for_blogs'],
            agent=self.content_writer_blogs()
        )

    @task
    def draft_blogs(self) -> Task:
        return Task(
            config=self.tasks_config['draft_blogs'],
            agent=self.content_writer_blogs(),
            output_json=Content
        )

    @task
    def seo_optimization(self) -> Task:
        return Task(
            config=self.tasks_config['seo_optimization'],
            agent=self.seo_specialist(),
            output_json=Content
        )

    # Assemble the crew
    @crew
    def marketingcrew(self) -> Crew:
        """Creates the Marketing crew"""
        return Crew(
            agents=self.agents,          # All defined agents
            tasks=self.tasks,            # All defined tasks
            process=Process.sequential,  # Tasks run in order
            verbose=True,                # Enable detailed logs
            planning=True,               # LLM will help plan execution steps
            planning_llm=llm,
            max_rpm=3                    # Rate limit per minute
        )


# Run the crew if this script is executed directly
if __name__ == "__main__":
    from datetime import datetime

    # Define the input parameters to the marketing workflow
    inputs = {
        "product_name": "AI Powered Excel Automation Tool",
        "target_audience": "Small and Medium Enterprises (SMEs)",
        "product_description": "A tool that automates repetitive tasks in Excel using AI, saving time and reducing errors.",
        "budget": "Rs. 50,000",
        "current_date": datetime.now().strftime("%Y-%m-%d"),
    }

    # Instantiate and run the marketing crew
    crew = TheMarketingCrew()
    crew.marketingcrew().kickoff(inputs=inputs)

    print("Marketing crew has been successfully created and run.")


# ✅ Flow / Highlights of the Code

# 1. Environment and Model Setup
    # Loads environment variables from .env.
    # Initializes a Gemini LLM (gemini-2.0-flash) for content generation with moderate creativity.

# 2. Pydantic Model for Output
    # Content model ensures all generated outputs (posts, blogs, etc.) are structured and validated.

# 3. Agent Definitions
    # Head of Marketing: Oversees strategy, performs research, can delegate tasks.
    # Social Media Creator: Creates posts, scripts, content calendar.
    # Blog Writer: Writes blog posts and performs related research.
    # SEO Specialist: Optimizes content for search engine visibility.

    # Each agent is equipped with tools for:

        # Searching (SerperDevTool)
        # Scraping (ScrapeWebsiteTool)
        # Reading/Writing files (FileReadTool/FileWriterTool)
        # Reading directories (DirectoryReadTool)

# 4. Task Definitions
    # Tasks cover the complete content lifecycle:
        # Market research
        # Strategy preparation
        # Content planning (calendar)
        # Drafting social and blog content
        # Creating scripts for reels
        # Blog research and writing
        # SEO optimization

# 5. Crew Assembly
    # Crew uses all agents and tasks in a sequential process.
    # Planning mode is enabled, letting LLM dynamically plan execution order and steps.
    # Memory isn't explicitly used, but structured content output is handled via output_json.

# 6. Execution
    # The script passes product and marketing details as input.
    # The crew is launched using .kickoff(inputs=...).
    # Tasks are executed in order, agents work collaboratively, and results are generated.

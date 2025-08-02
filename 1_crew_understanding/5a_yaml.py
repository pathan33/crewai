## https://docs.crewai.com/en/quickstart

# ✅ Till now, we have been creating agents and tasks individually by having inline prompts, the LLM instantiations
# and the tools defined in the code. This is not a scalable approach, especially when we have multiple agents
# and tasks. In this file, we will see how to use YAML files to define agents, tasks, and their configurations.

# ✅ This refactored code represents a modular, scalable, and maintainable approach to building an AI crew system using CrewAI. 
# It introduces loose coupling, separation of concerns, reusability and Environment-Agnostic through the use of:
    # - YAML configuration files (agents.yaml and tasks.yaml)
    # - Decorators like @CrewBase, @agent, @task, and @crew
    # - An OOP-style class (BlogCrew) encapsulating the crew logic

# This approach also helps in Environment-Agnostic development - YAML allows easier adaptation for different environments, projects, or user inputs.
# Rapid Iteration - Teams (especially non-developers) can update task goals, tools, and descriptions via YAML without modifying core logic.

# Import required classes from crewai
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

# Import external tools for web search, scraping, and file I/O
# from crewai_tools import SerperDevTool, ScrapeWebsiteTool, DirectoryReadTool, FileWriterTool, FileReadTool

# Load environment variables from a .env file
from dotenv import load_dotenv
load_dotenv()

# Define a blog writing crew class using CrewBase decorator
@CrewBase
class BlogCrew():
    """Blog writing crew"""

    # Paths to YAML config files for agents and tasks
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # Define a researcher agent using a config from the YAML file
    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['research_agent'],  # Reference to YAML config for researcher
            #tools=[SerperDevTool()],                      # Uses a web search tool
            verbose=True                                  # Enable detailed output
        )

    # Define a writer agent using a config from the YAML file
    @agent
    def writer(self) -> Agent:
        return Agent(
            config=self.agents_config['writer_agent'],  # Reference to YAML config for writer
            verbose=True                                # Enable detailed output
        )

    # Define a task for the researcher to perform
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],  # Reference to YAML config for task
            agent=self.researcher()                     # Assign researcher agent to task
        )

    # Define a task for the writer to generate the blog post
    @task
    def blog_task(self) -> Task:
        return Task(
            config=self.tasks_config['blog_task'],      # Reference to YAML config for task
            agent=self.writer()                         # Assign writer agent to task
        )

    # Create a crew by combining agents and their respective tasks
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.researcher(), self.writer()],         # List of participating agents
            tasks=[self.research_task(), self.blog_task()]     # List of tasks to be executed
        )

# If the script is run directly (not imported)
if __name__ == "__main__":
    blog_crew = BlogCrew()  # Instantiate the crew
    # Kick off the workflow with an input topic
    blog_crew.crew().kickoff(inputs={"topic": "The future of electrical vehicles"})


## Important Notes:

# ✅ Even though I don’t pass the paths to the YAML config files for agents.yaml and tasks.yaml, how is the code still able to identify and load them?
   
        # Paths to YAML config files for agents and tasks
        # agents = "config/agents.yaml"
        # tasks = "config/tasks.yaml"

        ## The @CrewBase decorator automatically discovers and loads agents.yaml and tasks.yaml files from the following default paths: 
            # config/agents.yaml and 
            # config/tasks.yaml

        ## When you decorate your class with @CrewBase, here’s what happens behind the scenes:
        
        # 1. Implicit Discovery
            # If you don’t explicitly define:
                # agents = "config/agents.yaml"
                # tasks = "config/tasks.yaml"
            
                # and assume you wrote the code as follows:
                # agents = List[BaseAgent]
                # tasks = List[BaseAgent]

            # The @CrewBase system assumes defaults:
                # config/agents.yaml for agents
                # config/tasks.yaml for tasks

            # It looks in the same directory tree as your crew class (e.g., src/latest_ai_development/) for a config folder.

        # 2. Auto-wiring via Decorators
            # The @agent and @task decorators register your functions and look up the corresponding YAML entries by name.

            # It matches your method name (e.g., researcher, reporting_analyst) to keys in agents.yaml.

            # Same for research_task, reporting_task → tasks.yaml.

            # This is why these names must match exactly between the methods and YAML keys unless explicitly overridden.

    # ✅ When Should You Provide Explicit Paths?
        # You only need to manually set the config paths if:

            # - You want to load YAMLs from a different directory
            # - You're working in a monorepo with shared configs
            # - You have multiple crews with different configs in the same app

        # Example override:
            # agents_config = "my_custom_folder/my_agents.yaml"
            # tasks_config = "my_custom_folder/my_tasks.yaml"

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------

# ✅ Flow / Highlights of the Code

# 1. Configuration Files (YAML-Based Setup)
    # agents.yaml defines the roles, goals, and backstories for:

        # research_agent: Conducts in-depth research on a given topic.
        # writer_agent: Converts research into structured, readable reports.

    # tasks.yaml defines the sequence of tasks:

        # research_task: Instructs the researcher to gather up-to-date insights.
        # blog_task: Assigns the reporting analyst to write a detailed report from the research.

# 2. Crew Definition (OOP + Decorators)
    # BlogCrew class:

        # Decorated with @CrewBase to enable automatic configuration loading.
        # Defines @agent methods for creating agents using YAML configs.
        # Defines @task methods to bind agents to their respective tasks.
        # Defines a @crew method to assemble and run the full workflow.

# 3. Automation & Defaults
    # Explicit paths to the YAML files are set config/agents.yaml and config/tasks.yaml.
    # Method names (e.g. research_agent, research_task) must match the keys in the YAML files for implicit wiring.

# 4. Execution Logic (main.py)
    # When the script runs:

        # The BlogCrew Class is instantiated.
        # The crew is kicked off using .crew().kickoff(inputs={"topic": "The future of electrical vehicles"})
        # The workflow proceeds sequentially:
            # research_task gathers findings on the topic.
            # blog_task generates a detailed report.
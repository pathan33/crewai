# Load environment variables from a .env file (e.g., API keys)
from dotenv import load_dotenv
load_dotenv()

# Import the LLM wrapper from crewai
from crewai import LLM
import os

# Initialize a Gemini model with low temperature (more deterministic output)
llm = LLM(
    model="gemini/gemini-2.0-flash",
    temperature=0.1
)

# Import core CrewAI components
from crewai import Agent, Task, Crew
# from crewai_tools import SerperDevTool  # Optional tool for web search (commented out)

# Define the research agent responsible for gathering factual data
research_agent = Agent(
    role="Research Specialist",  # Agent's role
    goal="Research interesting facts about the topic: {topic}",  # Dynamic goal based on topic
    backstory="You are an expert at finding relevant and factual data.",  # Describes agent's personality
    # tools=[SerperDevTool()],  # Tool for live search (currently not used)
    verbose=True,  # Enables detailed output/logging
    llm=llm        # Assigns the LLM to the agent
)

# Define the writer agent responsible for producing the blog summary
writer_agent = Agent(
    role="Creative Writer",  # Agent's role
    goal="Write a short blog summary using the research",  # Goal using input from research agent
    backstory="You are skilled at writing engaging summaries based on provided content.",  # Agent’s skill description
    llm=llm,
    verbose=True
)

# First task: instruct research agent to find recent interesting facts
task1 = Task(
    description="Find 3-5 interesting and recent facts about {topic} as of year 2025.",
    expected_output="A bullet list of 3-5 facts",
    agent=research_agent
)

# Second task: instruct writer to use the research and create a blog post
task2 = Task(
    description="Write a 100-word blog post summary about {topic} using the facts from the research.",
    expected_output="A blog post summary",
    agent=writer_agent,
    context=[task1]  # Uses the output from task1 as input
)

# Define the crew that brings together both agents and tasks
crew = Crew(
    agents=[research_agent, writer_agent],  # List of agents in the workflow
    tasks=[task1, task2],                   # List of tasks to perform
    verbose=True,                           # Enables logging
    memory=True,                            # Enables memory so agents retain context between tasks
    embedder={                              # Embedder configuration for semantic memory
        "provider": "google",
        "config": {
            "api_key": os.getenv("GEMINI_API_KEY"),  # Retrieves API key from .env
            "model": "text-embedding-004"            # Embedding model for context memory (https://docs.crewai.com/en/concepts/memory)
        }
    }
)

# Run the full crew workflow with a topic about electric vehicles
crew.kickoff(inputs={"topic": "The future of electrical vehicles"})

# Run the same crew again with a different topic; memory will retain prior context
crew.kickoff(inputs={"topic": "What is the revenue outlook in this sector?"})

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------

# ✅ Flow / Highlights of the Code

# 1. `Environment Setup:`

    # - Loads .env variables using load_dotenv() to securely handle environment configurations if any.

# 2. `Model Initialization:`

    # - Initializes a Gemini 2.0 Flash model via LLM() with low temperature of 0.1 (for accuracy and consistency).

# 3. `Agent Creation:`

    # - Research Agent: Gathers recent, factual data on the given topic.
    # - Writer Agent: Crafts a concise blog summary based on the research findings.

# 4. `Task Definition:`

    # - Task 1: Research agent finds 3–5 interesting and up-to-date facts.
    # - Task 2: Writer agent uses facts from Task 1 to compose a concise blog post.

# 5. `Crew Formation:`

    # - Bundles both agents and tasks into a single crew workflow.
    # - Enables Memory using Google’s embedding API (text-embedding-004), allowing contextual memory between runs.

# 6. `Execution:`

    # - First Run: Topic is “The future of electrical vehicles”.
    # - Second Run: Topic is “What is the revenue outlook in this sector?” — previous context may influence this response due to memory being enabled.

# For more information on the memory feature, refer to the official documentation: https://docs.crewai.com/en/concepts/memory

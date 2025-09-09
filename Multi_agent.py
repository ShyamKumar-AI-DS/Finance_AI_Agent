from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.googlesearch import GoogleSearch
from phi.tools.yfinance import YFinanceTools

from dotenv import load_dotenv
load_dotenv()

# web_search = Agent(
#     name = ("Search Agent"),
#     model = Groq(id = "llama-3.3-70b-versatile"),
#     tools=[GoogleSearch()],
#     show_tool_calls = True,
#     mardown = True,
#     instructions=["Always include web sources used to search"]

# )

# finance_agent = Agent(
#     name = ("Finance Agent"),
#     model = Groq(id = "llama-3.3-70b-versatile"),
#     tools= [YFinanceTools(stock_price=True,stock_fundamentals=True,analyst_recommendations=True)],
#     show_tool_calls = True,
#     markdown = True,
#     instructions=["Use tables to display data for better understandability"]
# )

# team_agent = Agent(
#     team=[web_search,finance_agent],
#     model = Groq(id = "llama-3.3-70b-versatile"),
#     show_tool_calls = True,
#     markdown = True,
#     instructions=["Always include web sources used to search","Use tables to display data for better understandability"],

# )

web_search = Agent(
    name="Search Agent",
    model=Groq(id="deepseek-r1-distill-llama-70b", max_tokens=500),
    tools=[GoogleSearch()],
    show_tool_calls=False,
    markdown=True,
    instructions=[
        "Search for recent news about the company",
        "Always include sources with hyperlinks",
        "Focus only on relevant information",
        "Be concise and factual"
    ]
)

finance_agent = Agent(
    name="Finance Agent",
    model=Groq(id="deepseek-r1-distill-llama-70b", max_tokens=500),
    tools=[YFinanceTools(
        stock_price=True,
        stock_fundamentals=True,
        analyst_recommendations=True
    )],
    show_tool_calls=False,
    markdown=True,
    instructions=[
        "Provide only factual financial data",
        "Use tables for structured data",
        "No explanations or preambles",
        "Focus on key metrics only"
    ]
)

team_agent = Agent(
    team=[web_search, finance_agent],
    model=Groq(id="deepseek-r1-distill-llama-70b", max_tokens=1000),
    show_tool_calls=False,
    markdown=True,
    instructions=[
        "Synthesize information from all agents",
        "Remove all preambles and boilerplate text",
        "Structure output in clear sections",
        "Use tables for data, bullet points for news",
        "Keep responses under 300 words",
        "Always include sources for news"
    ],
)
team_agent.print_response("Analyze AAPL fundamentals")



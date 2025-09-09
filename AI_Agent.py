from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.yfinance import YFinanceTools

from dotenv import load_dotenv
import os
load_dotenv()

agents = Agent(
    model = Groq(id = "llama-3.3-70b-versatile"),
    tools= [YFinanceTools(stock_price=True,stock_fundamentals=True,analyst_recommendations=True)],
    show_tool_calls = True,
    markdown = True,
    instructions=["Use tables to display data"]
)

agents.print_response("Summarize and compare analyst recommendation and stock fundamentals of TSLA & AAPL",show_full_reasoning=True)

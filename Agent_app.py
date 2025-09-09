import os
import re
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.googlesearch import GoogleSearch
from phi.tools.yfinance import YFinanceTools

# Load environment variables
load_dotenv()

# Check if Groq API key is set
if not os.getenv("GROQ_API_KEY"):
    st.error("❌ GROQ_API_KEY not found in environment variables. Please set it in your .env file.")
    st.stop()

# Set up the page
st.set_page_config(page_title="Stock Analysis Agent", page_icon="📈", layout="wide")
st.title("📈 AI Stock Analysis Agent")
st.markdown("Ask questions about stocks, and I'll analyze using web search and financial data.")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize agents only once using st.cache_resource
@st.cache_resource
def get_agents():
    web_search = Agent(
        name="Search Agent",
        model=Groq(id="qwen/qwen3-32b", max_tokens=800),
        tools=[GoogleSearch()],
        show_tool_calls=False,
        markdown=True,
        instructions=[
            "Search for recent news about the company",
            "Return only factual information with sources",
            "No explanations or preambles",
            "Use bullet points for news items"
        ]
    )

    finance_agent = Agent(
        name="Finance Agent",
        model=Groq(id="qwen/qwen3-32b", max_tokens=800),
        tools=[YFinanceTools(
            stock_price=True,
            stock_fundamentals=True,
            analyst_recommendations=True
        )],
        show_tool_calls=False,
        markdown=True,
        instructions=[
            "Provide only factual financial data",
            "Use markdown tables for structured data",
            "No explanations or preambles",
            "Focus on key metrics only"
        ]
    )

    team_agent = Agent(
        team=[web_search, finance_agent],
        model=Groq(id="qwen/qwen3-32b", max_tokens=1000),
        show_tool_calls=False,
        markdown=True,
        instructions=[
            "Synthesize information from all agents",
            "REMOVE ALL preambles, explanations, and boilerplate text",
            "Structure output in clear sections with proper headers",
            "Use tables for data, bullet points for news",
            "Keep responses concise and factual",
            "ALWAYS remove content like 'content_type=', 'event=', 'messages=', 'metrics='",
            "Only show the final clean structured output"
        ],
    )
    return team_agent

# Get the agent team
team_agent = get_agents()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Helper: Extract clean content from response ---
def extract_clean_content(response_obj) -> str:
    """Extract clean content from agent response object"""
    if hasattr(response_obj, 'content') and response_obj.content:
        return str(response_obj.content)
    return str(response_obj)

# --- Helper: Clean response text ---
def clean_response(text: str) -> str:
    """Remove all unwanted preambles, metadata, and formatting issues"""
    if not text:
        return ""
    
    # Convert to string
    text = str(text)
    
    # Remove content= wrapper and metadata
    text = re.sub(r'content_type=.*?(?=\n|$)', '', text)
    text = re.sub(r'event=.*?(?=\n|$)', '', text)
    text = re.sub(r'messages=\[.*?\]', '', text, flags=re.DOTALL)
    text = re.sub(r'metrics=.*?(?=\n|$)', '', text)
    text = re.sub(r'run_id=.*?(?=\n|$)', '', text)
    text = re.sub(r'agent_id=.*?(?=\n|$)', '', text)
    text = re.sub(r'model=.*?(?=\n|$)', '', text)
    text = re.sub(r'created_at=.*?(?=\n|$)', '', text)
    
    # Remove system message artifacts
    text = re.sub(r'## You are the leader of a team.*?(?=\n\n|$)', '', text, flags=re.DOTALL)
    text = re.sub(r'Agents in your team:.*?(?=\n\n|$)', '', text, flags=re.DOTALL)
    
    # Remove tool call artifacts
    text = re.sub(r'<tool_call.*?>', '', text)
    text = re.sub(r'tool_call_id=.*?(?=\n|$)', '', text)
    text = re.sub(r'tool_name=.*?(?=\n|$)', '', text)
    text = re.sub(r'tool_args=.*?(?=\n|$)', '', text, flags=re.DOTALL)
    
    # Remove retry messages
    text = re.sub(r'It seems there was an issue.*?try again:', '', text, flags=re.DOTALL)
    text = re.sub(r'Let me try again.*?:', '', text)
    
    # Remove extra whitespace and clean up
    text = re.sub(r'\\n', '\n', text)
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    text = text.strip()
    
    # Remove common preamble phrases
    preamble_patterns = [
        r'^.*?analysis.*?:?',
        r'^Based.*?information.*?:?',
        r'^I found.*?:',
        r'^Here.*?results.*?:',
        r'^Summary.*?:'
    ]
    
    for pattern in preamble_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE, count=1).strip()
    
    return text.strip()

# --- Helper: Parse Markdown tables into pandas DataFrame ---
def extract_and_render_tables(text: str):
    """
    Detect Markdown-style tables and render them using st.table().
    Returns cleaned text without the raw Markdown tables.
    """
    # Handle both markdown and HTML tables
    markdown_table_pattern = r"(\|(?:[^\n]*\|)+\n\|(?:\s*[-:]+\s*\|)+\n(?:\|(?:[^\n]*\|)*\n)*)"
    html_table_pattern = r"(<table>.*?</table>)"
    
    # Process HTML tables first
    html_matches = re.findall(html_table_pattern, text, re.DOTALL)
    for table in html_matches:
        try:
            # Convert HTML table to DataFrame
            rows = re.findall(r'<tr>(.*?)</tr>', table, re.DOTALL)
            if len(rows) >= 2:
                # Extract headers
                header_matches = re.findall(r'<th>(.*?)</th>', rows[0])
                headers = [h.strip() for h in header_matches]
                
                # Extract data rows
                data = []
                for row in rows[1:]:
                    cell_matches = re.findall(r'<td>(.*?)</td>', row)
                    if cell_matches:
                        data.append([c.strip() for c in cell_matches])
                
                if headers and data:
                    df = pd.DataFrame(data, columns=headers)
                    st.table(df)
        except Exception:
            st.markdown(table, unsafe_allow_html=True)
        
        text = text.replace(table, "")
    
    # Process markdown tables
    md_matches = re.findall(markdown_table_pattern, text)
    for table in md_matches:
        try:
            # Convert Markdown table into DataFrame
            lines = [line.strip() for line in table.strip().split("\n") if line.strip()]
            if len(lines) >= 3:
                # Parse header
                header = [h.strip() for h in lines[0].strip("|").split("|")]
                # Skip separator line (lines[1])
                data = []
                for line in lines[2:]:
                    row = [r.strip() for r in line.strip("|").split("|")]
                    if len(row) == len(header):
                        data.append(row)
                
                if data:
                    df = pd.DataFrame(data, columns=header)
                    st.table(df)
        except Exception:
            st.markdown(table)
        
        text = text.replace(table, "")
    
    return text.strip()

# --- Helper: Format news items ---
def format_news_section(text: str):
    """Extract and format news items as bullet points"""
    if not text.strip():
        return text
    
    # Look for news sections
    news_patterns = [
        r"(Latest News.*?)(?=\n##|\Z)",
        r"(Recent News.*?)(?=\n##|\Z)",
        r"(News.*?)(?=\n##|\Z)"
    ]
    
    for pattern in news_patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            news_content = match.group(1)
            # Extract bullet points or lines
            bullets = re.findall(r"[*\-]\s*(.+)", news_content)
            if not bullets:
                # If no bullets, split by lines
                lines = [line.strip() for line in news_content.split('\n') if line.strip() and not line.startswith('#')]
                bullets = [line for line in lines if not re.match(r'^\s*\|', line)]
            
            if bullets:
                st.subheader("📰 Latest News")
                for bullet in bullets[:5]:  # Limit to 5 news items
                    clean_bullet = re.sub(r'\s+', ' ', bullet).strip()
                    if clean_bullet:
                        st.markdown(f"- {clean_bullet}")
                # Remove news section from text
                text = text.replace(match.group(0), "")
            break
    
    return text.strip()

# User input
if prompt := st.chat_input("Ask about stocks (e.g., 'Analyze AAPL fundamentals' or 'What's the news on TSLA?')"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Show processing indicator
            with st.spinner("🔍 Analyzing stock data..."):
                # Run the agent (non-streaming for stability)
                response = team_agent.run(prompt)
                
                # Extract clean content
                raw_response = extract_clean_content(response)
                
                # Apply multiple cleaning passes
                full_response = clean_response(raw_response)
                
                # Extract and render tables first
                remaining_text = extract_and_render_tables(full_response)
                
                # Format news section
                remaining_text = format_news_section(remaining_text)
                
                # Final cleaning
                remaining_text = clean_response(remaining_text)
                
                # Show cleaned remaining text
                if remaining_text.strip():
                    # Add section headers if they don't exist
                    if remaining_text.strip() and not re.search(r"^##", remaining_text, re.MULTILINE):
                        if "News" in remaining_text or "news" in remaining_text:
                            st.subheader("📊 Financial Metrics")
                        elif any(keyword in remaining_text.lower() for keyword in ["metric", "value", "price", "recommend"]):
                            st.subheader("📊 Key Metrics")
                    
                    # Clean up any remaining artifacts
                    remaining_text = re.sub(r'^.*?of.*?\n', '', remaining_text, count=1)  # Remove "Analysis of XYZ" lines
                    remaining_text = re.sub(r'Sources:.*$', '', remaining_text, flags=re.DOTALL)  # Remove sources section
                    
                    if remaining_text.strip():
                        message_placeholder.markdown(remaining_text)
                else:
                    st.info("No structured data available for this query.")
            
            # If no content was rendered, show raw response
            if not full_response.strip():
                st.warning("No structured data found. Showing raw response:")
                st.text(raw_response[:500] + "..." if len(raw_response) > 500 else raw_response)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            full_response = f"An error occurred: {str(e)}"
            message_placeholder.markdown(full_response)
    
    # Add assistant response to history (cleaned)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Add sidebar info
with st.sidebar:
    st.header("About this Agent")
    st.info("""
    This AI agent combines:
    - **Web Search** for latest news
    - **Yahoo Finance** for stock data
    - **LLM Analysis** for insights
    
    Example queries:
    - Analyze AAPL fundamentals
    - Compare TSLA vs GM stock performance
    - What are analysts saying about NVDA?
    """)
    st.markdown("---")
    st.markdown("Powered by Groq & Llama 3.3")
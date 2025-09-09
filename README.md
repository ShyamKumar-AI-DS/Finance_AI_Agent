# 📈 AI Stock Analysis Agent

<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/a743b8a9-0839-4c38-a663-e2897bdbc939" />
  
*An intelligent agent that analyzes stocks using real-time financial data and web search.*

This Streamlit app combines **web search**, **Yahoo Finance data**, and **LLM-powered analysis** to provide insightful, structured responses about stocks — all in one clean interface.

---

## 🔍 Features

✅ **Real-Time Stock Fundamentals**  
Fetch key metrics like P/E ratio, EPS, dividend yield, market cap, and more from Yahoo Finance.

✅ **Latest News Integration**  
Search the web for recent news and developments related to any company (e.g., Apple, Tesla).

✅ **Analyst Sentiment Summary**  
Get a breakdown of analyst recommendations (Buy, Hold, Sell) with counts.

✅ **Clean, Structured Output**  
Responses are automatically cleaned and formatted into tables, bullet points, and sections — no noise.

✅ **Multi-Agent Architecture**  
Uses a team of specialized agents:
- **Web Search Agent**: Finds recent news
- **Finance Agent**: Extracts financial data
- **Team Agent**: Synthesizes insights and presents them cleanly

---

## 🛠️ Tech Stack

| Component | Technology |
|--------|-----------|
| Framework | [Streamlit](https://streamlit.io) |
| LLM Model | [Groq + Qwen3-32B](https://groq.com) |
| Tools | [Google Search](https://github.com/phi-lang/phi), [Yahoo Finance](https://github.com/phi-lang/phi) |
| Data Processing | Python, Pandas, Regular Expressions |
| Environment | `.env`, `python-dotenv` |
| Deployment | [Streamlit Community Cloud](https://streamlit.io/cloud) |

---

## 🚀 Getting Started (Local Development)

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/stock-analysis-agent.git
cd stock-analysis-agent

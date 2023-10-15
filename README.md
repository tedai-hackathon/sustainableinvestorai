# 💸 Sustainable Investor AI: 
**Empowering Sustainability Investments, One Click at a Time**

SustainableInvestorAI is an investment assistant catered to the needs of financial analysts who need accurate and timely information for sustainability-concious investments. By merging diverse data sources on the environmental and financial performances of companies with recent news streams and leveraging the power of multiple large language models, SustainableInvestorAI aims at painting a comprehensive picture of a company's risk factors, empowering a more holistic approach to investment. 

## Features
📊 **Single Company Analysis**:
- Analyze companies from various industry sectors, generate insights on the financial and sustainability performances.
- Stay updated with the top news sentiment surrounding the company's sustainability efforts for the past month, do not be surprised by any events. 
- These are the different sections:
  - **Company Overview**: Get a quick overview of the company.
  - **News Sentiment**: Stay updated with the top news sentiment surrounding the company's sustainability efforts for the past month.
  - **Sustainability Report Summary**: A quick overview of the sustainability efforts of a company for the current year.
  - **Trustability Score**: Judge the adherence of the company's sustainability report to industry standards.
  - **Analysis Questions**: Communicate with the company's sustainability report in an interactive environment and pull out the necessary insights.
  

📄 **Multiple Company Analysis**:
- Compare and contrast insights from the sustainability reports of companies within the same sector.

📄 **Multiple Company Interactive Table**:
- The most popular sustainability metrics of companies just one click away! 
- Choose the metrics you are interested in and compare a company's performance relative to the industry averages. 


## Tech Stack 
**Streamlit**: Powers the frontend, providing a seamless user interface. 
**Llama Index**: The data framework behind the Retrieval Augmented Generation (RAG) which allows to draw insights from the companies' sustainability reports.
**Alpha Vantage**: The go-to API service for fetching the most recent financial data and news articles about companies.


### **Local Setup**:


1. **Clone the Repository**:
```bash
git clone https://github.com/tedai-hackathon/sustainableinvestorai
cd sustainableinvestorai
```

2. **Install Required Dependencies**:
```bash
pip install -r requirements.txt
```

You can get your API keys here: [AlphaVantage](https://www.alphavantage.co/support/#api-key), [OpenAI](https://openai.com/blog/openai-api), [Anthropic](https://www.anthropic.com/earlyaccess)

```bash
# add the following API keys
av_api_key = "ALPHA_VANTAGE API KEY"

openai_api_key = "OPEN AI API KEY"

anthropic_api_key = ANTHROPIC_API_KEY

```

3. **Run SustainableInvestorAI**:
```bash
streamlit run src/Home.py
```

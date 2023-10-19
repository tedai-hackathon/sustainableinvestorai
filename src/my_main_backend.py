import json

import anthropic
from PyPDF2 import PdfReader
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
import csv
import requests 

import streamlit as st

from companydata import company_data

#selected_company = "BP"

class MainBackend:

    def __init__(_self):
        _self.model = anthropic.Anthropic()

    @st.cache_data
    def pull_company_overview(_self,selected_company):
        AV_API_KEY = "8X52OCUIN0Z13TRG"
        url = "https://www.alphavantage.co/query"
        if selected_company in company_data:
            ticker = company_data[selected_company]["ticker"]
            # Pull company info from Alpha Vangard API
            params = {
                "function": "OVERVIEW",
                "symbol": ticker, 
                "apikey": AV_API_KEY
                }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if not data:
                    print(f"No overview data found for {ticker}")
                    return None
                symbol = data.get("Symbol")
                assettype = data.get("AssetType")
                name = data.get("Name")
                desc = data.get("Description")
                exchange = data.get("Exchange")
                sector=data.get("Sector").lower()
                industry = data.get("Industry").lower()
                address = data.get("Address")
                marketcap = data.get("MarketCapitalization")
                marketcap_bil = round(int(marketcap)/1000000000,2)
                sharehigh = data.get("52WeekHigh")
                sharelow = data.get("52WeekLow")

                overview = f"""Company's official name is {name}. The company trades in the {exchange} with the ticker symbol "{symbol}".
                      {desc} The address of the headquarters is {address}.
                      {selected_company} operates in the {sector} sector within the {industry} industry. 
                      {selected_company}'s market capitalization is \\${marketcap_bil} billion. 
                      In the past year, {selected_company}'s highest share price was \\${sharehigh} and lowest share price was \\${sharelow}.
                      """
            else:
                print(f"Error: {response.status_code} - {response.text}")

            return overview
            
    @st.cache_data
    def pull_company_news(_self, selected_company):
        AV_API_KEY = "8X52OCUIN0Z13TRG"
        url = "https://www.alphavantage.co/query"
        if selected_company in company_data:
            ticker = company_data[selected_company]["ticker"]
            params = {
                "function": "NEWS_SENTIMENT",
                "tickers": ticker, 
                "apikey": AV_API_KEY,
                "sort": "RELEVANCE",
                "limit":1000,
                "time_from":"20230901T0100"
                }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                num_items = int(data.get("items"))
                data_feed = data["feed"]
                #data_feed = data_feed[:5]
                newstitle_all = []
                description_all = []
                sentiment_score_all = []
                source_all = []
                url_all = []
                time_all = []
                for item in range(0,num_items):
                    # get news title 
                    news_title = data_feed[item].get("title")
                    newstitle_all.append(news_title)
                    # get news summary 
                    description = data_feed[item].get("summary")
                    description_all.append(description)
                    # get news sentiment score 
                    sentiment_score = data_feed[item].get("overall_sentiment_score")
                    sentiment_score_all.append(sentiment_score)
                    # get news source 
                    source = data_feed[item].get("source")
                    source_all.append(source)
                    # get url 
                    url = data_feed[item].get("url")
                    url_all.append(url)
                    # get time 
                    time = data_feed[item].get("time_published")
                    time_all.append(time)

                keywords = ["sustainability","carbon","pollutant","emission","green","climate","EV","natural gas"]
                matching_indices = [index for index, summary in enumerate(description_all) if any(keyword in summary for keyword in keywords)]
                matching_indices = matching_indices[:4]
                
                #sustainability_news = [newstitle_all[i] for i in matching_indices if selected_company in newstitle_all[i]]
                company_title = [newstitle_all[i] for i in matching_indices]
                company_sentiment = [sentiment_score_all[i] for i in matching_indices]
                company_source = [source_all[i] for i in matching_indices]
                company_url = [url_all[i] for i in matching_indices]
                company_time = [time_all[i] for i in matching_indices]

            else: 
                print(f"Error: {response.status_code} - {response.text}")
            
            return company_title, company_sentiment, company_source, company_url, company_time

        
    @st.cache_data
    def generate_prompt_with_user_question(_self, uploaded_file_path, question,selected_company):
        # Set company information params
        if selected_company in company_data:
            company_info = company_data[selected_company]
            company_name = company_info["name"]
            company_location = company_info["location"]
            company_industry = company_info["industry"]
            
            # Set up the prompt
            query = f"""
            As a senior equity analyst with expertise in analyzing a company's sustainability report, you are presented with the following background information: 

            Company: {company_name}
            Location: {company_location}
            Sector: {company_industry}
            
            With the above information, please read through the sustainability report and respond to the following question, ensuring to reference the relevant parts in the report. 
            
            QUESTION: {question}
            
            Please adhere to the following guidelines in your answer: 

            1. Your response must be precise, thorough, and grounded on specific extracts from the report. 
            2. Answer the question only if you know the answer or can make a well-informed guess; otherwise tell me you don't know it. 
            3. Read through the whole document and print out all the sentences in the report you base your answer on in the EXCERPT section.
            4. Keep your ANSWER within 150 words. 
            5. Be skeptical to the information disclosed in the report as there might be greenwashing (exaggerating the firm's environmental responsibility). Always answer in a critical tone.
            
            Your response to the question should be formatted in JSON with three keys: 
            
            1. QUESTION: {question}
            2. ANSWER: Your answer to the question (be in a string format).
            3. EXCERPT: The sentences in the report from which you derive your answers to the question. 

            Your FINAL_ANSWER in JSON (ensure there’s no format error):"""
            
            reader = PdfReader(uploaded_file_path)

            pdf_name = "".join([company_name,".pdf"])
            
            article_text = [f""" {pdf_name} <DOC> """]
            
            for page in reader.pages:
                article_text.append(page.extract_text())
            article_text.append("""</DOC>""")
            article_text = "\n\n".join(article_text)
                
            prompt = f"{HUMAN_PROMPT} {article_text + query} {AI_PROMPT}"
                
            return prompt
        else:
            pass

    @st.cache_data
    def generate_response_for_user_question(_self, uploaded_report_path, question,selected_company):
        response = _self.model.completions.create(
            model="claude-2",
            max_tokens_to_sample=400000,
            prompt=_self.generate_prompt_with_user_question(uploaded_report_path, question,selected_company)
        )
        return json.loads(_self.find_json_in_response(response.completion))

    @st.cache_data
    def generate_prompt_for_trustability_score(_self, uploaded_file_path, question, question_guideline, requirement, selected_company):

        if selected_company in company_data:
            company_info = company_data[selected_company]
            company_name = company_info["name"]
            company_location = company_info["location"]
            company_industry = company_info["industry"]
            
            # Set up the prompt and directory path
            
            sustainability_query = f"""
            
            As a senior equity analyst with expertise in sustainability evaluating a company's sustainability report, you are presented with the following background information: 

            Company: {company_name}
            Location: {company_location}
            Sector: {company_industry}
            
            With the above information, please read through the sustainability report and respond to the following question, ensuring to reference the relevant parts in the report.
            
            QUESTION: {question}
            
            Please adhere to the following guidelines in your answer: 

            1. Your response must be precise, thorough, and grounded on specific extracts from the report. 
            2. Answer the question only if you know the answer or can make a well-informed guess; otherwise tell me you don't know it. 
            3. Read through the whole document and print out all the sentences in the report you base your answer on in the EXCERPT section.
            4. Keep your ANSWER and ANALYSIS within 150 words. 
            5. Be skeptical to the information disclosed in the report as there might be greenwashing (exaggerating the firm's environmental responsibility). Always answer in a critical tone.
            6. Scrutinize whether the report is grounded on quantifiable, concrete data or vague, unverifiable statements, and communicate your findings.                                                                                             
            7. {question_guideline}
            
            Finally, please analyze the extent to which the given EXCERPT satisfies the following requirements. Your ANALYSIS should specify which requirements have been met and which ones have not been satisfied. 
            The requirements outline the necessary components for high-quality disclosure pertaining to the QUESTION. 
            
            REQUIREMENTS: {requirement}
            
            Your response to the question should be formatted in JSON with five keys:
            1. QUESTION: {question}
            2. ANSWER: Your answer to the question (be in a string format).
            3. EXCERPT: The sentences in the report from which you derive your answers to the question. 
            4. ANALYSIS: A paragraph of analysis. 
            5. SCORE: An integer score from 0 to 100. A score of 0 indicates that most of the REQUIREMENTS have not been met or are insufficiently detailed. 
            
            In contrast, a score of 100 suggests that the majority of the <REQUIREMENTS> have been met and are accompanied by specific details.
            
            Your FINAL_ANSWER in JSON (ensure there’s no format error):
            """
            
            reader = PdfReader(uploaded_file_path)
            article_text = ["""SUSTAINABILITY_REPORT
                <DOC>
                """]
            
            for page in reader.pages:
                article_text.append(page.extract_text())
            article_text.append("""</DOC>""")
            article_text = "\n\n".join(article_text)
            
            prompt = f"{HUMAN_PROMPT} {article_text+sustainability_query} {AI_PROMPT}"
            
            return prompt
        else:
            pass

    @st.cache_data
    def get_trustability_score(_self, uploaded_report_path, selected_company):

        # Read the questions from csv

        csv_path = "standards/questions.csv"

        file_obj = open(csv_path, 'r')
        reader = csv.reader(file_obj)

        sustainability_inputs = []
        for item in reader:
            if reader.line_num == 1:  # skipping the header
                continue
            sustainability_inputs.append(item)

        trustability_score = 0
        num_sustainability_questions = 4
        cnt = 0
        st.write(f"Calculating trustability score...")
        for line in sustainability_inputs:
            question = line[0]
            question_guideline = line[1]
            requirement = line[2]


            completion = _self.model.completions.create(
                model="claude-2",
                max_tokens_to_sample=400000,
                prompt=_self.generate_prompt_for_trustability_score(uploaded_report_path, question, question_guideline, requirement, selected_company),
            )
            answer = json.loads(_self.find_json_in_response(completion.completion))
            trustability_score += answer["SCORE"]
            cnt += 1
            st.write(f"{25*cnt}% complete")

        # Obtain a final average sustainability score across IFRS Recommendation categories
        trustability_score /= num_sustainability_questions

        # Scale the 1-100 score to 1-5
        final_score = trustability_score / 20

        return final_score

    
    def find_json_in_response(_self, response_text):
        stack = []
        start_bracket_found = False
        start_index = None
        end_index = None
        index = 0

        while True:
            if response_text[index] == '{':
                stack.append('{')
                if not start_bracket_found:
                    start_bracket_found = True
                    start_index = index
            elif response_text[index] == '}':
                stack.pop()
            if len(stack) == 0 and start_bracket_found:
                end_index = index + 1
                return response_text[start_index:end_index]
            index += 1
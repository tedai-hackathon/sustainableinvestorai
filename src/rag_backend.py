#### 
# Author: Aycan Katitas 
# Description: RAG Implementation - Comparing multiple documents
# Date: 10/09/2023
####

import os
from os.path import join
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="langchain")

from PyPDF2 import PdfReader
from langchain import OpenAI
from langchain.document_loaders import PyPDFLoader
from llama_index import SimpleDirectoryReader, ServiceContext, VectorStoreIndex
from llama_index.query_engine import SubQuestionQueryEngine
from llama_index.tools import ToolMetadata
from llama_index.tools.query_engine import QueryEngineTool
from llama_index import set_global_service_context
from dotenv import load_dotenv 
from langchain.chat_models import ChatOpenAI
import streamlit as st

@st.cache_resource
class RAGBackend:
    def __init__(self):
        self.reports_dir_path = "reports/"
        self.all_company_names = next(os.walk(self.reports_dir_path))[1]
        report_filenames = {
            "SHELL": "shell-sr-2022.pdf",
            "BP": "bp-sr-2022.pdf",
            "TOTAL": "total-sr-2022.pdf",
            "MARATHON": "marathon-sr-2022.pdf",
            "APPLE": "APPLE.pdf",
            "ADIDAS": "adidas_1-3_sustainability_progress_report.pdf",
            "ABBOTT": "Abbott.pdf"
        }
        self.all_report_paths = {company_name: self.reports_dir_path + company_name + "/" + report_filename for company_name, report_filename in report_filenames.items()}

        self.query_engine_tools = {}

        load_dotenv()
        llm = OpenAI(temperature=0, model_name="gpt-4", max_tokens=-1)
        #llm = ChatOpenAI(temperature=0, model_name="gpt-4", max_tokens=-1)

        service_context = ServiceContext.from_defaults(llm=llm)
        set_global_service_context(service_context=service_context)
    
    
    def create_query_engine_tools_for_question(self, company_names_to_compare):
        required_query_engine_tools = []
        for company_name in company_names_to_compare:
            if company_name not in self.query_engine_tools:
                st.info(f"Creating vector query engine for {company_name}...")
                company_docs = self.prepare_doc(company_name)
                company_index = self.prepare_vector_index(company_name, company_docs)
                self.query_engine_tools[company_name] = self.prepare_query_engine_tool(company_name, company_index)
            else:
                st.info(f"Retrieving already created vector query engine for {company_name}...")
            
            required_query_engine_tools.append(self.query_engine_tools[company_name])
        
        return required_query_engine_tools


    def ask_question(self, question, company_names_to_compare):
        comparison_question = f"Compare and contrast the companies {', '.join(company_names_to_compare)} with respect to the following question: {question}"
        print()
        print("COMPARISON QUESTION:", comparison_question)
        required_query_engine_tools = self.create_query_engine_tools_for_question(company_names_to_compare)

        self.overall_query_engine = SubQuestionQueryEngine.from_defaults(query_engine_tools=required_query_engine_tools)

        comparison_response = self.overall_query_engine.query(comparison_question)
        print("ANSWER:", str(comparison_response), end="\n\n")

        return str(comparison_response)
                
    
    def prepare_doc(self, company_name):

        ## STEP 1 - Document Loader
        # Using Llamaindex 
        
        metadata_fn = lambda filename: {'file_name': filename.split("/")[-1]}
        company_report_path = self.all_report_paths[company_name]
        company_docs = SimpleDirectoryReader(
            input_files=[company_report_path],
            file_metadata=metadata_fn,
            filename_as_id=True).load_data()
        print(f'Loaded {company_name} sustainability report with {len(company_docs)} pages')
        
        return company_docs


    def prepare_vector_index(self, company_name, company_docs):

        ## STEP 2 - Data Indexing 
        # Split document into chunks 
        # Embed each chunk 
        # Store chunks in a vector store 

        company_index = VectorStoreIndex.from_documents(company_docs)
        print(f'Prepared vector index for {company_name}.')
        
        return company_index


    def prepare_query_engine_tool(self, company_name, company_index):
        ## STEP 3 - Generate the query engine

        company_query_engine = company_index.as_query_engine(similarity_top_k=5)

        company_query_engine_tool = QueryEngineTool(
                query_engine=company_query_engine,
                metadata=ToolMetadata(
                    name=f"{company_name}_query_engine",
                    description=f"{company_name} sustainability report query engine",
                ),
            )
        print(f'Prepared query engine for {company_name}.')

        return company_query_engine_tool

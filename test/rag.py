#### 
# Author: Aycan Katitas 
# Description: RAG Implementation - Comparing multiple documents
# Date: 10/09/2023
####

import os
from os.path import join
import warnings

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

## Set API Keys 

load_dotenv()

## Ignore langchain import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="langchain")

openai_api_key = os.environ.get("OPENAI_API_KEY")
llm = OpenAI(temperature=0, model_name="text-davinci-003", max_tokens=-1)
#llm = ChatOpenAI(temperature=0, model_name="gpt-4", max_tokens=-1)

# Setting default llm to gpt-3
service_context = ServiceContext.from_defaults(llm=llm)
set_global_service_context(service_context=service_context)

### STEP1 - PARSING THE DOCUMENT

dir_path = "../reports/"
sh_uploaded_file_path = join(dir_path,"SHELL","shell-sr-2022.pdf")
bp_uploaded_file_path = join(dir_path,"BP","bp-sr-2022.pdf")

# Document Loader 
# try document loaders of pypdf2, langchain and llamaindex - see which is better

# reader = PdfReader(sh_uploaded_file_path)
# print(f"Sustainability report pages {len(reader.pages)}")
# article_text = []
# for page in reader.pages:
#     article_text.append(page.extract_text())

# Using Langchain document loader 
# loader = PyPDFLoader(sh_uploaded_file_path)
# pages = loader.load_and_split()
# print(pages[0])
# print(f"Loaded sustainability report with {len(pages)} but page number is indicated as normal")

# Using Llamaindex 

metadata_fn = lambda filename: {'file_name': filename.split("/")[-1]}

# Read Shell's sustainability report 
shell_docs = SimpleDirectoryReader(
    input_files=[sh_uploaded_file_path],
    file_metadata=metadata_fn,
    filename_as_id=True).load_data()
print(f'Loaded Shell sustainability report with {len(shell_docs)} pages')

# Read BP's sustainability report 
bp_docs = SimpleDirectoryReader(
    input_files=[bp_uploaded_file_path],
    file_metadata=metadata_fn,
    filename_as_id=True).load_data()
print(f'Loaded BP sustainability report with {len(bp_docs)} pages')

## STEP 2 - Data Indexing 
# Split document into chunks 
# Embed each chunk 
# store chunks in a vector store 
shell_index = VectorStoreIndex.from_documents(shell_docs)
bp_index = VectorStoreIndex.from_documents(bp_docs)

shell_engine = shell_index.as_query_engine(similarity_top_k=5)
bp_engine = bp_index.as_query_engine(similarity_top_k=5)

company1_question = "By which year does Shell plan to become a net-zero emission energy business?"
company2_question = "By which year does BP plan to become a net-zero emission energy business?"

response_shell = shell_engine.query(company1_question)
response_bp = bp_engine.query(company2_question)

# Showing chunks it created the answer on 
print("QUESTION 1 TO COMPANY 1:", company1_question)
print("ANSWER:", response_shell.response)
print()
print("QUESTION 2 TO COMPANY 2:", company1_question)
print("ANSWER:", response_bp.response)
# for node in response_bp.source_nodes:
#     print(node.node.extra_info)
#     print(node.get_content())

query_engine_tools = [
    QueryEngineTool(
        query_engine=shell_engine,
        metadata=ToolMetadata(
            name="shell_query_engine",
            description="Shell sustainability report query engine",
        ),
    ),
    QueryEngineTool(
        query_engine=bp_engine,
        metadata=ToolMetadata(
            name="bp_query_engine",
            description="BP sustainability report query engine",
        ),
    ),
]

overall_query_engine = SubQuestionQueryEngine.from_defaults(query_engine_tools=query_engine_tools)
comparison_question = "Compare and contrast Shell and BP's target years to become net-zero emission energy businesses."
print()
print("COMPARISON QUESTION:", comparison_question)
comparison_response = overall_query_engine.query(comparison_question)
print("ANSWER:", str(comparison_response))






#pp = "/Users/aycankatitas/Desktop/Git/gaifinanceeconhackathon/reports/SHELL/"
#df = SimpleDirectoryReader(input_dir=pp, file_metadata=filename_fn,filename_as_id=True).load_data()








# Document Splitting - split the document into chunks 

### STEP 2 - EMBED THE DOCUMENT 

# Turn words into numerical representation

### STEP 3 - ANSWER GENERATION 

# Retrieve relevant chunks - by cosine similarity or KNN 

# Generate an answer 
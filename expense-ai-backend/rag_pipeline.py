from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate

# 1. Load and Split
loader = PyPDFLoader("../data/document.pdf")
chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100).split_documents(loader.load())

# 2. Vector Store
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=OllamaEmbeddings(model="llama3"),
    persist_directory="./chroma_db"
)

# 3. RAG Chain
llm = OllamaLLM(model="llama3")
retriever = vectorstore.as_retriever()

template = """Use the following pieces of context to answer the question at the end.

{context}

Question: {question}

Helpful Answer:"""

custom_rag_prompt = ChatPromptTemplate.from_template(template)

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | custom_rag_prompt
    | llm
)

print(rag_chain.invoke("Summarize this document."))
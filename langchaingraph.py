import bs4
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain_ollama import OllamaEmbeddings
from langchain.chat_models import init_chat_model
from langchain_core.vectorstores import InMemoryVectorStore
import getpass
import os

os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = ""

llm = init_chat_model("llama3", model_provider="ollama")
embeddings = OllamaEmbeddings(model="llama3")
vector_store = InMemoryVectorStore(embeddings)



# Load and chunk contents of the blog
loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs=dict(
        parse_only=bs4.SoupStrainer(
            class_=("post-content", "post-title", "post-header")
        )
    ),
)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True,)
all_splits = text_splitter.split_documents(docs)

# Index chunks
total_documents = len(all_splits)
third = total_documents // 3

for i, document in enumerate(all_splits):
    if i < third:
        document.metadata["section"] = "beginning"
    elif i < 2 * third:
        document.metadata["section"] = "middle"
    else:
        document.metadata["section"] = "end"
_ = vector_store.add_documents(documents=all_splits)

# Define prompt for question-answering
prompt = hub.pull("rlm/rag-prompt")


# class Search(TypedDict):
#     """Search query."""

#     query: Annotated[str, ..., "Search query to run."]
#     section: Annotated[
#         Literal["beginning", "middle", "end"],
#         ...,
#         "Section to query.",
#     ]
    
class State(TypedDict):
    question: str
    # query: Search
    context: List[Document]
    answer: str


# def analyze_query(state: State):
#     structured_llm = llm.with_structured_output(Search)
#     query = structured_llm.invoke(state["question"])
#     return {"query": query}

def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}

def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}

graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()
print('generate graph')

def get_graph():
    return graph
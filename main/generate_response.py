from langchain.chat_models import ChatOpenAI
from gptcache import Cache
from gptcache.manager.factory import manager_factory
from gptcache.processor.pre import get_prompt
from langchain.cache import GPTCache
import langchain
import hashlib
import os
from langchain.vectorstores.pinecone import Pinecone
from dotenv import load_dotenv
from langchain import PromptTemplate, LLMChain
import pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA

PINECONE_API_KEY = "d4dfa428-c7a3-4ea6-a858-35ccd0485943"
PINECONE_ENV = "us-west1-gcp-free"
OPENAI_API_KEY = "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"
PINECONE_INDEX_NAME = "chatbot"
PINECONE_NAMESPACE = "vector-data"


def get_hashed_name(name):
    return hashlib.sha256(name.encode()).hexdigest()


def init_gptcache(cache_obj: Cache, llm: str):
    hashed_llm = get_hashed_name(llm)
    cache_obj.init(
        pre_embedding_func=get_prompt,
        data_manager=manager_factory(
            manager="map", data_dir=f"map/map_cache_{hashed_llm}"),
    )


def generate_message(query, history, behavior, temp, chat):
    # load_dotenv()

    template = """{behavior}

    Training data: {examples}

    Chathistory: {history}
    Human: {human_input}
    Assistant:"""

    prompt = PromptTemplate(
        input_variables=["history", "examples", "human_input", "behavior"], template=template)

    langchain.llm_cache = GPTCache(init_gptcache)
    llm = ChatOpenAI(model_name="gpt-3.5-turbo",
                      temperature=temp,
                      openai_api_key=OPENAI_API_KEY)

    conversation = LLMChain(
        llm=llm,
        verbose=True,
        prompt=prompt
    )
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    docsearch = Pinecone.from_existing_index(
        index_name=PINECONE_INDEX_NAME, namespace = PINECONE_NAMESPACE, embedding=embeddings)
    _query = query
    docs = docsearch.similarity_search(query=_query, k=10)

    examples = ""
    for doc in docs:
        # if doc.metadata['chat'] == str(chat):
            doc.page_content = doc.page_content.replace('\n\n', ' ')
            examples += doc.page_content + '\n'

    response = conversation.run(
        human_input=query,
        history=history,
        behavior=behavior,
        examples=examples
    )

    return response


def generate_AI_message(query, history, behavior, temp):
    # load_dotenv()

    template = """ {behavior}

    {history}
    Human: {human_input}
    Assistant:"""

    prompt = PromptTemplate(
        input_variables=["history", "human_input", "behavior"], template=template)

    def get_hashed_name(name):
        return hashlib.sha256(name.encode()).hexdigest()

    def init_gptcache(cache_obj: Cache, llm: str):
        hashed_llm = get_hashed_name(llm)
        cache_obj.init(
            pre_embedding_func=get_prompt,
            data_manager=manager_factory(
                manager="map", data_dir=f"map/map_cache_{hashed_llm}"),
        )

    langchain.llm_cache = GPTCache(init_gptcache)
    llm = ChatOpenAI(model_name="gpt-3.5-turbo",
                      temperature=temp,
                      openai_api_key=OPENAI_API_KEY)

    conversation = LLMChain(
        llm=llm,
        verbose=True,
        prompt=prompt
    )

    response = conversation.run(
        human_input=query,
        history=history,
        behavior=behavior,
    )

    return response


def generate_Bubble_message(query):
    load_dotenv()

    template = "Generate a title for a fantasy animal, character or fairy in {query}. A title must two words, first is adjective and second is noun. Do not provide any explanations. Do not respond with anything except the output of the title."

    prompt = PromptTemplate(
        input_variables=["query"], template=template)

    def get_hashed_name(name):
        return hashlib.sha256(name.encode()).hexdigest()

    def init_gptcache(cache_obj: Cache, llm: str):
        hashed_llm = get_hashed_name(llm)
        cache_obj.init(
            pre_embedding_func=get_prompt,
            data_manager=manager_factory(
                manager="map", data_dir=f"map/map_cache_{hashed_llm}"),
        )

    langchain.llm_cache = GPTCache(init_gptcache)

    llm = ChatOpenAI(model_name="gpt-3.5-turbo",
                     temperature=1,
                     openai_api_key="")
    conversation = LLMChain(
        llm=llm,
        verbose=True,
        prompt=prompt
    )
    response = conversation.run(
        query=query
    )
    response = response.replace('"', '')
    return response

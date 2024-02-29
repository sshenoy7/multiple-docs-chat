import streamlit as st
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain_community.vectorstores import faiss
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from htmlTemplates import css, bot_template, user_template
import textract
import os
from docx import Document
import io
from chatWithDoc import get_conversation_chain, get_text_chunks, get_text_from_uploaded_documents, get_vectorstore
from chatWithWebsite import get_context_retriever_chain, get_conversational_rag_chain, get_vectorstore_from_url
from langchain_core.messages import AIMessage, HumanMessage
import json

def clear():
    st.session_state.uQuery = ''

def chat_with_documents(chat_option_form):
    with st.sidebar:
        uploaded_docs = st.file_uploader(
            "I can read books",
            accept_multiple_files=True
        )
        read_document = st.button("Read Book")
        if read_document:
            with st.spinner("Reading book..."):
                # get doc text
                raw_text = get_text_from_uploaded_documents(uploaded_docs)

                # get the text chunks
                text_chunks = get_text_chunks(raw_text)

                # create embeddings and store in vector database
                vectorstore = get_vectorstore(text_chunks)
                
                st.session_state.conversation = get_conversation_chain(vectorstore)
                st.write("Let your conversation begin...")
    

def chat_with_website():
    with st.sidebar:
        url_to_learn = st.text_input("I can learn from a website URL")
        read_website = st.button("Read Blog")
        if read_website:
            if url_to_learn:
                with st.spinner("Reading website..."):
                    if "vector_store" not in st.session_state:
                        st.session_state.vector_store = get_vectorstore_from_url(url_to_learn)
                    
                    st.session_state.retriever_chain = get_context_retriever_chain(st.session_state.vector_store)
                    st.session_state.conversation_rag_chain = get_conversational_rag_chain(st.session_state.retriever_chain)
                    
                    st.write("Let your conversation begin...")
        

def chat_with_database():
    with st.sidebar:
        st.write("Patience my dear friend. I am evolving!! :)")
    
def handle_user_input_for_doc(user_question):
    if user_question is not None:
        response = st.session_state.conversation({'question': user_question})
        st.session_state.chat_history = response['chat_history']

        for i, message in enumerate(st.session_state.chat_history):
            if i % 2 == 0:
                st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
            else:
                st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)

def handle_user_input_for_website(user_question):
    response = st.session_state.conversation_rag_chain.invoke({
        "chat_history": st.session_state.website_chat_history,
        "input": user_question
    })
    st.session_state.website_chat_history.append(HumanMessage(content=user_question))
    st.session_state.website_chat_history.append(AIMessage(content=response['answer']))

    for i, message in enumerate(st.session_state.website_chat_history):
        if i == 0:
            continue
        elif i % 2 == 1:
            st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)

def main():
    load_dotenv()
    st.set_page_config(page_title="Know your books", page_icon=":books:")
    st.write(css, unsafe_allow_html=True)
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    
    if "retriever_chain" not in st.session_state:
        st.session_state.retriever_chain = None
    
    if "conversation_rag_chain" not in st.session_state:
        st.session_state.conversation_rag_chain = None

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    
    if "website_chat_history" not in st.session_state:
        st.session_state.website_chat_history = [
            AIMessage(content="Hello, I am a bot. How can I help you?"),
        ]
    
    if "user_input" not in st.session_state:
        st.session_state.user_input = None

    st.header("Ask me anything you taught me!! :books:")
    user_question = st.chat_input("Your Query:")

    with st.sidebar:
        chat_option_form = st.form("chat_options")
        mode = chat_option_form.radio("What do you want to chat with?", ("Chat with Documents", "Chat with Website", "Chat with Database"))
        submitted = chat_option_form.form_submit_button("Let's Train!")
    
    if mode == "Chat with Documents":
        chat_with_documents(chat_option_form)
        if user_question:
            handle_user_input_for_doc(user_question)
    elif mode == "Chat with Website":
        chat_with_website()
        if user_question:
            handle_user_input_for_website(user_question)
    elif mode == "Chat with Database":
        chat_with_database()
    

if __name__ == "__main__":
    main()
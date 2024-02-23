import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain_community.vectorstores import faiss
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from htmlTemplates import bot_template, user_template



def get_text_from_uploaded_pdfs(uploaded_pdfs):
    text = ""
    for pdf in uploaded_pdfs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(raw_text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(raw_text)

    return chunks

def get_vectorstore(text_chunks):
    embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
    vectorstore = faiss.FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    
    return vectorstore

def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )

    return conversation_chain

def handle_user_input(user_question):
    if st.session_state.conversation is None:
        print('Whaatt??')
    
    if user_question is None:
        print('Ask something')

    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)

def main():
    load_dotenv()

    st.set_page_config(page_title="Know your books", page_icon=":books:")
    if "conversation" not in st.session_state:
        st.session_state.conversation = None

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    st.header("Ask me anything you taught me!! :books:")
    user_question = st.text_input("Ask Me:")

    if user_question:
        handle_user_input(user_question)
    st.write(user_template.replace("{{MSG}}", "Hello, robot!"), unsafe_allow_html=True)
    st.write(bot_template.replace("{{MSG}}", "Hello, Human!"), unsafe_allow_html=True)

    with st.sidebar:
        st.subheader("You've taught me these")
        uploaded_pdfs = st.file_uploader(
            "Teach me stuff",
            accept_multiple_files=True
        )
        if st.button("Learn"):
            with st.spinner("Processing..."):
                # get pdf text 
                raw_text = get_text_from_uploaded_pdfs(uploaded_pdfs)

                # get the text chunks
                text_chunks = get_text_chunks(raw_text)

                # create embeddings and store in vector database
                vectorstore = get_vectorstore(text_chunks)
                
                st.session_state.conversation = get_conversation_chain(vectorstore)
                st.write('Let the conversation begin...')



if __name__ == '__main__':
    main()
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

def get_text_from_uploaded_documents(uploaded_docs):
    text = ""
    for doc in uploaded_docs:
        _, ext = os.path.splitext(doc.name)
        try:
            text += extract_text_from_other(doc, ext)
        except Exception as e:
            print(f"Something went wrong while processing {doc}, falling back to extension-specific libraries. Error: {e}")
            if ext == ".pdf":
                text += extract_text_from_pdf(doc)
            elif ext == ".docx":
                text += extract_text_from_docx(doc)
            # elif ext == ".rtf":
            #     text += extract_text_from_rtf(doc)
    return text

## NOT Supported
# def extract_text_from_rtf(rtf_file):
#     # Read the RTF file and extract plain text
#     doc = rtf_file.read()

#     # Extract plain text
#     text = plain_text(doc)

#     return text

def extract_text_from_pdf(pdf_file):
    pdf_text = ""
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        pdf_text += page.extract_text()
    return pdf_text

def extract_text_from_docx(docx_file):
    docx_text = ""
    # Create a Document object from the content
    docx = Document(docx_file)
    # Extract text from the Document object
    for para in docx.paragraphs:
        docx_text += para.text + "\n"
    return docx_text

def extract_text_from_other(other_file, extension):
    if extension in [".rtf", ".docx", ".pdf"]:
        raise ValueError(f"{extension} is not fully-supported by textract")
    # Read the content of the uploaded file
    content = other_file.read()
    # Decode the content as UTF-8
    text = content.decode("utf-8")
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
    st.write(css, unsafe_allow_html=True)
    if "conversation" not in st.session_state:
        st.session_state.conversation = None

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    st.header("Ask me anything you taught me!! :books:")
    user_question = st.text_input("Your Query:")

    if user_question:
        handle_user_input(user_question)

    with st.sidebar:
        st.subheader("You've taught me these")
        uploaded_docs = st.file_uploader(
            "Teach me stuff",
            accept_multiple_files=True
        )
        if st.button("Learn"):
            with st.spinner("Processing..."):
                # get doc text
                raw_text = get_text_from_uploaded_documents(uploaded_docs)

                # get the text chunks
                text_chunks = get_text_chunks(raw_text)

                # create embeddings and store in vector database
                vectorstore = get_vectorstore(text_chunks)
                
                st.session_state.conversation = get_conversation_chain(vectorstore)
                st.write("Let your conversation begin...")



if __name__ == '__main__':
    main()
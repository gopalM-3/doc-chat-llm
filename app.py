import streamlit as st
from pypdf import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.llms.huggingface_hub import HuggingFaceHub
from templates import *
from dotenv import load_dotenv


def extract_text(docs):
    extracted_text = ''
    for doc in docs:
        reader = PdfReader(doc)
        for page in reader.pages:
            extracted_text += page.extract_text()

    return extracted_text


def get_chunks(raw_text):
    text_splitter = CharacterTextSplitter(
        separator='\n',
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )

    chunks = text_splitter.split_text(raw_text)

    return chunks


def get_vector_store(chunks):
    embeddings = HuggingFaceInstructEmbeddings(model_name='hkunlp/instructor-xl')
    vector_store = FAISS.from_text(text=chunks, embeddings=embeddings)

    return vector_store


def initiate_convo(vector_store):
    llm = HuggingFaceHub(
        repo_id='google/flan-t5-xxl',
        model_kwargs={
            'temperature': 0.5,
            'max_len': 512
        }
    )

    memory = ConversationBufferMemory(
        memory_key='chat_history',
        return_messages=True
    )

    convo_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriver(),
        memory=memory
    )

    return convo_chain


def handle_question(question):
    response = st.session_state.convo({'question': question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace('{{message}}', message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace('{{message}}', message.content), unsafe_allow_html=True)


def main():
    load_dotenv()

    st.set_page_config(page_title='Chat2PDF', page_icon=':page_facing_up:')

    st.write(CSS, unsafe_allow_html=True)

    if 'convo' not in st.session_state:
        st.session_state.convo = None

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = None

    st.header('Chat with multiple PDFs at once :page_facing_up:')
    st.write(bot_template.replace('{{message}}', 'Hello mortal!'), unsafe_allow_html=True)

    question = st.text_input('Ask away...')
    if question:
        handle_question(question)

    with st.sidebar:
        st.subheader('Your documents')
        st.text('i. Upload your PDFs\nii. Click on the \'Process\' button\niii. Shoot your questions!')
        docs = st.file_uploader('Drop your files here', accept_multiple_files=True)
        if st.button('Process'):
            with st.spinner('Cooking...'):
                # extracting the text from the doc
                raw_text = extract_text(docs)

                # create the text chunks
                text_chunks = get_chunks(raw_text)

                # creating the vector store
                vector_store = get_vector_store(text_chunks)

                # initiate conversation chain
                st.session_state.convo = initiate_convo(vector_store)


if __name__ == '__main__':
    main()

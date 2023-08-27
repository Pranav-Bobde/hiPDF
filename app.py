import streamlit as st
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from pdfminer.high_level import extract_text

def process_pdf(pdf):
    # set pdf name
    st.session_state["pdf_name"] = pdf.name[:-4]
    # extract text from pdf
    pdf_text = extract_text(pdf)
    # get texts/chunks from pdf
    texts = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
    ).split_text(pdf_text)
    # generate embeddings and vectorstore
    embeddings = OpenAIEmbeddings(openai_api_key=token)
    vectorstore = FAISS.from_texts(texts=texts, embedding=embeddings)
    st.session_state["vectorstore"] = vectorstore

def gen_response(question):
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, openai_api_key=token)
    vectorstore = st.session_state["vectorstore"]

    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())
    res = qa_chain({"query": question})
    return res["result"]

def display_messages():
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

def reset_chat():
    content = f"Welcome to the PDF - '{st.session_state['pdf_name']}'. Feel free to ask any questions. 🤗"
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": content,
        }
    ]

st.set_page_config(page_title="🤗💬 PDF Chat App", initial_sidebar_state="expanded")

hide_streamlit_style = """
<style>
footer {
    visibility: hidden;
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

with st.sidebar:
    st.title("hi PDF 📕")
    st.markdown(
        """
        ## About
        This is a FREE PDF chat app powered by OpenAI.
        - You can upload any pdf file
        - You can chat and ask questions about the PDF
        """
    )

    def isValidToken(token):
        return token.startswith("sk-") and len(token) == 51

    if "OPENAI_API_KEY" in st.secrets and isValidToken(st.secrets["OPENAI_API_KEY"]):
        st.success("Api key already provided!", icon="✅")
        token = st.secrets["OPENAI_API_KEY"]
    else:
        token = st.text_input(
            "Enter your OpenAI Key", type="password")
        if not isValidToken(token):
            st.warning("Please enter a valid Api Key!", icon="⚠️")
        else:
            st.success("Api key received successfully!", icon="✅")

    st.button('Clear Chat History', on_click=reset_chat)

pdf = st.file_uploader("Upload a PDF file", type=["pdf"], disabled=not token)
if not pdf:
    st.warning("Please upload a pdf file.", icon="⚠️")
else:
    # if new pdf uploaded
    if pdf.name[:-4] != st.session_state.get("pdf_name", ""):
        with st.spinner("Processing..."):
            process_pdf(pdf)
        reset_chat()

    # display messages
    display_messages()

    # if same pdf 
    # get user input
    if question := st.chat_input(disabled=not (token and pdf)):
        # add user input to messages
        st.session_state["messages"].append(
            {
                "role": "user",
                "content": question,
            }
        )
        st.chat_message("user").write(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # get response from openai
                response = gen_response(question)

                # add response to messages
                st.session_state["messages"].append(
                    {
                        "role": "assistant",
                        "content": response,
                    }
                )
                st.write(response)


import streamlit as st

def gen_pdf_summary():
    return "This is a summary of the pdf file."

def display_messages():
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

def reset_chat():
    content = f"Welcome to the PDF {st.session_state['pdf_name']}. \n {st.session_state['pdf_summary']}"
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

    st.markdown(
        """
        Made with ❤️ by [Pranav Bobde](https://github.com/Pranav-Bobde)
        """
    )

pdf = st.file_uploader("Upload a PDF file", type=["pdf"])
if not pdf:
    st.warning("Please upload a pdf file.", icon="⚠️")
else:
    # if new pdf uploaded
    if pdf.name[:-4] != st.session_state.get("pdf_name", ""):
        # set pdf name
        st.session_state["pdf_name"] = pdf.name[:-4]
        # set pdf summary
        pdf_summary = gen_pdf_summary()
        st.session_state["pdf_summary"] = pdf_summary
        reset_chat()

    # display messages
    display_messages()

    # if same pdf 
    # get user input
    if question := st.chat_input(disabled=not pdf):
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
                response = "This is a response from openai."

                # add response to messages
                st.session_state["messages"].append(
                    {
                        "role": "assistant",
                        "content": response,
                    }
                )
                st.write(response)


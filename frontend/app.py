
import streamlit as st
import requests

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="AI-Powered Document Intelligence Assistant",
    page_icon="📘",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000"

# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>
.main {
    background-color: #f7f9fc;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.hero {
    padding: 25px;
    border-radius: 15px;
    background: linear-gradient(120deg, #14213d, #2457a7);
    color: white;
    margin-bottom: 25px;
}

.hero h1 {
    color: white;
    font-size: 30px;
}

.hero p {
    color: #e5eaf5;
    font-size: 15px;
}

.answer-box {
    background-color: #ffffff;
    padding: 22px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
}

.source-tag {
    display: inline-block;
    background-color: #e8f0fe;
    color: #174ea6;
    padding: 7px 12px;
    border-radius: 8px;
    margin: 4px;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)


# ---------------- SESSION STATE ----------------

if "uploaded" not in st.session_state:
    st.session_state.uploaded = False

if "filename" not in st.session_state:
    st.session_state.filename = ""

if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------------- HEADER ----------------

st.markdown("""
<div class="hero">
    <h1>📘 AI-Powered Document Intelligence Assistant</h1>
    <p>
        AI-powered document understanding using Semantic Search,
        FAISS and Large Language Models.
    </p>
</div>
""", unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.title("⚙️ Workspace")

    st.markdown("### Document Status")

    if st.session_state.uploaded:
        st.success("Document Ready")
        st.caption(st.session_state.filename)
    else:
        st.warning("No document uploaded")

    st.divider()

    

   

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ---------------- DOCUMENT UPLOAD ----------------

st.header("1. Upload Engineering Document")

col1, col2 = st.columns([2, 1])

with col1:

    uploaded_file = st.file_uploader(
        "Choose your PDF document",
        type=["pdf"]
    )

    if st.button("Upload & Process Document", type="primary"):

        if uploaded_file is None:
            st.warning("Please select a PDF first.")

        else:

            with st.spinner("Extracting text and creating document embeddings..."):

                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/pdf"
                    )
                }

                try:

                    response = requests.post(
                        f"{API_URL}/upload",
                        files=files,
                        timeout=180
                    )

                    if response.status_code == 200:

                        data = response.json()

                        st.session_state.uploaded = True
                        st.session_state.filename = data["filename"]
                        st.session_state.messages = []

                        st.success("Document processed successfully!")

                        metric1, metric2 = st.columns(2)

                        metric1.metric(
                            "Total Pages",
                            data["total_pages"]
                        )

                        metric2.metric(
                            "Text Chunks",
                            data["total_chunks"]
                        )

                    else:
                        st.error(response.text)

                except requests.RequestException as error:
                    st.error(f"Backend connection error: {error}")


with col2:

    st.info(
        "Upload a PDF to extract its content, "
        "generate embeddings and enable AI-powered questions."
    )


st.divider()


# ---------------- QUESTION ANSWERING ----------------

st.header("2. Ask Questions")

st.write(
    "Ask questions about the uploaded document "
    "and receive AI-generated answers with source references."
)


# Display previous conversation

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant" and message.get("sources"):

            st.caption("Source Pages")

            for page in message["sources"]:
                st.markdown(
                    f'<span class="source-tag">📄 Page {page}</span>',
                    unsafe_allow_html=True
                )


# Chat input

question = st.chat_input(
    "Ask something about your document..."
)

if question:

    if not st.session_state.uploaded:

        st.warning("Please upload a PDF document first.")

    else:

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):

            with st.spinner("Searching document and generating AI answer..."):

                try:

                    response = requests.get(
                        f"{API_URL}/ask",
                        params={"question": question},
                        timeout=120
                    )

                    if response.status_code == 200:

                        data = response.json()

                        answer = data["answer"]
                        sources = data.get("sources", [])

                        st.markdown(answer)

                        if sources:

                            st.caption("Source Pages")

                            for page in sources:

                                st.markdown(
                                    f'<span class="source-tag">📄 Page {page}</span>',
                                    unsafe_allow_html=True
                                )

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources
                        })

                    else:

                        error_message = response.text
                        st.error(error_message)

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"Error: {error_message}",
                            "sources": []
                        })

                except requests.RequestException as error:

                    st.error(f"Backend connection error: {error}")

import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_community.tools.tavily_search import TavilySearchResults

# Load Keys
load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

if not google_api_key or not tavily_api_key:
    st.error("⚠️ Error: Keys not found. Please check your .env file.")
    st.stop()

# Configure Google API
genai.configure(api_key=google_api_key)

# Page Setup (Clean & Simple UI)
st.set_page_config(
    page_title="Telecom Assistant",
    page_icon="📡",
    layout="centered", 
    initial_sidebar_state="expanded"
)

# Custom Styling 
st.markdown("""
<style>
    .stChatMessage {border-radius: 10px; margin-bottom: 10px;}
    .main-title {font-size: 2.5rem; font-weight: 700; color: #4F8BF9; text-align: center;}
    .sub-text {text-align: center; color: #666;}
</style>
""", unsafe_allow_html=True)

# Sidebar Design (For Context & Reset)
with st.sidebar:
    st.header("📡 Telecom Assistant")
    st.markdown("---")
    st.markdown("**What can I help with?**")
    st.markdown("- 📶 Data Packages")
    st.markdown("- 🏠 Home Broadband")
    st.markdown("- 🛠️ Troubleshooting")
    st.markdown("- 📞 Hotlines")
    
    st.markdown("---")
    # Reset Button
    if st.button("🔄 Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.caption("Powered by Gemini Pro & LangChain")

# Logic Functions 
@st.cache_resource
def get_vector_store():
    data_folder = "data"
    
    if not os.path.exists(data_folder):
        st.error(f"Folder '{data_folder}' not found! Please create a 'data' folder.")
        return None
    
    documents = []
    try:
        for file in os.listdir(data_folder):
            if file.endswith(".pdf"):
                pdf_path = os.path.join(data_folder, file)
                loader = PyPDFLoader(pdf_path)
                documents.extend(loader.load())
        
        if not documents:
            st.error("No PDF files found in 'data' folder!")
            return None
            
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)
        
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
        return vectorstore
        
    except Exception as e:
        st.error(f"Error loading PDFs: {e}")
        return None

@st.cache_resource
def get_working_model_name():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name or 'pro' in m.name:
                    return m.name
        return 'models/gemini-1.5-flash'
    except:
        return 'models/gemini-pro'

def generate_answer(query, vector_store, chat_history):
    model_name = get_working_model_name()
    
    docs = vector_store.similarity_search(query, k=3)
    context_text = "\n\n".join([doc.page_content for doc in docs])

    pdf_prompt = f"""
    You are a polite and helpful Customer Support Agent for a Sri Lankan Telecommunications Company.
    
    Context from Guides:
    {context_text}
    
    Customer Question: {query}
    
    Instructions:
    1. Be friendly and concise.
    2. If the user asks for a price/code, give exact details from the text.
    3. If the answer is NOT in the context, reply exactly "NOT_FOUND".
    """
    
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(pdf_prompt)
        answer = response.text
    except Exception as e:
        try:
            model = genai.GenerativeModel('models/gemini-1.0-pro')
            response = model.generate_content(pdf_prompt)
            answer = response.text
        except:
            return f"System Error: {e}"

    if "NOT_FOUND" in answer:
        status_msg = st.empty()
        status_msg.info("🔍 Checking online sources...")
        
        try:
            tavily = TavilySearchResults(max_results=3)
            web_results = tavily.invoke(query)
            
            web_prompt = f"""
            You are a Telecom Support Agent. The internal document didn't have the answer, so use these web search results.
            
            Web Results: {web_results}
            Question: {query}
            
            Answer helpfully and summarize the best options.
            """
            
            response = model.generate_content(web_prompt)
            final_answer = response.text
            status_msg.empty() 
            return final_answer
            
        except Exception as e:
            return f"I couldn't find that information in our guides or online."
    
    else:
        return answer

# app interface 

# Header
st.markdown('<div class="main-title">📡 Telecom Support Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Ask me about Data Packages, Routers, and Services</div>', unsafe_allow_html=True)
st.write("") # Spacer

# Load Database
vector_store = get_vector_store()

if vector_store:
    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "ai", "content": "Hello! 👋 I can help you find the best data packages or fix router issues. What do you need today?"}
        ]

    # Display Chat History with Avatars
    for msg in st.session_state.messages:
        # Select Avatar based on role
        avatar = "📡" if msg["role"] == "ai" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])

    # User Input Handling
    if user_input := st.chat_input("Type your question here..."):
        # Display User Message
        st.chat_message("human", avatar="👤").write(user_input)
        st.session_state.messages.append({"role": "human", "content": user_input})
        
        # Generate and Display AI Response
        with st.chat_message("ai", avatar="📡"):
            with st.spinner("Thinking..."):
                response_text = generate_answer(user_input, vector_store, st.session_state.messages)
                st.write(response_text)
                st.session_state.messages.append({"role": "ai", "content": response_text})
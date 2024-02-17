import random
import shutil
import string
import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
from hugchat import hugchat
from hugchat.login import Login
import asyncio
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
from langchain.text_splitter import CharacterTextSplitter
from promptTemplate import prompt4conversation, prompt4Context
from promptTemplate import prompt4conversationInternet
# FOR DEVELOPMENT NEW PLUGIN 
# from promptTemplate import yourPLUGIN
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from HuggingChatAPI import HuggingChat
from langchain.embeddings import HuggingFaceHubEmbeddings
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from itertools import islice


hf = None
repo_id = "sentence-transformers/all-mpnet-base-v2"

if 'hf_token' in st.session_state:
    if 'hf' not in st.session_state:
        hf = HuggingFaceHubEmbeddings(
            repo_id=repo_id,
            task="feature-extraction",
            huggingfacehub_api_token=st.session_state['hf_token'],
        ) # type: ignore
        st.session_state['hf'] = hf

st.set_page_config(
    page_title="Talk with Webpages💬", page_icon="🤗", layout="wide", initial_sidebar_state="expanded"
)

st.markdown('<style>.css-w770g5{\
            width: 100%;}\
            .css-b3z5c9{    \
            width: 100%;}\
            .stButton>button{\
            width: 100%;}\
            .stDownloadButton>button{\
            width: 100%;}\
            </style>', unsafe_allow_html=True)


# Sidebar contents for logIN, choose plugin, and export chat
with st.sidebar:
    st.title('🤗💬 WebChat App')
    
    if 'hf_email' not in st.session_state or 'hf_pass' not in st.session_state:
        with st.expander("ℹ️ Login in Hugging Face", expanded=True):
            st.write("⚠️ You need to login in Hugging Face to use this app. You can register [here](https://huggingface.co/join).")
            st.header('Hugging Face Login')
            hf_email = st.text_input('Enter E-mail:')
            hf_pass = st.text_input('Enter password:', type='password')
            hf_token = st.text_input('Enter API Token:', type='password')
            if st.button('Login 🚀') and hf_email and hf_pass and hf_token: 
                with st.spinner('🚀 Logging in...'):
                    st.session_state['hf_email'] = hf_email
                    st.session_state['hf_pass'] = hf_pass
                    st.session_state['hf_token'] = hf_token

                    try:
                    
                        sign = Login(st.session_state['hf_email'], st.session_state['hf_pass'])
                        cookies = sign.login()
                        chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
                    except Exception as e:
                        st.error(e)
                        st.info("⚠️ Please check your credentials and try again.")
                        st.error("⚠️ dont abuse the API")
                        st.warning("⚠️ If you don't have an account, you can register [here](https://huggingface.co/join).")
                        from time import sleep
                        sleep(3)
                        del st.session_state['hf_email']
                        del st.session_state['hf_pass']
                        del st.session_state['hf_token']
                        st.experimental_rerun()

                    st.session_state['chatbot'] = chatbot

                    id = st.session_state['chatbot'].new_conversation()
                    st.session_state['chatbot'].change_conversation(id)

                    st.session_state['conversation'] = id
                    # Generate empty lists for generated and past.
                    ## generated stores AI generated responses
                    if 'generated' not in st.session_state:
                        st.session_state['generated'] = ["I'm **WebChat**, How may I help you ? "]
                    ## past stores User's questions
                    if 'past' not in st.session_state:
                        st.session_state['past'] = ['Hi!']

                    st.session_state['LLM'] =  HuggingChat(email=st.session_state['hf_email'], psw=st.session_state['hf_pass'])
                    
                    st.experimental_rerun()
                    

    else:
        with st.expander("ℹ️ Advanced Settings"):
            #temperature: Optional[float]. Default is 0.5
            #top_p: Optional[float]. Default is 0.95
            #repetition_penalty: Optional[float]. Default is 1.2
            #top_k: Optional[int]. Default is 50
            #max_new_tokens: Optional[int]. Default is 1024

            temperature = st.slider('🌡 Temperature', min_value=0.1, max_value=1.0, value=0.5, step=0.01)
            top_p = st.slider('💡 Top P', min_value=0.1, max_value=1.0, value=0.95, step=0.01)
            repetition_penalty = st.slider('🖌 Repetition Penalty', min_value=1.0, max_value=2.0, value=1.2, step=0.01)
            top_k = st.slider('❄️ Top K', min_value=1, max_value=100, value=50, step=1)
            max_new_tokens = st.slider('📝 Max New Tokens', min_value=1, max_value=1024, value=1024, step=1)
    

        # FOR DEVELOPMENT NEW PLUGIN YOU MUST ADD IT HERE INTO THE LIST 
        # YOU NEED ADD THE NAME AT 144 LINE

        #plugins for conversation
        plugins = ["🛑 No PLUGIN", "🌐 Web Search", "🔗 Talk with Website"]
        if 'plugin' not in st.session_state:
            st.session_state['plugin'] = st.selectbox('🔌 Plugins', plugins, index=0)
        else:
            if st.session_state['plugin'] == "🛑 No PLUGIN":
                st.session_state['plugin'] = st.selectbox('🔌 Plugins', plugins, index=plugins.index(st.session_state['plugin']))


# FOR DEVELOPMENT NEW PLUGIN FOLLOW THIS TEMPLATE
# PLUGIN TEMPLATE
# if st.session_state['plugin'] == "🔌 PLUGIN NAME" and 'PLUGIN NAME' not in st.session_state:
#     # PLUGIN SETTINGS
#     with st.expander("🔌 PLUGIN NAME Settings", expanded=True):
#         if 'PLUGIN NAME' not in st.session_state or st.session_state['PLUGIN NAME'] == False:
#             # PLUGIN CODE
#             st.session_state['PLUGIN NAME'] = True
#         elif st.session_state['PLUGIN NAME'] == True:
#             # PLUGIN CODE
#             if st.button('🔌 Disable PLUGIN NAME'):
#               st.session_state['plugin'] = "🛑 No PLUGIN"
#               st.session_state['PLUGIN NAME'] = False
#               del ALL SESSION STATE VARIABLES RELATED TO PLUGIN
#               st.experimental_rerun()
#       # PLUGIN UPLOADER
#       if st.session_state['PLUGIN NAME'] == True:
#           with st.expander("🔌 PLUGIN NAME Uploader", expanded=True):
#               # PLUGIN UPLOADER CODE
#               load file
#               if load file and st.button('🔌 Upload PLUGIN NAME'):
#                   qa = RetrievalQA.from_chain_type(llm=st.session_state['LLM'], chain_type='stuff', retriever=retriever, return_source_documents=True)
#                   st.session_state['PLUGIN DB'] = qa
#                   st.experimental_rerun()
# 



# WEB SEARCH PLUGIN
        if st.session_state['plugin'] == "🌐 Web Search" and 'web_search' not in st.session_state:
            # web search settings
            with st.expander("🌐 Web Search Settings", expanded=True):
                if 'web_search' not in st.session_state or st.session_state['web_search'] == False:
                    reg = ['us-en', 'uk-en', 'it-it']
                    sf = ['on', 'moderate', 'off']
                    tl = ['d', 'w', 'm', 'y']
                    if 'region' not in st.session_state:
                        st.session_state['region'] = st.selectbox('🗺 Region', reg, index=1)
                    else:
                        st.session_state['region'] = st.selectbox('🗺 Region', reg, index=reg.index(st.session_state['region']))
                    if 'safesearch' not in st.session_state:
                        st.session_state['safesearch'] = st.selectbox('🚨 Safe Search', sf, index=1)
                    else:
                        st.session_state['safesearch'] = st.selectbox('🚨 Safe Search', sf, index=sf.index(st.session_state['safesearch']))
                    if 'timelimit' not in st.session_state:
                        st.session_state['timelimit'] = st.selectbox('📅 Time Limit', tl, index=1)
                    else:
                        st.session_state['timelimit'] = st.selectbox('📅 Time Limit', tl, index=tl.index(st.session_state['timelimit']))
                    if 'max_results' not in st.session_state:
                        st.session_state['max_results'] = st.slider('📊 Max Results', min_value=1, max_value=5, value=2, step=1)
                    else:
                        st.session_state['max_results'] = st.slider('📊 Max Results', min_value=1, max_value=5, value=st.session_state['max_results'], step=1)
                    if st.button('🌐 Save change'):
                        st.session_state['web_search'] = "True"
                        st.experimental_rerun()

        elif st.session_state['plugin'] == "🌐 Web Search" and st.session_state['web_search'] == 'True':
            with st.expander("🌐 Web Search Settings", expanded=True):
                st.write('🚀 Web Search is enabled')
                st.write('🗺 Region: ', st.session_state['region'])
                st.write('🚨 Safe Search: ', st.session_state['safesearch'])
                st.write('📅 Time Limit: ', st.session_state['timelimit'])
                if st.button('🌐🛑 Disable Web Search'):
                    del st.session_state['web_search']
                    del st.session_state['region']
                    del st.session_state['safesearch']
                    del st.session_state['timelimit']
                    del st.session_state['max_results']
                    del st.session_state['plugin']
                    st.experimental_rerun()

# WEBSITE PLUGIN
        if st.session_state['plugin'] == "🔗 Talk with Website" and 'web_sites' not in st.session_state:
            with st.expander("🔗 Talk with Website", expanded=True):
                web_url = st.text_area("🔗 Enter a website URLs , one for each line")
                if web_url is not None and st.button('🔗✅ Add website to context'):
                    if web_url != "":
                        text = []
                        #max 10 websites
                        with st.spinner('🔗 Extracting TEXT from Websites ...'):
                            for url in web_url.split("\n")[:10]:
                                page = requests.get(url)
                                soup = BeautifulSoup(page.content, 'html.parser')
                                text.append(soup.get_text())
                            # creating a vectorstore

                        with st.spinner('🔗 Creating Vectorstore...'):
                            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
                            texts = text_splitter.create_documents(text)
                            # Select embeddings
                            embeddings = st.session_state['hf']
                            # Create a vectorstore from documents
                            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                            db = Chroma.from_documents(texts, embeddings, persist_directory="./chroma_db_" + random_str)
                        
                        with st.spinner('🔗 Saving Vectorstore...'):
                            # save vectorstore
                            db.persist()
                            #create .zip file of directory to download
                            shutil.make_archive("./chroma_db_" + random_str, 'zip', "./chroma_db_" + random_str)
                            # save in session state and download
                            st.session_state['db'] = "./chroma_db_" + random_str + ".zip" 
                        
                        with st.spinner('🔗 Creating QA chain...'):
                            # Create retriever interface
                            retriever = db.as_retriever()
                            # Create QA chain
                            qa = RetrievalQA.from_chain_type(llm=st.session_state['LLM'], chain_type='stuff', retriever=retriever, return_source_documents=True)
                            st.session_state['web_sites'] = qa
                            st.session_state['web_text'] = text
                        st.experimental_rerun()
        
        if st.session_state['plugin'] == "🔗 Talk with Website":
            if 'db' in st.session_state:
                # leave ./ from name for download
                file_name = st.session_state['db'][2:]
                st.download_button(
                    label="📩 Download vectorstore",
                    data=open(file_name, 'rb').read(),
                    file_name=file_name,
                    mime='application/zip'
                )

            if st.button('🛑🔗 Remove Website from context'):
                if 'web_sites' in st.session_state:
                    del st.session_state['db']
                    del st.session_state['web_sites']
                    del st.session_state['web_text']
                del st.session_state['plugin']
                st.experimental_rerun()

# END OF PLUGIN
    add_vertical_space(4)
    if 'hf_email' in st.session_state:
        if st.button('🗑 Logout'):
            keys = list(st.session_state.keys())
            for key in keys:
                del st.session_state[key]
            st.experimental_rerun()

##### End of sidebar


# User input
# Layout of input/response containers
input_container = st.container()
response_container = st.container()
data_view_container = st.container()
loading_container = st.container()



## Applying the user input box
#with input_container:
input_text = st.chat_input("🧑‍💻 Write here 👇", key="input")

with data_view_container:
    if 'web_text' in st.session_state:
        with st.expander("🤖 View the **Website content**"):
            st.write(st.session_state['web_text'])

# Response output
## Function for taking user prompt as input followed by producing AI generated responses
def generate_response(prompt):
    final_prompt =  ""
    make_better = True
    source = ""

    with loading_container:

        # FOR DEVELOPMENT PLUGIN
        # if st.session_state['plugin'] == "🔌 PLUGIN NAME" and 'PLUGIN DB' in st.session_state:
        #     with st.spinner('🚀 Using PLUGIN NAME...'):
        #         solution = st.session_state['PLUGIN DB']({"query": prompt})
        #         final_prompt = YourCustomPrompt(prompt, context)
        
        if st.session_state['plugin'] == "🔗 Talk with Website" and 'web_sites' in st.session_state:
            #get only last message
            context = f"User: {st.session_state['past'][-1]}\nBot: {st.session_state['generated'][-1]}\n"
            with st.spinner('🚀 Using tool to get information...'):
                result = st.session_state['web_sites']({"query": prompt})
                solution = result["result"]
                if len(solution.split()) > 110:
                    make_better = False
                    final_prompt = solution
                    if 'source_documents' in result and len(result["source_documents"]) > 0:
                        final_prompt += "\n\n✅Source:\n" 
                        for d in result["source_documents"]:
                            final_prompt += "- " + str(d) + "\n"
                else:
                    final_prompt = prompt4Context(prompt, context, solution)
                    if 'source_documents' in result and len(result["source_documents"]) > 0:
                        source += "\n\n✅Source:\n"
                        for d in result["source_documents"]:
                            source += "- " + str(d) + "\n"
    
        else:
            #get last message if exists
            if len(st.session_state['past']) == 1:
                context = f"User: {st.session_state['past'][-1]}\nBot: {st.session_state['generated'][-1]}\n"
            else:
                context = f"User: {st.session_state['past'][-2]}\nBot: {st.session_state['generated'][-2]}\nUser: {st.session_state['past'][-1]}\nBot: {st.session_state['generated'][-1]}\n"
            
            if 'web_search' in st.session_state:
                if st.session_state['web_search'] == "True":
                    with st.spinner('🚀 Using internet to get information...'):
                        internet_result = ""
                        internet_answer = ""
                        with DDGS() as ddgs:
                            ddgs_gen = ddgs.text(prompt, region=st.session_state['region'], safesearch=st.session_state['safesearch'], timelimit=st.session_state['timelimit'])
                            for r in islice(ddgs_gen, st.session_state['max_results']):
                                internet_result += str(r) + "\n\n"
                            fast_answer = ddgs.answers(prompt)
                            for r in islice(fast_answer, 2):
                                internet_answer += str(r) + "\n\n"

                        final_prompt = prompt4conversationInternet(prompt, context, internet_result, internet_answer)
                else:
                    final_prompt = prompt4conversation(prompt, context)
            else:
                final_prompt = prompt4conversation(prompt, context)

        if make_better:
            with st.spinner('🚀 Generating response...'):
                print(final_prompt)
                response = st.session_state['chatbot'].chat(final_prompt, temperature=temperature, top_p=top_p, repetition_penalty=repetition_penalty, top_k=top_k, max_new_tokens=max_new_tokens)
                response += source
        else:
            print(final_prompt)
            response = final_prompt

    return response

## Conditional display of AI generated responses as a function of user provided prompts
with response_container:
    if input_text and 'hf_email' in st.session_state and 'hf_pass' in st.session_state:
        response = generate_response(input_text)
        st.session_state.past.append(input_text)
        st.session_state.generated.append(response)
    

    #print message in normal order, frist user then bot
    if 'generated' in st.session_state:
        if st.session_state['generated']:
            for i in range(len(st.session_state['generated'])):
                with st.chat_message(name="user"):
                    st.markdown(st.session_state['past'][i])
                
                with st.chat_message(name="assistant"):
                    if len(st.session_state['generated'][i].split("✅Source:")) > 1:
                        source = st.session_state['generated'][i].split("✅Source:")[1]
                        mess = st.session_state['generated'][i].split("✅Source:")[0]

                        st.markdown(mess)
                        with st.expander("📚 Source of message number " + str(i+1)):
                            st.markdown(source)

                    else:
                        st.markdown(st.session_state['generated'][i])

            st.markdown('', unsafe_allow_html=True)
            
            
    else:
        st.info("👋 Hey , we are very happy to see you here 🤗")
        st.info("👉 Please Login to continue, click on top left corner to login 🚀")
        st.error("👉 If you are not registered on Hugging Face, please register first and then login 🤗")
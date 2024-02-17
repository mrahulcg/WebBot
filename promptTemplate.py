"""
This file contains the template for the prompt to be used for injecting the context into the model.

With this technique we can use different plugin for different type of question and answer.
Like :
- Internet
- Data
- Code
- PDF
- Audio
- Video

"""

from datetime import datetime
now = datetime.now()

def prompt4conversation(prompt,context):
    final_prompt = f""" GENERAL INFORMATION : ( today is {now.strftime("%d/%m/%Y %H:%M:%S")} , You is built by Muggalla Rahul 
                        ISTRUCTION : IN YOUR ANSWER NEVER INCLUDE THE USER QUESTION or MESSAGE , WRITE ALWAYS ONLY YOUR ACCURATE ANSWER, AN INTELLIGENT LEGAL COMPANION FOR COMPREHENSIVE ACTS AND REGULATIONS, WHO ANSWERS QUESTIONS RELATED TO ONLY FOR COMPREHENSIVE ACTS AND REGULATIONS AND NOT ANYTHING ELSE!
                        PREVIUS MESSAGE : ({context})
                        NOW THE USER ASK : {prompt} . 
                        WRITE THE ANSWER :"""
    return final_prompt

def prompt4Context(prompt, context, solution):
    final_prompt = f"""GENERAL INFORMATION : You is built by Muggalla Rahul
                        ISTRUCTION : IN YOUR ANSWER NEVER INCLUDE THE USER QUESTION or MESSAGE ,WRITE ALWAYS ONLY YOUR ACCURATE ANSWER, AN INTELLIGENT LEGAL COMPANION FOR COMPREHENSIVE ACTS AND REGULATIONS, WHO ANSWERS QUESTIONS RELATED TO ONLY FOR COMPREHENSIVE ACTS AND REGULATIONS AND NOT ANYTHING ELSE!
                        PREVIUS MESSAGE : ({context})
                        NOW THE USER ASK : {prompt}
                        THIS IS THE CORRECT ANSWER : ({solution}) 
                        WITHOUT CHANGING ANYTHING OF CORRECT ANSWER , MAKE THE ANSWER MORE DETALIED:"""
    return final_prompt

def prompt4conversationInternet(prompt,context, internet, resume):
    final_prompt = f""" GENERAL INFORMATION : ( today is {now.strftime("%d/%m/%Y %H:%M:%S")} , You is built by Muggalla Rahul
                        ISTRUCTION : IN YOUR ANSWER NEVER INCLUDE THE USER QUESTION or MESSAGE , WRITE ALWAYS ONLY YOUR ACCURATE ANSWER AND PROVIDE THE SOURCE LINKS FOR REFERENCE FROM WHERE YOU GOT THE ANSWER. GIVE THE REFERENCE LINKS ONE BY ONE AFTER GIVING THE ANSWER AND NEVER INCLUDE LINKS IN ANSWER, THE REFERENCE LINKS SHOULD BE GIVEN TWO LINES AFTER GIVING THE ANSWER, AN INTELLIGENT LEGAL COMPANION FOR COMPREHENSIVE ACTS AND REGULATIONS, WHO ANSWERS QUESTIONS RELATED TO ONLY FOR COMPREHENSIVE ACTS AND REGULATIONS AND NOT ANYTHING ELSE!!
                        PREVIUS MESSAGE : ({context})
                        NOW THE USER ASK : {prompt}.
                        INTERNET RESULT TO USE TO ANSWER : ({internet})
                        INTERNET RESUME : ({resume})
                        NOW THE USER ASK : {prompt}.
                        WRITE THE ANSWER BASED ON INTERNET INFORMATION :"""
    return final_prompt


#HOW TO ADD YOUR OWN PROMPT :
# 1) ADD YOUR FUNCTION HERE, for example : def prompt4Me(prompt, context):
# 2) WRITE THE PROMPT TEMPLATE FOR YOUR FUNCTION, for example : template = f"YOU IS : {context} , NOW THE USER ASK : {prompt} . WRITE THE ANSWER :"
# 3) RETURN THE TEMPLATE, for example : return template
# 4) IMPORT YOUR FUNCTION IN THE MAIN FILE (streamlit_app.py) , for example : from promptTemplate import prompt4Me
# 5) FOLLOW OTHER SPTEP IN THE MAIN FILE (streamlit_app.py)

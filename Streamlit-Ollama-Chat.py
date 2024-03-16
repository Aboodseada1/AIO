import os
import streamlit as st
from langchain_community.llms import Ollama

def main():
    st.title('🦜🔗 Chat With Website')
    st.subheader('Input your website URL, ask questions, and receive answers directly from the website.')

    prompt = st.text_input("Ask a question (query/prompt)")
    if st.button("Submit Query", type="primary"):
        try:
            # Use a Mistral model from Ollama
            llm = Ollama(model="mistral")
            
            # Run the prompt and return the response
            response = llm.invoke(prompt)

            
            # Display the response
            st.write(response)
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == '__main__':
    main()

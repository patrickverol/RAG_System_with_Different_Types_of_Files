"""
Web Application
This module implements the Streamlit web interface for the RAG system.
It provides a user-friendly interface for querying documents and viewing results.
"""

# Import regular expression module
import re

# Import Streamlit for web interface
import streamlit as st

# Import HTTP request handling
import requests

# Import JSON handling
import json

# Import time for performance measurement
import time

# Import environment variables handling
import os

# Filter warnings
import warnings
warnings.filterwarnings('ignore')

# Import evaluation and feedback modules
from llm import gera_documento_id, captura_user_input, captura_user_feedback

# Import storage module
from storage import get_storage


def main():
    """
    Main function to run the Streamlit application.
    Handles user interface, document queries, and feedback collection.
    """
    
    # Configure Streamlit page
    st.set_page_config(page_title="RAG Project", page_icon=":100:", layout="wide")

    # Set application title
    st.title('🤖 RAG Project')
    st.title('🔍 Search Engine with Generative AI and RAG')

    # Sidebar with instructions
    st.sidebar.title("Instructions")
    st.sidebar.markdown("""
    ### How to Use the App:
    - Type a question in the text input field.
    - Click on the "Send" button.
    - View the answer and the documents used to answer the question.
    - Click on the "Satisfied" button if you are satisfied with the answer.
    - Click on the "Not Satisfied" button if you are not satisfied with the answer.
    - Click on the "Download" button to download the document.

    ### Available files:
    - PDF
    - DOCX
    - DOC
    - TXT
    - PPTX
    - PPT

    ### Purpose:
    This application provides a search engine for documents. You can search for documents by typing a question in the text input field. Download the document to view the reference content.
    """)

    # Support button in sidebar
    if st.sidebar.button("Support"):
        st.sidebar.write("For any questions, please contact: patrickverol@gmail.com")


    # Configure storage
    storage_config = {
        'storage_type': 'http',
        'base_url': 'http://document_storage:8080'
    }
    
    # Add S3 specific configurations if needed
    if storage_config['storage_type'] == 's3':
        storage_config.update({
            'bucket_name': os.getenv('S3_BUCKET_NAME'),
            'region_name': os.getenv('AWS_REGION'),
            'endpoint_url': os.getenv('S3_ENDPOINT_URL')
        })
    # Add HTTP base URL if needed
    elif storage_config['storage_type'] == 'http':
        print(f"Using document storage URL: {storage_config['base_url']}")  # Debug log

    # Initialize storage
    storage = get_storage(**storage_config)
    
    # Only print base_url for HTTP storage
    if storage_config['storage_type'] == 'http':
        print(f"Using document storage URL: {storage.base_url}")

    # Initialize session state variables
    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'docId' not in st.session_state:
        st.session_state.docId = None
    if 'userInput' not in st.session_state:
        st.session_state.userInput = ""
    if 'feedbackSubmitted' not in st.session_state:
        st.session_state.feedbackSubmitted = False

    # Create text input for questions with a default example
    question = st.text_input(
        "Type a question to execute a query on the documents:",
        value="What is a broker?",
        help="Example questions: 'What is a stock?', 'What are the key investment strategies?'"
    )

    # Check if "Send" button was clicked
    if st.button("Send"):
        if not question:
            st.warning("Type your question to continue.")
            return
            
        # Display the question
        st.write("The question was: \"", question+"\"")
        
        # Define API URL
        url = "http://backend:8000/rag_api"

        # Create JSON payload
        payload = json.dumps({"query": question})
        
        # Set request headers
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

        # Make POST request to API
        start_time = time.time()  # Start time measurement
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)
            
            # Debug information
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Headers: {response.headers}")
            print(f"Response Content: {response.text[:200]}...")  # Print first 200 chars of response
            
            # Check if response is empty
            if not response.text:
                st.error("The API returned an empty response. Check the backend.")
                return
                
            # Try to parse JSON
            try:
                response_data = json.loads(response.text)
            except json.JSONDecodeError as e:
                st.error(f"Error decoding JSON response: {str(e)}")
                print(f"Received response: {response.text}")
                return
                
            end_time = time.time()    # End time measurement
            responseTime = round(end_time - start_time, 2)  # Calculate response time

            # Get API response and extract answer text
            answer = response_data.get("answer")
            if not answer:
                st.error("The API response does not contain the 'answer' field")
                return
                
            score = response_data.get("score", 1.0)  # Get response score, default to 1.0 if not present

            # Compile regex to find document references
            rege = re.compile("\[Document\ [0-9]+\]|\[[0-9]+\]")
            
            # Find all document references in response
            m = rege.findall(answer)
            print(f"Found document references: {m}")  # Debug log

            # Initialize list for document numbers
            num = []
            
            # Extract document numbers from references
            for n in m:
                num = num + [int(s) for s in re.findall(r'\b\d+\b', n)]
            print(f"Extracted document numbers: {num}")  # Debug log

            # Display answer using markdown
            st.markdown(answer)
            
            # Get documents from response context
            documents = response_data.get('context', [])
            print(f"Documents from context: {documents}")  # Debug log
            
            # Initialize list for documents to display
            show_docs = []
            
            # Add documents matching extracted numbers to show_docs
            for n in num:
                for doc in documents:
                    if int(doc['id']) == n:
                        # Ensure the document path is relative to the documents directory
                        if doc['path'].startswith('/'):
                            doc['path'] = doc['path'][1:]  # Remove leading slash
                        show_docs.append(doc)
            print(f"Documents to show: {show_docs}")  # Debug log
            
            # Initialize variable for download button identifiers
            dsa_id = 10231718414897291

            # Display expanded documents with download buttons
            for doc in show_docs:
                # Create expander for each document
                with st.expander(str(doc['id'])+" - "+doc['path']):
                    # Display document content
                    st.write(doc['content'])
                    
                    # Get document URL from storage
                    try:
                        # Ensure the document path is relative and properly formatted
                        doc_path = doc['path'].lstrip('/')
                        print(f"Getting URL for document path: {doc_path}")
                        doc_url = storage.get_document_url(doc_path)
                        print(f"Generated URL: {doc_url}")
                        
                        # Get document content
                        temp_file = storage.get_document(doc_path)
                        print(f"Successfully retrieved document content")
                        
                        # Read the file content in binary mode
                        with open(temp_file, 'rb') as f:
                            doc_content = f.read()
                        
                        # Determine MIME type based on file extension
                        file_ext = os.path.splitext(doc_path)[1].lower()
                        mime_type = {
                            '.pdf': 'application/pdf',
                            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                            '.doc': 'application/msword',
                            '.txt': 'text/plain',
                            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                            '.ppt': 'application/vnd.ms-powerpoint'
                        }.get(file_ext, 'application/octet-stream')
                        
                        # Create download button with proper MIME type
                        st.download_button(
                            label=f"Download {os.path.basename(doc_path)}",
                            data=doc_content,
                            file_name=os.path.basename(doc_path),
                            mime=mime_type
                        )
                        
                        # Clean up temporary file
                        os.unlink(temp_file)
                        
                    except Exception as e:
                        print(f"Error downloading {doc_path}: {str(e)}")
                        st.error(f"Error downloading document: {str(e)}")

            # Add evaluation and feedback
            try:
                # Generate document ID
                docId = gera_documento_id(question, answer)
                
                # Capture user input
                captura_user_input(
                    docId,
                    question.replace("'", ""), 
                    answer, 
                    score,  # Use score from API
                    responseTime,  # Use calculated response time
                )

                # Update session state
                st.session_state.result = answer
                st.session_state.docId = docId
                st.session_state.userInput = question.replace("'", "")
                st.session_state.feedbackSubmitted = False

            except Exception as e:
                print(e)
                st.error("Error processing the evaluation. Check the Qdrant and try again.")

        except requests.exceptions.RequestException as e:
            st.error(f"Error in the API request: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")

    # Display query result and feedback outside the "Send" button block
    if st.session_state.result:
        # Satisfaction feedback section
        if not st.session_state.feedbackSubmitted:
            st.write("Are you satisfied with the answer?")
            feedback_col1, feedback_col2 = st.columns(2)
            with feedback_col1:
                if st.button("Satisfied"):
                    captura_user_feedback(st.session_state.docId, st.session_state.userInput, st.session_state.result, True)
                    st.session_state.feedbackSubmitted = True
                    st.success("Feedback registered: Satisfied")
            with feedback_col2:
                if st.button("Not Satisfied"):
                    captura_user_feedback(st.session_state.docId, st.session_state.userInput, st.session_state.result, False)
                    st.session_state.feedbackSubmitted = True
                    st.warning("Feedback registered: Not Satisfied")


if __name__ == "__main__":
    main()
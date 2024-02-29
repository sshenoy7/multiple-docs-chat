import streamlit as st

def main():
    st.sidebar.title("Sidebar")
    
    # Initialize session state variables
    if 'show_file_uploader' not in st.session_state:
        st.session_state.show_file_uploader = False
    if 'show_learn_button' not in st.session_state:
        st.session_state.show_learn_button = False
        
    with st.sidebar.form(key='my_form'):
        st.write("Select an option:")
        option = st.radio("", ["Option 1", "Option 2", "Option 3"])
        submit_button = st.form_submit_button("Submit")
        
        if option == "Option 1" and submit_button:
            # Show file uploader and "Learn" button if Option 1 is selected
            st.session_state.show_file_uploader = True
            st.session_state.show_learn_button = True
    
    # Place file uploader and "Learn" button below the form
    if st.session_state.show_file_uploader:
        uploaded_file = st.sidebar.file_uploader("Upload a file")
        if uploaded_file:
            st.sidebar.write("File uploaded successfully!")
            
    if st.session_state.show_learn_button:
        learn_button_clicked = st.sidebar.button("Learn")
        if learn_button_clicked:
            st.sidebar.write("Learning...")
        
if __name__ == "__main__":
    main()

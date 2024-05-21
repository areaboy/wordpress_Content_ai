import streamlit as st
import replicate
import os
import requests
import json
import streamlit.components.v1 as components
from streamlit.components.v1 import html



st.header("Wordpress Content Creator AI")
st.write("Helping Wordpress Content Creators to easily **create/generate** Posts contents and automatically post it to their respective Wordpress Sites....")
st.info(" You can ask Arctic AI to  **generate any Contents, Informations, Programmatical Codes, Histories, Posts & much more.....**")


if "event_result" not in st.session_state:
    st.session_state.event_result = ""
    st.write(st.session_state.event_result)

# Replicate and Wordpress API Credentials
with st.sidebar:
    st.title('Snowflake Arctic & Wordpress API Settings')
    if 'REPLICATE_API_TOKEN' in st.secrets:
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
        
    else:
        replicate_api = st.text_input('Enter Replicate API token:', type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
            st.warning('Please enter your Replicate API token.')
            st.markdown("**Don't have an API token?** Head over to [Replicate](https://replicate.com) to sign up for one.")

    os.environ['REPLICATE_API_TOKEN'] = replicate_api

    wordpress_login_id = st.text_input('Enter Wordpress Admin Login ID/Email:')
    
    wordpress_site_url = st.text_input('Enter Wordpress Site URL (Eg. https://mywordpress_site.com ):')
    
    wordpress_user_app_password = st.text_input('Enter Wordpress User App Password:', type='password')
    st.warning('**User app password** can be created via **wordpress admin**. On Wordpress Admin page,Go to **User** --> **Profile**  scroll down the Profile page --> **Application Passwords**. Enter any name you want to save your Apps Password with at --> **New Application Password Name** form input and click on **Add New Application Password** Button  **(Password Format eg yubY x8Ui nbcv lCgx yred xbnq)** ')



    # os.environ['REPLICATE_API_TOKEN'] = replicate_api
    st.subheader("Adjust model parameters")
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.3, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)


# Pass Form data to be posted to Wordpress in a Session State
# if st.session_state.event_result != "":
   # data_session = st.text_input('.', st.session_state.event_result)

   


# Post Data to Wordpress Rest API
def process_data_wordpress(wordpress_post_title): 
 
   if wordpress_login_id == "":  
        st.error(f"Wordpress Login ID cannot be empty....")
   elif wordpress_user_app_password == "":  
        st.error(f"Wordpress User App Password cannot be empty....")
   elif wordpress_site_url == "":  
        st.error(f"Wordpress Site URL cannot be empty....")

    
   else:
      with st.spinner("please wait. Posting to Wordpress Site...."): 
        wp_post_url = wordpress_site_url + "/wp-json/wp/v2/posts"       
        headers = {
        'Accept': 'application/json',
        # Already added when you pass json=
        # 'Content-Type': 'application/json',
        }

        json_data = {
        "title": wordpress_post_title,
        "content": st.session_state.event_result,
        "comment_status": "closed",
        "status": "draft"
        }

        response = requests.post(wp_post_url, headers=headers, json=json_data, auth=(wordpress_login_id, wordpress_user_app_password))
        # print("Server Response" ,response)
        # st.info(response)
        # st.info(response.status_code)
        data = response.json() 
        if response.status_code == 201: 
            st.success("Data Successfully Send to Wordpress....")
            html_string = '''

        <script language="javascript">
          alert('Data Successfully Send to Wordpress....');
        </script>
        '''
        components.html(html_string)



def clear_response_history():
    st.session_state.event_result =''

t_prompt_data= st.text_area('Enter Prompt: (Eg. Ask ARCTIC AI to generate any Contents.)' )
def process_data(): 
 os.environ['REPLICATE_API_TOKEN'] = replicate_api
 if replicate_api =='':
     st.markdown("**Replicate API token is empty**")
 elif wordpress_login_id == "":  
        st.error(f"Wordpress Login ID cannot be empty....")
 elif wordpress_user_app_password == "":  
        st.error(f"Wordpress User App Password cannot be empty....")
 elif wordpress_site_url == "":  
        st.error(f"Wordpress Site URL cannot be empty....")
    
 else:
   
    # with st.spinner("please wait....."):      
    query = []
    for event in replicate.stream(
    "snowflake/snowflake-arctic-instruct",
    input={
        "top_k": 50,
        "top_p": top_p,
        "prompt": t_prompt_data,
        "temperature": temperature,
        "max_new_tokens": 512,
        "min_new_tokens": 0,
        "stop_sequences": "<|im_end|>",
        "prompt_template": "<|im_start|>system\nYou're a helpful assistant<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n\n<|im_start|>assistant\n",
        "presence_penalty": 1.15,
        "frequency_penalty": 0.2
    },
    ):
    
       # st.write(str(event), end="")
       # print(str(event), end="")
       query.append(event.data)
 

    for res in query:
     # st.success(id)
     result_query = "".join(query)
     # result_query = "\n".join(query)
    st.session_state.event_result = result_query
    st.markdown(f"Question/Prompt: **{t_prompt_data}** ")
    st.success(f"Arctic AI Response: {st.session_state.event_result} ")
 

    # Update the session_state with the event result
    st.session_state.event_result = result_query
 
    st.subheader("Post To Your Wordpress Site...")
    
    wordpress_post_title = st.text_input('Enter Wordpress Post Title', t_prompt_data)
    st.button('Post on Wordpress As Draft', on_click=process_data_wordpress, args=[wordpress_post_title])
    st.button('Clear AI Response', on_click=clear_response_history)


st.button('Generate Content', on_click=process_data)


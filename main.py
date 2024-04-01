import requests
import json
import llmCalls
import streamlit as st

from collections import Counter


# OAuth details
def get_access_token():
    token_url = "https://test.api.ipaustralia.gov.au/public/external-token-api/v1/access_token"
    client_id = "yxiwJi97i0uovRanXopKmeKVVVWHekdq"
    client_secret = "FGpr0TT760VZQowop3t1UeDJdyzYSRdF3V67KfCJpLf2H5Ab4FNkUeCOBEitWKjd"

    # Prepare the auth credentials
    auth = (client_id, client_secret)

    # Prepare the data payload for the token request
    payload = {
        "grant_type": "client_credentials"
    }

    # Request the access token
    response = requests.post(token_url, auth=auth, data=payload)

    # Check if the token request was successful
    if response.ok:
        # Extract the access token
        access_token = response.json().get("access_token")
        print("Access token obtained successfully.")
        return access_token
    else:
        print("Failed to obtain access token. Status code:", response.status_code)
        return None

def search_patents(access_token, generated_keywords):
    # Prepare the header with the obtained access token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"  # Assuming the API expects JSON content
    }

    # The URL for the search API
    search_url = 'https://test.api.ipaustralia.gov.au/public/australian-patent-search-api/v1/search/quick'

    # The search body as a dictionary (to be converted to JSON)
    base_body = {
        "searchType": "ID",
        "sort": {
            "field": "APPLICATION_NUMBER",
            "direction": "DESC"
        },
        "pageSize": 1,
        "pageNumber": 1,
        "searchMode": "QUICK_ABSTRACT"
    }

    # Store the responses in a list
    responses = []

    # Make the authenticated request to the search API for each keyword
    for keyword in generated_keywords:
        # Update the query in the body for the current keyword
        body = base_body.copy()
        body['query'] = keyword

        # Make the request and get the response
        response = requests.post(search_url, headers=headers, data=json.dumps(body))

        # Parse the response JSON and get the 'results' list
        try:
            results = response.json().get('results', [])
        except json.JSONDecodeError:
            print("The response could not be parsed as JSON.")
            continue

        # If there are more than 20 results, keep only the first 20
        if len(results) > 20:
            results = results[:20]

        # Store the modified results list in the responses list
        responses.append(results)

    return responses

def get_ordered_numbers(responses):
    # Initialize a Counter object
    counter = Counter()

    # Iterate over the responses
    for results in responses:
        # Update the counter with the results
        counter.update(results)

    # Get the numbers in the order of most to least common
    ordered_numbers = [number for number, count in counter.most_common()]

    return ordered_numbers

def get_specific_responses(access_token, ordered_numbers):
    # Prepare the header with the obtained access token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"  # Assuming the API expects JSON content
    }

    # Store the responses in a dictionary
    specific_responses = {}

    # The URL for the specific search API
    specific_search_url = 'https://test.api.ipaustralia.gov.au/public/australian-patent-search-api/v1//patent/{}'

    # Make the authenticated request to the specific search API for each number
    for number in ordered_numbers:
        # Format the URL with the current number
        url = specific_search_url.format(number)

        # Make the request and store the response
        response = requests.get(url, headers=headers)

        # Parse the response text as JSON
        try:
            response_json = json.loads(response.text)
        except json.JSONDecodeError:
            print(f"The response for number {number} could not be parsed as JSON.")
            continue

        # Store the response JSON in the specific_responses dictionary with the number as the key
        specific_responses[number] = response_json

    return specific_responses

def truncate_responses(specific_responses, ordered_numbers):
    # Store the final responses in a dictionary
    truncated_specific_responses = {}

    # Set the number of responses to process
    n = 5

    # Iterate over the first n numbers in the ordered_numbers list
    for number in ordered_numbers[:n]:
        # Get the response for the current number
        response = specific_responses.get(number)

        # Check if the first item in 'publishedDocuments' is None
        published_document = response["publishedDocuments"][0]
        if published_document is None:
            continue

        # Get the 'claimsText' and 'abstractText' parts and truncate them to the first 250 words
        patent_title = response['bibliographicData']['inventionTitle'][0]['title']
        claims_text = response["publishedDocuments"][0].get("claimsText", "")
        abstract_text = response["publishedDocuments"][0].get("abstractText", "")
        claims_text = ' '.join(claims_text.split()[:250])
        abstract_text = ' '.join(abstract_text.split()[:250])

        # Store the truncated parts in the truncated_specific_responses dictionary with the number as the key
        truncated_specific_responses[number] = {
            'title': patent_title,
            'claimsText': claims_text,
            'abstractText': abstract_text
        }
    # print("-------------------")
    # print("Truncated Specific Responses")
    # print(truncated_specific_responses)
    # print("-------------------")
    return truncated_specific_responses

def write_analysis(truncated_specific_responses):
    # Initialize an empty string to store the analysis
    analysis = ""

    # Iterate over the truncated_specific_responses dictionary
    for number, response in truncated_specific_responses.items():
        # Add the number to the analysis string
        analysis += f"Patent Number: {number}\n"

        # Add the 'Title' part to the analysis string
        analysis += "Title:\n"
        analysis += f"{response['title']}\n"
        analysis += "--------------------\n"

        # Add the 'claimsText' part to the analysis string
        analysis += "Claims Text:\n"
        analysis += f"{response['claimsText']}\n"
        analysis += "--------------------\n"

        # Add the 'abstractText' part to the analysis string
        analysis += "Abstract Text:\n"
        analysis += f"{response['abstractText']}\n"
        analysis += "--------------------\n"

    # Write the analysis string to a file
    with open('analysis.txt', 'w', encoding='utf-8') as f:
        f.write(analysis)

def run_analysis():
    access_token = get_access_token()
    if access_token:
        generated_keywords = llmCalls.get_keyword_analysis()['keywords']
        responses = search_patents(access_token, generated_keywords)
        print("-------------------")
        print(responses)
        print("-------------------")

        ordered_numbers = get_ordered_numbers(responses)
        specific_responses = get_specific_responses(access_token, ordered_numbers)
        truncated_specific_responses = truncate_responses(specific_responses, ordered_numbers)
        write_analysis(truncated_specific_responses)
        final_analysis = llmCalls.final_analysis()
        print(final_analysis)
        return final_analysis

#_______________________________________________________________________________________________________________________
# Streamlit
st.title("Patent Attorney")
st.write("This application takes in potential patent ideas and checks for disputes and infringement with existing patents.")

# Add instructions for user in streamlit
st.write("Please enter your patent's descriptive title:")
st.write("Example: *Water Purification System Utilizing UV-C LED Photocatalytic Disinfection*")

# User input for patent title
patent_title = st.text_input("Patent Title", max_chars=250)

# User input for patent abstract
st.write("Please enter your patent's abstract. Make sure to include EXACTLY what you are patenting. Dont be afraid of technical terms. **More specifics = better output.**")
patent_abstract = st.text_area("Patent Abstract", max_chars=5000)

patent_context = patent_title + " " + patent_abstract

# Submit button
submit_button = st.button("Submit")

# Check if both inputs are provided and submit button is pressed
if patent_title and patent_abstract and submit_button:
    # Write the patent_context to a .txt file
    with open('patent_context.txt', 'w') as f:
        f.write(patent_context)

    # Run the analysis
    final_output = run_analysis()
    st.title("Output")
    st.write(final_output)

else:
    st.write("Please provide both the patent title and abstract and click the submit button to run the analysis.")

#_______________________________________________________________________________________________________________________




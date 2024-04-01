import prompts
import json
# from langchain_openai import ChatOpenAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
from openai import OpenAI


from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

def get_patent_context():
   # Read the patent_context from the .txt file
  with open('patent_context.txt', 'r') as f:
    patent_context = f.read()

  context = patent_context
  return context

def get_keyword_analysis():

  context = get_patent_context()
  keyword_system_message = prompts.keyword_system_message
  keyword_prompt = prompts.generate_keyword_prompt(context)

  response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    temperature=0.3,
    response_format={"type": "json_object"},
    messages=[
      {"role": "system", "content": keyword_system_message},
      {"role": "user", "content": keyword_prompt}
    ]
  )
  try:
    json_data = json.loads(response.choices[0].message.content)
    print(json_data)
  except json.JSONDecodeError:
    print("The response could not be parsed as JSON.")
  return json_data


def final_analysis():
    context = get_patent_context()
    analysis_system_message = prompts.analysis_system_message(context)
    analysis_prompt = prompts.generate_analysis_prompt()
    response = client.chat.completions.create(
      model="gpt-4-turbo-preview",
      temperature=0.3,
      response_format={ "type": "json_object" },
      messages=[
        {"role": "system", "content": analysis_system_message},
        {"role": "user", "content": analysis_prompt}
      ]
  )
    try:
      analysis_output = json.loads(response.choices[0].message.content)
      print(analysis_output)
            # Start formatting the Markdown text
      markdown_output = "# Current Patent Analysis\n\n"

      # Iterate through each patent in the analysis
      for patent in analysis_output["CURRENT_PATENTS_Analysis"]:
          patent_number = patent['Patent_Number']
          markdown_output += f"## Patent Number: [{patent_number}](https://ipsearch.ipaustralia.gov.au/patents/{patent_number})\n"
          markdown_output += f"- **Description**: {patent['Description']}\n"
          markdown_output += f"- **Relevance to Context**: {patent['Relevance_to_CONTEXT']}\n\n"

      # Adding the Conclusion section
      markdown_output += "## Conclusion\n"
      conclusion = analysis_output["Conclusion"]
      markdown_output += f"- **Closest Match**: {conclusion['Closest_Match']}\n"
      markdown_output += f"- **No Match**: {conclusion['No_Match']}\n"
      markdown_output += f"- **Potential Overlap**: {conclusion['Potential_Overlap']}\n"

    except json.JSONDecodeError:
      print("The response could not be parsed as JSON.")
    
    return markdown_output

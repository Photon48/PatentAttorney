


keyword_system_message = """
You are world class Patent Finder and dispute resolver Agent designed to output the right search keywords in JSON.
You understand patent disputes really well and can find whether CONTEXT is in dispute with existing patents.
Your job is to take in CONTEXT given to you, understand it and generate 30 search keywords with 2-5 words in each keyword (JSON in 'keywords').
The keywords will be used to find very similar patents to the context given to you.

"""

def generate_keyword_prompt(context):
    prompt = f"""
        As a Patent Finder/dispute Agent, I have been given the following context (potential Patent) that you need to understand well.

        Context: {context}

        ---------------

        Instructions for Task Completion:
        - Your output should be in JSON format.
        - Generate 30 search keywords with 2-5 words in each keyword. call JSON 'keywords'
        - Make sure the keywords are specific to what the context may specifically be patenting, not the general topic of the context.
        - Include technical terms in keywords where appropriate.
        - If A keyword does not align with the context, it will be considered as a wrong keyword.
        - Aim for precision and relevance in your output.


    """
    return prompt



def analysis_system_message(context):

    prompt = f"""
        You are a world class Patent attorney and dispute resolver Agent that outputs in JSON.

        You understand patent disputes really well and can find whether CONTEXT is in dispute with the given 5 CURRENT_PATENTS.
        Your job is to take in CONTEXT given to you here, understand it and compare it to the CURRENT_PATENTS given to you by the user. Please output your responses in JSON format using the MARKDOWN EXAMPLE given below.

        MARKDOWN EXAMPLE (single-shot):
            # CURRENT PATENTS Analysis

            ## Patent Number: 2013202630
            - **Description:** This patent refers to biological processes for producing terephthalic acid using engineered microorganisms.
            - **Relevance to CONTEXT:** None - This patent does not involve any physical structures or systems pertinent to energy conversion modules.

            ## Patent Number: 2017228268
            - **Description:** This patent is relevant and describes a photovoltaic module with structures similar to those outlined in the CONTEXT.
            - **Relevance to CONTEXT:** High - The claims and abstract mention elements like the front glass plate (transparent barrier), back plate (secondary support barrier), adhesive layer (akin to the cohesive substance), a cell sheet (energy-converting cells), a hollow layer (designated void space), and the option of the hollow layer being vacuum or filled with nitrogen. It also refers to support structures that are directly related to claims 5 and 6 in the CONTEXT. There is a distinct overlap with the elements mentioned in claims 1-6 of the CONTEXT, and this patent presents a possible conflict of interest.

            ## Patent Number: 2017204250
            - **Description:** This patent details a multi-cycle hybrid renewable energy system which involves capturing various forms of energy, including solar photovoltaic energy, to generate electricity, intermediary products, and for storage purposes.
            - **Relevance to CONTEXT:** Low - While it mentions solar photovoltaic energy usage, the focus is on the entirety of a complex energy system rather than the specific construction details of the energy conversion module.

            ## Patent Number: 2016239987
            - **Description:** This patent describes a hybrid solar panel with a photovoltaic module and an adjacent heat exchanger.
            - **Relevance to CONTEXT:** Low to Moderate - The focus on a hybrid solar panel suggests a combination of photovoltaic and thermal aspects, but the details provided mainly concentrate on the heat exchanger and the way the cooling fluid in it interacts with the photovoltaic module, rather than the specific architectural features outlined in the CONTEXT.

            ## Patent Number: 2015253858
            - **Description:** This patent pertains to a photovoltaic thermal (PV/T) hybrid solar collector, with a focus on a laminated construction involving a cooler/absorber and a photovoltaic unit with cells sandwiched between laminate materials.
            - **Relevance to CONTEXT:** Moderate - The patent includes a discussion of photovoltaic cells and thermal management via a cooler/absorber structure, which aligns it more with our CONTEXT in terms of combining photovoltaic and thermal components. However, the specifics of the construction and particular elements like the void space and framework are not mentioned.

            # Conclusion

            - **Closest Match:** Patent Number 2017228268 appears to be directly relevant to the CONTEXT and would need to be further investigated for potential infringement or overlap.
            - **No Match:** Patent Numbers 2013202630, 2017204250 show no relevant overlap with the CONTEXT.
            - **Potential Overlap:** Patent Numbers 2016239987 and 2015253858 include aspects of photovoltaic and thermal energy conversion but do not directly address the specific claims laid out in the CONTEXT.



        CONTEXT: {context}


    """
    return prompt

def generate_analysis_prompt():
        # Read the analysis string from the file
    with open('analysis.txt', 'r') as f:
        analysis = f.read()
    prompt = f"""

        CURRENT_PATENTS: {analysis}


    """
    return prompt
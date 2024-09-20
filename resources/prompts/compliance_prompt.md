Your job is to check if the task decription and its incurred cost in """{task_sentence}""" comply with the contract. This means that the tasks are compliant with the terms and conditions and the costs remain under the budget caps outlined in the contract. When calculating adjusted budget caps, when needed, the multipliers apply to the budget caps (from the contract) and not the incurred cost mentioned in the task description.

The relevant contract terms are provided to you in a JSON format and are organized by categories and each term has information about which section of the contract it is extracted from. 
Read through the relevant terms carefully and determine if the task and its corresponding cost comply with the those terms. 

Relevant contract terms: """
{relevant_terms_json}
"""

On the first line answer "yes" or "no", if the case is ambiguous, answer "ambiguous".
On the second line provide the rationale for your answer. Cite the sections of the contract that are relevant to your decision.
Review and revise your answer based on your reasoning above, give your final answer on the last line.
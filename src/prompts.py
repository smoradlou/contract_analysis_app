from langchain.prompts import PromptTemplate

def read_prompt(file_path):
    """Reads and returns the content of a prompt from a specified file."""
    with open(file_path, 'r') as file:
        return file.read()

def format_prompt(template_str, **kwargs):
    """
    Formats a given template string using the provided keyword arguments.

    Args:
    - template_str (str): The prompt template string.
    - kwargs: The dynamic values to be inserted into the template.

    Returns:
    - str: The formatted prompt.
    """
    prompt_template = PromptTemplate.from_template(template_str)
    return prompt_template.format(**kwargs)

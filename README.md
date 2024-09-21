
# Contract Analysis App

## Overview

Welcome to the **Contract Analysis App**! This App has two main fuctionalities. It extracts terms and conditions from a contract. Only DOCX format is supported at the moment for the contract text. It can also check task descriptions and their costs against the contract for compliance, to be provided as XLSX or CSV,  The two functionalities are presented on two columns in the user interface.

## Local Setup

To get started, follow these steps for configuring your local environment.

### Virtual Environment Setup

1. **Create a new virtual environment**:
   - Install `pipenv`:
     ```bash
     pip install pipenv
     ```
   - Create a new `pipenv` environment:
     ```bash
     pipenv install
     ```

2. **Install dependencies**:
   ```bash
   pipenv install
   ```

3. **Activate the virtual environment**:
   ```bash
   pipenv shell
   ```

### Running the App

1. **Create a `.env` file**:
   - This file will store your secrets as well as other environment variables.
   
   Please refer to .env example.

2. **Add the secrets to the `.env` file**.

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```
## Next Steps
1. **Add unit tests**
2. **Create a diverse test set for evaluation**
3. **Implement logging** for all of the steps in the prompt chain and the agent
4. **Error handling and edge cases**
5. **Modify the calculator agent to be more specific to the usecase, i.e. calculations of budget caps.** It is still far from perfect at its current form.

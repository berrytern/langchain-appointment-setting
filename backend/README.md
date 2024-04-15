# FastAPI Translation Service

This project demonstrates how to build a attendant for appointment setting using Python 3.11+ and FastAPI, leveraging OpenAPI models for achaive the main goal.
## Prerequisites
- [Python 3.11+](https://www.python.org/downloads/)


### Initial setup

- Clone the repository:
    ```sh
    git clone https://github.com/berrytern/langchain-appointment-setting.git
    cd langchain-appointment-setting
    ```
- Create a virtual environment and activate it:
    ```sh
    python -m venv dev_env # Create virtual environment
    . dev_env/bin/activate # Activate the virtual environment
    ```
- Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

### Usage

- Obtain API keys:
    - Follow the tutorial on this [link](https://www.maisieai.com/help/how-to-get-an-openai-api-key-for-chatgpt)

- Update configuration:
    - Copy the .env.example file to .env
    - Add your ChatOpenApi API key to .env file.

- Run the FastAPI app:
    ```sh
    python server.py
    ```
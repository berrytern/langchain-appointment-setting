# FastAPI Attendant  Service

This project demonstrates how to build a attendant for appointment setting using Python 3.11+ and FastAPI, leveraging OpenAPI models for achaive the main goal.

### Initial setup

- Clone the repository:
    ```sh
    git clone https://github.com/berrytern/langchain-appointment-setting.git
    cd langchain-appointment-setting
    ```

### Usage

- Obtain API keys:
    - Follow the tutorial on this [link](https://www.maisieai.com/help/how-to-get-an-openai-api-key-for-chatgpt)

- Update configuration:
    - Copy the .env.example file to .env
    - Add your ChatOpenApi API key to .env file.

- Run the services:
    ```sh
    docker compose up -d 
    ```

- Access the web-site:
    http://localhost:80
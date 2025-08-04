# fastapi-langraph

## Getting Started

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/posgnu/fastapi-langraph.git
    cd fastapi-langraph
    ```

2.  **Set up environment variables:**

    Copy the `.env.example` file to `.env` and add your API keys.
    ```bash
    cp .env.example .env
    ```

3.  **Install dependencies:**
    ```bash
    poetry install
    ```

4.  **Run the application:**
    ```bash
    PYTHONPATH=. poetry run uvicorn fastapi_langraph.main:app --reload
    ```

The application will be available at `http://localhost:8000`.

# FASTAPI Project

This repository contains a project built using [FastAPI](https://fastapi.tiangolo.com/), a modern, fast (high-performance) web framework for building APIs with Python.

## Features

- **High Performance**: Built on Starlette and Pydantic for speed and efficiency.
- **Automatic Documentation**: Interactive API docs generated with Swagger UI and ReDoc.
- **Asynchronous Support**: Fully supports async programming for modern Python applications.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/imeugenecarlo/FASTApi.git
    cd your-repo
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

1. Start the FastAPI server:
    ```bash
    uvicorn main:app --reload
    ```

2. Open your browser and navigate to:
    - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
    - ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Project Structure

```
/project-root
├── docker-compose.yml          # Docker Compose configuration for services
├── Dockerfile                  # Dockerfile for building the FastAPI app
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
├── app/                        # Main application folder
│   ├── main.py                 # Entry point of the FastAPI application
│   ├── models.py               # Pydantic models for request/response
│   ├── chains/                 # Chain logic for conversational retrieval
│   │   ├── support_chain.py    # Conversational retrieval chain logic
│   ├── data/                   # Data files for the application
│   │   └── faq.txt             # FAQ data for vector store
│   ├── model/                  # Schema definitions
│   │   └── schemas.py          # Pydantic schemas for API requests
│   ├── routes/                 # API route definitions
│   │   └── weaviate_routes.py  # Routes for Weaviate interactions
│   ├── services/               # Business logic and service integrations
│   │   ├── embedding_service.py # Embedding generation and vector store logic
│   │   ├── weaviate_client.py  # Weaviate client and RAG pipeline
│   │   ├── weaviate_utils.py   # Utility functions for Weaviate
│   ├── utils/                  # Utility modules
│   │   ├── logging_utils.py    # Centralized logging configuration
│   │   ├── prompt_templates.py # Prompt templates for LLM interactions
├── __pycache__/                # Compiled Python files (ignored in .gitignore)
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

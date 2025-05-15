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
├── app/
│   ├── main.py          # Entry point of the application
│   ├── routers/         # API route definitions
│   ├── models/          # Data models
│   ├── services/        # Business logic
│   └── tests/           # Unit and integration tests
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

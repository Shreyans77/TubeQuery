# YouTube RAG Application

A powerful Retrieval-Augmented Generation (RAG) application that allows you to "chat" with YouTube videos. By processing video transcripts, this tool enables you to ask questions and get accurate answers based on the video's content.

## Features

*   **Video Processing**: Instantly extracts and processes transcripts from YouTube videos.
*   **Intelligent Q&A**: Uses advanced LLMs (Mistral-7B via HuggingFace) to answer questions based *only* on the video context.
*   **Vector Search**: Utilizes FAISS for efficient similarity search within the video content.
*   **Clean Interface**: Simple and responsive web interface for easy interaction.

## Tech Stack

*   **Backend**: Python, FastAPI
*   **LLM Orchestration**: LangChain
*   **Models**: Mistral-7B-Instruct (via HuggingFace Hub)
*   **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
*   **Vector Database**: FAISS (CPU)
*   **Frontend**: HTML, CSS, JavaScript

## Prerequisites

*   Python 3.8+
*   A HuggingFace API Token

## Installation

1.  **Clone the repository**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create and activate a virtual environment**
    ```bash
    python -m venv venv
    
    # Windows
    .\venv\Scripts\activate
    
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Setup**
    Create a `.env` file in the root directory and add your HuggingFace API token:
    ```env
    HUGGINGFACEHUB_API_TOKEN=your_token_here
    ```

## Usage

1.  **Start the Server**
    Run the application using Uvicorn:
    ```bash
    uvicorn backend.backend:app --reload
    ```

2.  **Access the Application**
    Open your browser and navigate to:
    `http://localhost:8000`

3.  **Interact**
    *   Paste a YouTube URL and click "Process Video".
    *   Once processed, ask any question about the video in the chat interface.

## Project Structure

*   `backend/`: Contains the FastAPI application and RAG logic.
    *   `backend.py`: API Server entry point.
    *   `rag_engine.py`: Core logic for transcript extraction, embedding, and LLM querying.
*   `static/`: Frontend assets (HTML, CSS, JS).
*   `requirements.txt`: Project dependencies.

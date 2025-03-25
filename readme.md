# RAG System 🚀

![FastAPI](https://img.shields.io/badge/FastAPI-009485?style=flat-square&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat-square&logo=next.js&logoColor=white)
![Postgres](https://img.shields.io/badge/Postgres-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

## 📖 Description

This project is a **Retrieval-Augmented Generation (RAG) System**. The backend of this project is developed in **FastAPI**, and the frontend is built using **Next.js**. For the vector database, I am using **Postgres** with the **pgvector** extension. The system utilizes the open-source **llama3.2:1b** model to generate responses. You can run this project easily using **Docker**—just clone the repository, build the Docker images, and start the containers with a few simple commands!

## 📑 Table of Contents

- [Features](#-features)
- [System Requirements](#-system-requirements)
- [Installation](#-installation)
- [Backend Architecture Pattern](#-backend-architecture-pattern)
- [Project Structure](#-project-structure-backend)
- [Usage](#-usage)
- [Future Enhancements](#-future-enhancements)
- [Contributing](#-contributing)

## ✨ Features

- **FastAPI Backend**: A fast and scalable API to process requests efficiently.
- **Next.js Frontend**: A modern, responsive interface for users.
- **Postgres with pgvector**: A powerful vector database for similarity searches.
- **Llama3.2:1b Model**: An open-source model for generating high-quality responses.
- **Docker Support**: Simplified setup and deployment with Docker.
- **Document ingestion**: Document ingestion and query processing.

## 💻 System Requirements

To run this project locally, ensure you have the following installed:

- **Docker**: Version 28.0.1 or higher
- **Docker Compose**: Version 1.29 or higher
- **Git**: Required to clone the repository
- **Python**: Version 3.9 or higher (if running without Docker)
- **Node.js**: Version 18 or higher (if running without Docker)
- **RAM**: Min 8GB of RAM.

## 🛠 Installation

### ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white) Using Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/pwnbisht/RAG.git
   cd RAG

2. **Build the Docker Images**:
   ```bash
   docker-compose build

3. **Start the Containers**:
   ```bash
   docker-compose up -d
   
4. **Access the application**:
   - frontend: <span style="background:#ff983f63; padding:1px;">http://localhost:3000</span> (For container and host machine ports are same)
   - backend: <span style="background:#ff983f63; padding:1px;">http://localhost:8000</span>  (For container and host machine ports are same)
   - database: <span style="background:#ff983f63; padding:1px;">http://localhost:5432</span>  (For container port is 5432 and host port is 5433)
   - ollama server: <span style="background:#ff983f63; padding:1px;">http://localhost:11434</span> (For container port is 11434 and host port is 11435)


### Without Docker
If you’d rather set it up manually, follow these steps:

1. **Set up Ollama**:
   Ollama runs the **llama3.2:1b** model locally for response generation.
   - Install Ollama: Download and install from [ollama download](https://ollama.com/download).
   - Pull the model: 
      ```bash
      ollama pull llama3.2:1b
   - Start the server: 
      ```bash
      ollama serve
      
2. **Set up Postgres**:
   Postgres serves as the database for storing data.
   - Install Postgres: Get it from [postgresql.org/download](https://www.postgresql.org/download/) and follow the instructions for your OS.
   - Create a database and user:
      ```bash
      sudo -u postgres psql
      CREATE DATABASE voiceai;
      \q

3. **Install pgvector**:
   pgvector adds vector support to Postgres for similarity searches.
   - Clone the repository:
      ```bash
      git clone https://github.com/pgvector/pgvector.git
      cd pgvector

   - Build and install: 
      ```bash
      make
      sudo make install

   - Enable the extension:
      ```bash
      psql -U postgres -d voiceai -c "CREATE EXTENSION vector;"


4. **Clone the repository**:
   ```bash
   git clone https://github.com/pwnbisht/RAG.git
   cd RAG

5. **Set up the backend**:
   - Navigate to the backend directory:
   ```bash
      cd backend
   ```

   - Create a virtual environment and install dependencies:
   ```bash
      python -m venv venv
      source venv/bin/activate  # On Windows: venv\Scripts\activate
      pip install -r requirements.txt
   ```
   
   - Start the Backend
   ```bash
   uvicorn app.main:app
   ```

6. **Set up the Frontend**:
   - Navigate to the frontend directory:
   ```bash
      cd frontend
   ```

   - Install dependencies and start:
   ```bash
      npm install
      npm run dev
   ```

7. **Access the Application**:
   - frontend: <span style="background:#ff983f63; padding:1px;">http://localhost:3000</span>
   - backend: <span style="background:#ff983f63; padding:1px;">http://localhost:8000</span> 


## 🏗 Backend Architecture Pattern
   The backend follows a **Route → Controller → Factory → Repository** pattern for clean separation of concerns:


### Pattern Components

1. **Routes** (`/api/*`)
   - 🌐 Entry point for HTTP requests
   - 🛂 Request validation
   - 🔀 Route traffic to appropriate controllers
   - Example: `documents.py` handles `/docs/*` endpoints

2. **Controllers** (`/controllers/*`)
   - 🧠 Business logic orchestrators
   - 🔄 Coordinate between services and repositories
   - 🛡️ Authorization checks
   - Example: `DocumentController` handles documents workflow

3. **Factories** (`/factory/*`)
   - 🏭 Object creation specialists
   - 🔄 Dependency injection management
   - 🧩 Complex object assembly
   - Example: `get_document_service` creates model instances with proper configuration

4. **Repositories** (`/repositories/*`)
   - 💽 Database interaction layer
   - 📦 CRUD operations encapsulation
   - 🛡️ Database abstraction
   - Example: `DocumentRepository` handles document storage operations

### Why This Pattern?

- ✅ **Separation of Concerns**: Each layer has distinct responsibility
- 🧪 **Testability**: Mock individual components easily
- 🔄 **Reusability**: Shared repositories and factories
- 🚀 **Scalability**: Add new features without breaking existing flow
- 🔧 **Maintainability**: Isolate changes to specific layers

## 📂 Project Structure (Backend)
```bash
   📦 Root
   |
   ├─ .gitignore
   ├─ backend
   │  ├─ Dockerfile
   │  ├─ app
   │  │  ├─ .env
   │  │  ├─ __init__.py
   │  │  ├─ api
   │  │  │  └─ v1
   │  │  │     ├─ router.py
   │  │  │     └─ users
   │  │  │        ├─ auth
   │  │  │        │  ├─ auth.py
   │  │  │        │  └─ auth_response.py
   │  │  │        └─ documents
   │  │  │           └─ documents.py
   │  │  ├─ controllers
   │  │  │  ├─ documents
   │  │  │  │  └─ documents.py
   │  │  │  └─ users
   │  │  │     └─ auth.py
   │  │  ├─ core
   │  │  │  ├─ config.py
   │  │  │  ├─ exceptions.py
   │  │  │  └─ factory
   │  │  │     ├─ documentfactory.py
   │  │  │     └─ userfactory.py
   │  │  ├─ db
   │  │  │  ├─ Dockerfile
   │  │  │  ├─ base.py
   │  │  │  ├─ init.sql
   │  │  │  ├─ init_db.py
   │  │  │  └─ models
   │  │  │     ├─ __init__.py
   │  │  │     ├─ documents.py
   │  │  │     └─ users.py
   │  │  ├─ main.py
   │  │  ├─ middlewares
   │  │  │  └─ security_headers.py
   │  │  ├─ repositories
   │  │  │  ├─ __init__.py
   │  │  │  ├─ documents
   │  │  │  │  └─ documents.py
   │  │  │  └─ users
   │  │  │     ├─ tokens.py
   │  │  │     └─ users.py
   │  │  ├─ schemas
   │  │  │  ├─ __init__.py
   │  │  │  ├─ documents
   │  │  │  │  └─ document_schemas.py
   │  │  │  └─ users
   │  │  │     └─ users.py
   │  │  ├─ services
   │  │  │  ├─ __init__.py
   │  │  │  ├─ auth
   │  │  │  │  └─ auth.py
   │  │  │  └─ documents
   │  │  │     ├─ chat_service.py
   │  │  │     ├─ documentservice.py
   │  │  │     ├─ embeddings.py
   │  │  │     └─ llm_service.py
   │  │  ├─ tests
   │  │  │  ├─ __init__.py
   │  │  │  ├─ documents
   │  │  │  │  ├─ __init__.py
   │  │  │  │  └─ test_documents.py
   │  │  │  └─ users
   │  │  │     ├─ test_auth.py
   │  │  │     └─ __init__.py
   │  │  └─ utils
   │  │     ├─ __init__.py
   │  │     └─ security.py
   │  └─ requirements.txt
```

### 🚀 Usage
- **Start the application** using either Docker or the manual setup steps above.
- **Visit the frontend** at <span style="background:#ff983f63; padding:1px;">http://localhost:3000</span>
- **Interact with the RAG system**:

   - Create the user in the Frontend enterface.
   - Login the user.
   - Upload the Document for Q&A.
   - Enter queries in the frontend interface.
   - The system retrieves relevant data and generates responses using the llama3.2:1b model.


### 🔮 Future Enhancements
- **Faster Response**
- **Promtps Enhencemets**
- **Better Query Handling**
- **Multiple Models**
- **Agents**
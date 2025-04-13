# 🧠 Semantic Document Chat App

An AI-powered application that enables users to **upload documents** and **chat with them** intelligently. The system uses **LLMs**, **vector embeddings**, and **retrieval-augmented generation (RAG)** to deliver contextual responses based on the content of the uploaded documents.

---

## 🚀 Features

- 📄 Upload PDFs or DOCX files  
- 🔍 Semantic document understanding  
- 💬 Conversational interface with memory  
- ⚙️ FAISS vector store for fast retrieval  
- 🤖 LLM integration with Together.ai or OpenAI-compatible models  
- 🧠 Powered by LangChain and FastAPI  
- 🌐 Streamlit-based frontend  

---

## 📁 Project Structure

```
app/
├── backend/              # FastAPI backend (chat logic, API routes)
│   ├── accessors.py
│   ├── chat.py
│   ├── config.py
│   ├── endpoints.py
│   ├── models.py
│   └── utils.py
├── frontend/             # Streamlit frontend
│   └── app.py
ci/                       # Continuous integration configs
temp/                     # Temp folder for storing downloads
run_backend.py            # Entry point to start FastAPI server
run_frontend.py           # Entry point to run Streamlit frontend
docker-compose.yml        # Compose file for MongoDB and other services
.env                      # Environment variables
requirements.txt          # Python dependencies
```

---

## 🛠️ Setup Instructions

### 🔧 1. Clone the repo

```bash
git clone https://github.com/your-username/semantic-doc-chat.git
cd semantic-doc-chat
```

### 📦 2. Install Python dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 🧪 3. Set up your environment

Create a `.env` file:

```env
MONGO_URL=mongodb://root:root@localhost:27017/your_db_name
MONGO_DB_NAME=your_db_name
S3_URL=http://localhost:9000
S3_KEY=your_s3_key
S3_SECRET=your_s3_secret
S3_BUCKET=your_bucket_name
S3_PATH=uploads
TOGETHER_API_KEY=your_together_api_key
```

> 🔐 Replace values with your actual credentials.

---

## 🧬 Run the Application

### 🚀 Backend (FastAPI)

```bash
python run_backend.py
```

### 🌐 Frontend (Streamlit)

```bash
python run_frontend.py
```

---

## 🐳 Docker Support

To run MongoDB via Docker:

```bash
docker-compose up -d
```

---

## 📚 Example Usage

1. Go to the frontend  
2. Upload a `.pdf` or `.docx`  
3. Start chatting with the document!  

---

## 💻 For Developers

### ✅ Code Style

This project uses [`ruff`](https://docs.astral.sh/ruff/) for linting and `pre-commit` hooks to enforce formatting.

### 🔧 Set up `pre-commit`

```bash
pip install pre-commit
pre-commit install
```

Now every commit will automatically trigger linting and formatting checks.

To run pre-commit manually on all files:

```bash
pre-commit run --all-files
```

---

## ✅ To-Do

- [ ] Add support for multiple file uploads  
- [ ] Improve memory/context handling across sessions  
- [ ] Add user authentication  
- [ ] Support local LLMs (e.g., via Ollama)

---

## 📄 License

MIT License. Feel free to fork and build on top of this.

---

## 💬 Credits

Built with ❤️ using:
- [FastAPI](https://fastapi.tiangolo.com/)
- [LangChain](https://www.langchain.com/)
- [Streamlit](https://streamlit.io/)
- [Together.ai](https://together.ai/)
- [Emojis](https://emojipedia.org/) from [Emojipedia](https://emojipedia.org/)

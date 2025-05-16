# BytePersona - The Code-Driven Extension of Who I Am!

**BytePersona** is a smart portfolio chatbot interface designed to represent Mr. Dhinesh E in a conversational manner. It uses a custom HTML/CSS/JS frontend mimicking WhatsApp's UI and interacts with a FastAPI backend powered by a Prolog knowledge base.

## 💬 What It Does

- Answers questions about Dhinesh E's personal, academic, and technical background.
- Parses user messages and generates contextual responses.
- Handles greetings, heart emojis, and factual queries using Prolog.
- Provides an engaging chat-like user experience via a WhatsApp-style interface.

## 🧠 How It Works

### Frontend (📱 `index.html`)
- Designed to look and feel like WhatsApp.
- Written in HTML, CSS, and vanilla JavaScript.
- Sends messages to the FastAPI backend and renders responses dynamically.
- Includes features like:
  - Emoji picker
  - Typing indicator
  - Link parsing
  - Responsive design

### Backend (⚙️ `main.py`)
- Built with FastAPI.
- Consults `knowledge_base.pl` using `pyswip` (SWI-Prolog bridge).
- Uses CORS to communicate with the frontend.
- Handles different user intents like:
  - Personal info (name, email, location, etc.)
  - Education and CGPA
  - Projects and certifications
  - Skills and hobbies
  - Greetings and emojis

## 📁 Project Structure

```
BytePersona/
├── index.html            # WhatsApp-style chatbot UI
├── main.py               # FastAPI server with Prolog integration
└── knowledge_base.pl     # Prolog facts and rules about Dhinesh E
```

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- SWI-Prolog installed and in your system PATH
- `pip install -r requirements.txt` with `fastapi`, `uvicorn`, and `pyswip`

### Running Locally

1. Start the FastAPI backend:
   ```bash
   uvicorn main:app --reload
   ```

2. Open the `index.html` file in a browser (served via localhost or directly).

> 🔗 Make sure the backend is accessible at `http://localhost:8000/chat` or change the endpoint in `index.html`.

## 📄 License

This project is licensed under the MIT License.

## ✨ Credits

Developed by Dhinesh E .

---

Enjoy chatting with BytePersona! 🤖💬

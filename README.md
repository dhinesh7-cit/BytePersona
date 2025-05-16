# BytePersona

**BytePersona** is a modular AI-driven application designed to create personalized digital personas. It combines a backend API with a Streamlit-based frontend, enabling users to interact with AI-generated personas seamlessly.

## 🚀 Features

- **Backend API**: Handles data processing, persona generation, and serves as the core engine of the application.
- **Streamlit Frontend**: Provides an intuitive user interface for interacting with generated personas.
- **Modular Architecture**: Separation of concerns between backend and frontend for scalability and maintainability.

## 📁 Project Structure

```
BytePersona/
├── backend_api/       # Backend API codebase
└── streamlit_app/     # Streamlit frontend application
```

## 🔧 Getting Started

### Prerequisites

- Python 3.7 or higher
- Recommended: Virtual environment tool (e.g., `venv`, `conda`)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/dhinesh7-cit/BytePersona.git
   cd BytePersona
   ```

2. **Set up and run the backend API:**
   ```bash
   cd backend_api
   pip install -r requirements.txt
   python app.py
   ```

3. **Set up and run the Streamlit frontend:**
   ```bash
   cd ../streamlit_app
   pip install -r requirements.txt
   streamlit run app.py
   ```

*Ensure that the backend API is running before launching the Streamlit app.*

## 🛠️ Technologies Used

- **Backend**: Python, Flask/FastAPI (depending on implementation)
- **Frontend**: Streamlit
- **AI/ML**: OpenAI GPT models (or other NLP models)
- **Others**: Docker (optional for containerization), Git

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

## 📬 Contact

For questions or suggestions, please open an issue or contact [Dhinesh E](https://github.com/dhinesh7-cit).

---

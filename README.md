# 🎯 ActionPoint - AI Meeting Assistant

ActionPoint is an intelligent meeting assistant that records audio, transcribes it locally, and uses AI to extract actionable tasks. It then automatically syncs those tasks to a Trello board.

**Key Feature:** Built with a **Zero-Cost architecture** using local speech recognition (Whisper) and Google's Gemini Flash API.

---

## 🚀 Features

- 🎙️ **Record Meetings:** Browser-based audio recording with visual status.
- 👂 **Local Transcription:** Uses OpenAI's **Whisper** model running locally on your CPU (privacy-focused & free).
- 🧠 **AI Analysis:** Uses **Google Gemini 1.5 Flash** to generate summaries and extract tasks (JSON structured output).
- ✅ **Trello Sync:** Automatically creates cards on your Trello board for every identified task.

---

## 🛠️ Tech Stack

- **Frontend:** React, Vite, Axios, Lucide Icons
- **Backend:** Python, Flask
- **AI Models:** OpenAI Whisper (Local), Google Gemini 1.5 Flash
- **Integrations:** Trello API

---

## ⚙️ Setup Guide

### Prerequisites

1. **Node.js** installed
2. **Python 3.9+** installed
3. **FFmpeg** installed and added to system PATH (required for Whisper)

---

### 🔧 Backend Setup

```bash
cd backend
python -m venv venv
```

**Activate virtual environment**

Windows:

```bash
.\venv\Scripts\activate
```

Mac / Linux:

```bash
source venv/bin/activate
```

**Install dependencies**

```bash
pip install flask flask-cors python-dotenv openai-whisper google-generativeai requests
```

**Create a `.env` file in the `backend` folder**

```env
GOOGLE_API_KEY=your_google_key_here
TRELLO_API_KEY=your_trello_key
TRELLO_TOKEN=your_trello_token
TRELLO_LIST_ID=your_trello_list_id
```

**Run the backend server**

```bash
python app.py
```

---

### 🎨 Frontend Setup

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

---

## 📸 How to Use

1. Open the app in your browser (usually `http://localhost:5173`)
2. Click **Start Recording** and speak
3. Click **Analyze Meeting**
4. Review the AI-generated **Summary** and **Tasks**
5. Click **Sync to Trello** to push tasks to your board

---

## 🔐 Privacy & Cost

- All audio transcription is done **locally**
- No paid APIs are required
- Only lightweight Gemini Flash API is used for text analysis

---

# Interview Prep Bot

A LangChain and Gemini chatbot that helps students practice behavioral, technical, HR, and situational interview questions. It adapts its coaching to a target role and experience level, explains answer structure, and keeps context during a practice session.

## What is included

- Streamlit chat interface with five practice focuses, suggested questions, session history, and friendly error handling.
- A LangChain prompt template connected to Gemini using `ChatGoogleGenerativeAI`.
- A terminal interface (`python interview_bot.py`) as an alternative to the web app.
- Streaming answers with low reasoning effort, a 45-second request timeout, and no automatic retries to keep waits bounded.
- `.env` configuration and `.gitignore` protection for API keys.

## Requirements

- Python 3.10 or newer.
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).
- Internet access while the app calls Gemini.

## Setup (Windows PowerShell)

Open PowerShell in this project folder and run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Open the included `.env` in a text editor and add your Gemini API key. If `.env` is missing, create it from the example with `Copy-Item .env.example .env`. Keep `.env` private; it is excluded from Git. If PowerShell blocks virtual-environment activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again.

By default, the app uses `gemini-3.5-flash` with low reasoning effort to keep replies quick. You can change `GEMINI_MODEL` in `.env` to another model available to your Gemini API key.

## Run the web app

```powershell
streamlit run app.py
```

Streamlit prints a local address (usually `http://localhost:8501`). Open it in your browser. Choose a role and experience level in the sidebar, select a practice focus, then ask a question or choose a suggestion.

## Run in the terminal

```powershell
python interview_bot.py
```

Enter a target role and experience level, then ask questions. Type `quit` to exit.

## Five questions to try

1. **Behavioral:** “Tell me about a time you faced a challenge in a team. How can I structure my answer using STAR?”
2. **Introduction:** “Help me draft a 60-second introduction for an entry-level data analyst interview. Use placeholders for my experience.”
3. **Technical:** “Explain Python list comprehensions and give me a short interview-ready example.”
4. **Situational:** “What would you do if you disagreed with a teammate about a technical decision?”
5. **HR:** “How should I answer ‘Why do you want to work here?’ when I have not researched the company yet?”

Follow each answer with a question such as “Can you make that more concise?” to try the session context.

## Common issues

- **Missing API key:** Check that `.env` exists beside `app.py` and contains `GEMINI_API_KEY=...`; restart the app after editing it.
- **Invalid key or permission:** Confirm the key is active and configured for the Gemini API in Google AI Studio.
- **Model not found:** Set `GEMINI_MODEL` to a model enabled for your account.
- **Network or quota error:** Check your connection and Gemini API quota, then retry.

The key is read by Python on the server side and is never placed in the browser interface. Never commit `.env` or share its contents.

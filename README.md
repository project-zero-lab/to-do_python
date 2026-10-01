# Project Zero - Facilitated by : Mr. Vijay Patkar

# my_Taskz 🎯
**Built in Project Zero — Web App Deployment using Python**

A productivity to-do app, deployed on Streamlit Community Cloud so every
learner can try it from a browser link — no install, nothing to set up.

## Learners have to build their own versions


## Run it locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy (free, public)
1. Push this folder to a public GitHub repo.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub.
3. "New app" → pick this repo → main file path: `app.py` → Deploy.
4. Share the `*.streamlit.app` link with students.

## ⚠️ Important: how data works
This app stores tasks in **`st.session_state`**, which Streamlit keeps
**per browser tab, in server memory only**:

- ✅ Multiple people on the same link at the same time each get their **own
  private task list** — nobody sees anyone else's tasks.
- ❌ Nothing is saved anywhere. **Closing the tab, refreshing the page, or
  the app going idle and restarting (Community Cloud sleeps unused apps)
  wipes that tab's tasks.**

This is correct and expected for a classroom demo —
it is **not** a bug. If a future session wants tasks to survive a refresh
or be shared across devices, that needs a real database and probably
login, which is a good "what's the next problem?" hook for a later module,
not something to bolt on quietly here.

## Files
- `app.py` — the whole app (one file, intentionally, so students can read it top to bottom)
- `requirements.txt` — the one dependency: streamlit

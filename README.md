# Voice Command AI

A Python-based voice assistant for Windows that listens to spoken commands and performs useful desktop and online tasks, including Google search, YouTube search and playback, weather updates, news headlines, Windows volume control, and email sending.

> **Security notice:** Never commit your real `.env` file, API keys, or email app passwords to GitHub. If a key or password was already pushed to a repository, revoke or rotate it; deleting it from the latest code does not remove it from Git history.

## Features

- **Speech recognition:** Converts speech to text using the Google Speech Recognition service through the `SpeechRecognition` package.
- **Text-to-speech:** Speaks responses using `pyttsx3` and Windows SAPI5.
- **Wake/sleep flow:** Checks recognized speech for phrases such as “hey assistant,” “wake up,” or “hello”; supports “go to sleep.”
- **Google search:** Opens Google results for a spoken search query.
- **YouTube search:** Opens YouTube search results for a spoken query.
- **YouTube playback:** Uses `pywhatkit` to open a matching YouTube video for a spoken “play …” command.
- **Weather:** Fetches current weather data from Open-Meteo.
- **News:** Reads up to five top headlines from NewsAPI.
- **Windows volume control:** Sets the Windows master volume to a percentage from 0 to 100.
- **Email:** Sends an email through Gmail SMTP using credentials loaded from environment variables and a spoken recipient name.
- **Error handling:** Handles common speech-recognition, HTTP/network, response-data, email, playback, and volume-control errors.

## Requirements

- Windows (the speech engine uses SAPI5 and volume control uses Pycaw/Windows audio APIs).
- Python 3.10 or a compatible Python version supported by the dependencies.
- A working microphone and speakers/headphones.
- Internet access for Google speech recognition, weather/news requests, and YouTube/Google services.
- A NewsAPI key for news functionality.
- A Gmail account configured to use an App Password, where supported, for email functionality.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Rushabh-14/voice-comand-AI.git
cd voice-comand-AI
```

If you already have the repository cloned, open a terminal in its project folder instead.

### 2. Create and activate a virtual environment (recommended)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use Command Prompt:

```bat
.venv\Scripts\activate.bat
```

### 3. Install dependencies

Install the packages used by the project:

```bash
python -m pip install SpeechRecognition pyttsx3 requests pywhatkit numpy sounddevice comtypes pycaw python-dotenv
```

Depending on your Python and Windows setup, microphone support may also require the audio dependencies used by `SpeechRecognition`. If microphone initialization fails, consult the SpeechRecognition installation instructions for your environment.

## Configuration

The project loads settings from a local `.env` file using `python-dotenv`.

### 1. Create `.env`

Copy `.env.example` to a new file named `.env` in the same folder as `main.py`.

```dotenv
NEWS_API_KEY=your_new_newsapi_key_here
MY_EMAIL=your_gmail_address@gmail.com
MY_APP_PASSWORD=your_gmail_app_password_here
```

Replace the placeholders with your own values. Do not add quotation marks unless they are actually part of a value.

- `NEWS_API_KEY`: Your NewsAPI key. Obtain it from [NewsAPI](https://newsapi.org/).
- `MY_EMAIL`: The Gmail address used to send email.
- `MY_APP_PASSWORD`: The Gmail App Password for that account, where App Passwords are available. Do not use your normal Gmail password.

### 2. Keep secrets out of Git

The repository should include `.env.example`, which contains placeholders, and `.gitignore`, which excludes `.env`.

**Do not commit `.env`.** Before pushing, check the staged files:

```bash
git status
```

If a secret was committed previously, revoke or rotate it immediately. Removing a secret from the current file does not remove it from earlier commits.

## Run the assistant

From the project folder, run:

```bash
python main.py
```

The program asks:

```text
Run in test mode? (y/n):
```

- Enter `y` to start listening for commands immediately.
- Enter `n` to enter the wake-phrase loop.

The wake-phrase loop uses speech recognition to detect the configured phrases. It is not a dedicated offline wake-word detection engine, and speech recognition requires internet access.

## Voice commands

Speak clearly and allow the assistant to finish listening before giving the next command.

| Example phrase | Action |
|---|---|
| `search in google Python tutorials` | Opens Google search results for “Python tutorials.” |
| `search in youtube lo-fi music` | Opens YouTube search results for “lo-fi music.” |
| `play Imagine Dragons` | Uses `pywhatkit` to open a matching YouTube video. |
| `what is the weather` | Reads current weather data for the coordinates configured in `get_weather()`. |
| `give me the news` | Reads up to five US top headlines from NewsAPI. |
| `set volume to 50` | Sets Windows master volume to 50%. |
| `send email` | Asks for a recipient name, subject, and message, then sends the email. |
| `go to sleep` | Returns to the wake-phrase loop. |
| `help` | Speaks a list of supported commands. |
| `exit` or `quit` | Stops the assistant loop. |

For volume control, use the format `set volume to N`, where `N` is an integer from `0` to `100`.

### Email recipients

Edit `email_list` in `main.py` and replace the example addresses with the intended recipients:

```python
email_list = {
    "dude": "your_friend@example.com",
    "mom": "mom@example.com",
    "dad": "dad@example.com",
}
```

When you say “send email,” the assistant asks you to say `dude`, `mom`, or `dad`. It uses the spoken name to choose the matching address. If the name is not recognized as one of these keys, the email is cancelled.

Email sending requires valid `MY_EMAIL` and `MY_APP_PASSWORD` values in `.env`. Review the recipient, subject, and message configuration before using the feature with real email accounts.

## Weather location

The current code uses fixed coordinates in `get_weather()`:

```python
latitude, longitude = 21.2472, 72.8508
```

These coordinates are configured for Surat, India. Change them if you want weather for a different location. The weather service is [Open-Meteo](https://open-meteo.com/).

## Project structure

A suggested repository layout is:

```text
voice-comand-AI/
├── main.py
├── .env.example
├── .gitignore
├── README.md
└── .venv/              # Local environment; do not commit
```

The `.env` file is created locally from `.env.example` and should remain untracked.

## Troubleshooting

- **Microphone not detected:** Check Windows microphone permissions, the default input device, and the microphone dependencies for `SpeechRecognition`.
- **Speech not recognized:** Speak clearly, check your internet connection, and make sure the microphone is working.
- **News unavailable:** Verify `NEWS_API_KEY`, your internet connection, and your NewsAPI account/key limits. The code reports network and response errors in the terminal.
- **Weather unavailable:** Check internet access and try again later. Open-Meteo must be reachable.
- **Email fails:** Verify `MY_EMAIL` and `MY_APP_PASSWORD`, confirm that Gmail SMTP access is available for the account, and use an App Password where required.
- **Volume control fails:** This feature depends on Windows audio APIs and may not work on other operating systems.
- **YouTube playback fails:** Check internet access and whether YouTube can open in your default browser.

## Security and privacy

- Store API keys and email credentials in `.env`, not directly in Python source code.
- Keep `.env` out of version control.
- Rotate any credential that has already been exposed in a public repository.
- Speech recognition sends audio to Google's recognition service through the library; avoid speaking sensitive information when using online recognition.
- The email feature sends messages through Gmail SMTP. Confirm the recipient, subject, and message before sending.

## Known limitations

- The application is Windows-oriented because it uses SAPI5 and Pycaw.
- Speech recognition and online features require an internet connection.
- Weather is requested for fixed coordinates until you change them in the code.
- News headlines are requested for the US (`country=us`) in the current implementation.
- The wake-phrase flow is based on speech recognition rather than a dedicated offline wake-word model.
- Recipient names and addresses must be configured manually in `email_list`.
- The project does not currently include automated tests or a graphical user interface.

## Possible future improvements

- Add a configurable weather location.
- Add support for more news countries and categories.
- Add a confirmation step before sending emails.
- Add a dedicated wake-word engine for more reliable offline activation.
- Add automated tests and structured logging.
- Add a GUI for settings and command status.

## Contributing

Contributions and suggestions are welcome. For changes, consider opening an issue first, then submit a pull request with a clear description of what changed and how it was tested. Do not include API keys, passwords, or other secrets in commits or issue reports.

## License

No license is specified here. Add a `LICENSE` file if you choose to publish the project under an open-source license. Until then, do not assume that others have permission to reuse, modify, or distribute the code.

## Author

**Rushabh Parmar**

GitHub: [@Rushabh-14](https://github.com/Rushabh-14)

---

If this project helps you, consider starring the repository.

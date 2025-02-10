
## Setup Instructions

### 1. Google OAuth Credentials

1. **Create a Google Cloud Project**:  
   Visit the [Google Cloud Console](https://console.cloud.google.com/) and create a new project.

2. **Enable the Google Calendar API**:  
   Navigate to **APIs & Services > Library** and enable the Google Calendar API for your project.

3. **Configure the OAuth Consent Screen**:  
   Set up the OAuth consent screen (for testing, choose "Desktop app" to simplify the redirect URI configuration).

4. **Create OAuth 2.0 Credentials**:  
   - Create a new OAuth 2.0 Client ID of type **"Desktop app"**.
   - Download the resulting `credentials.json` file.
   - Place `credentials.json` in the `calendar_bot/` directory.

### 2. Generate the OAuth Token Locally

Before running your containers, generate the OAuth token (`token.pickle`) on your local machine:

1. **Install Required Packages** (if not already installed):

    ```bash
    pip install google-auth-oauthlib google-api-python-client google-auth-httplib2
    ```

2. **Run the OAuth Script**:  
   Create and run a script (e.g., `run_oauth.py`) using the code below to generate `token.pickle`:

    ```python
    # run_oauth.py
    import os
    import pickle
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    # Define the scopes required (read-only access to Calendar)
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

    CREDENTIALS_FILE = 'credentials.json'
    TOKEN_FILE = 'token.pickle'

    def get_credentials():
        creds = None
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
        return creds

    def main():
        creds = get_credentials()
        print("Successfully obtained credentials!")
        print("Access Token:", creds.token)

    if __name__ == '__main__':
        main()
    ```

3. **Execute the Script**:

    ```bash
    python run_oauth.py
    ```

4. **Place `token.pickle`**:  
   Once generated, move `token.pickle` to the `calendar_bot/` directory.

### 3. Environment Variables

Create `.env` files in each service directory.

**Example: `calendar_bot/.env`**

```dotenv
CALENDAR_ID=your_calendar_id_here@example.com

# Step 1:
## Create a Google API Project
To create a Google API project, follow these steps:
- Go to the Google API Console (https://console.developers.google.com/)
- Click on the ‘Select a project’ drop-down, then on the ‘+’ button to create a new project.
- Name the project and click ‘Create’.

# Step 2:
## Enable Google Calendar API
After creating your project, you need to enable the Google Calendar API for it:
- In the Google API Console, ensure your new project is selected.
- Click on ‘Library’ in the left sidebar.
- Find ‘Google Calendar API’ and click on it.
- Click on ‘Enable’.

# Step 3:
## Create OAuth 2.0 Client IDs
This is how your program will authenticate itself to Google’s servers.
- Click on ‘OAuth consent screen’ in the left sidebar.
- Select ‘External’ for the user type, then click ‘Create’.
- Fill in the required fields, then click ‘Save and Continue’.
- Click on ‘Credentials’ in the left sidebar.
- Click on the ‘Create Credentials’ button, then select ‘OAuth client ID’.
- For the application type, select ‘Desktop app’.
- Name your OAuth client ID, then click ‘Create’.
- Click ‘OK’ to dismiss the dialog showing your client ID and secret.
- Click the download button (an arrow pointing down) to the right of the client ID you just created.

# Step 4:
## Download Client Configuration File
The file you just downloaded contains the credentials your Python script will use to authenticate itself.
- Rename this file to credentials.json 
- Move it to the gcalendar_sync/secrets folder.

# Step 5:
## Installing the Google Client Library
Next, we need the Google Client Library to interact with the Google Calendar API. <br>
This library can be installed easily using pip:
```
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
```
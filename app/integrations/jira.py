import os
import requests
from dotenv import load_dotenv

load_dotenv()

response = requests.get(
    f"{os.getenv('JIRA_URL')}/rest/api/3/myself",
    auth=(
        os.getenv("JIRA_EMAIL"),
        os.getenv("JIRA_API_TOKEN")
    ),
    headers={
        "Accept": "application/json"
    }
)

print(response.status_code)
print(response.text)
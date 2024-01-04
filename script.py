import os
import requests
from openai import OpenAI
from datetime import datetime, timedelta

GITHUB_SECRET = os.environ.get('GITHUB_SECRET')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

openai_client = OpenAI(api_key=OPENAI_API_KEY)

def get_commits_last_day(github_token, repo_name):
    headers = {'Authorization': f'token {github_token}'}
    api_url = f'https://api.github.com/repos/{repo_name}/commits'
    
    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        raise Exception("Failed to fetch the latest commit from GitHub")

    latest_commit = response.json()[0]
    last_commit_time = datetime.strptime(latest_commit['commit']['committer']['date'], '%Y-%m-%dT%H:%M:%SZ')
    since_time = (last_commit_time - timedelta(days=1)).isoformat()

    api_url += f'?since={since_time}'
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to fetch commits from GitHub")

def summarize_code(commit_messages):
    combined_message = " ".join(commit_messages)
    summary = openai_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f'Here are my recent commit messages. Please create a #buildinpublic tweet for me from these changes so that I can share it with my followers. \n\n{combined_message}'
            }
        ],
        model="gpt-3.5-turbo"
    )

    return summary.choices[0].message.content

def main():
    REPO_NAME = "" # add your repo name here; e.g. "carraya/buildinpublic"
    try:
        commits = get_commits_last_day(GITHUB_SECRET, REPO_NAME)
        commit_messages = [commit['commit']['message'] for commit in commits]
        if commit_messages:
            summary = summarize_code(OPENAI_API_KEY, commit_messages)
            print(summary)
        else:
            print("No commits in the last 24 hours.")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
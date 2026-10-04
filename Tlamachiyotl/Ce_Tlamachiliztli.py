# Based on https://docs.anthropic.com/en/docs/quickstart
#
# Important!!!

#only run once if anthropic not installed
#import subprocess, sys
#subprocess.check_call([sys.executable, "-m", "pip", "install", "anthropic"])

import os
from anthropic import Anthropic
from typing import List, Dict

client = Anthropic()


def generate_response(messages: List[Dict]) -> str:
    """Call LLM to get response"""
    system = next((m["content"] for m in messages if m["role"] == "system"), None)
    user_messages = [m for m in messages if m["role"] != "system"]
    response = client.messages.create(
        model="claude-sonnet-4-6",
        messages=user_messages,
        max_tokens=1024,
        system=system
    )
    return response.content[0].text


messages = [
    {"role": "system", "content": "You are an expert software engineer that prefers functional programming."},
    {"role": "user", "content": "Write a function to swap the keys and values in a dictionary."}
]

response = generate_response(messages)
print(response)

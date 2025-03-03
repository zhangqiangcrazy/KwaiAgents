import logging
import os
import requests
import sys
import time
import traceback

import openai
from openai import OpenAI

def make_gpt_messages(query, system, history):
    msgs = list()
    if system:
        msgs.append({
            "role": "system",
            "content": system
        })
    for q, a in history:
        msgs.append({
            "role": "user",
            "content": str(q)
        })
        msgs.append({
            "role": "assistant",
            "content": str(a)
        })
    msgs.append({
        "role": "user",
        "content": query
    })
    return msgs

def make_ollama_chat_messages(query, system, history):
    msgs = list()
    if system:
        msgs.append({
            "role": "system",
            "content": system
        })
    for q, a in history:
        msgs.append({
            "role": "user",
            "content": str(q)
        })
        msgs.append({
            "role": "assistant",
            "content": str(a)
        })
    msgs.append({
        "role": "user",
        "content": query
    })
    return msgs

class OpenAIClient(object):
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model
        openai.api_type = os.environ.get("OPENAI_API_TYPE", "open_ai")
        openai.api_key = os.environ["OPENAI_API_KEY"]
        if openai.api_type == "azure":
            openai.api_version = os.environ["OPENAI_API_VERSION"]
            openai.api_base = os.environ["OPENAI_API_BASE"]

    def chat(self, query, history=list(), system="", temperature=0.0, stop="", *args, **kwargs):
        msgs = make_gpt_messages(query, system, history)

        try:
            if openai.api_type == "open_ai":
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=msgs,
                    temperature = temperature,
                    stop=stop
                    )
            elif openai.api_type == "azure":
                response = openai.ChatCompletion.create(
                    engine = self.model,
                    messages=msgs,
                    temperature = temperature,
                    stop=stop
                )
            response_text = response['choices'][0]['message']['content']
        except:
            print(traceback.format_exc())
            response_text = ""

        new_history = history[:] + [[query, response_text]]
        return response_text, new_history


class OllamaChatClient(object):
    def __init__(self, model="qwen2.5:7b", host="localhost", port=11434):
        self.model = model
        self.client = OpenAI(
            base_url=f'http://{host}:{port}/v1/',
            api_key='ollama',  # required but ignored
        )

    def chat(self, query, history=list(), system="", temperature=0.0, stop="", *args, **kwargs):
        msgs = make_ollama_chat_messages(query, system, history)
        try:
            response = self.client.chat.completions.create(
                messages=msgs,
                model=self.model,
            )
            response_text = response.choices[0].message.content
        except:
            print(traceback.format_exc())
            response_text = ""
        new_history = history[:] + [[query, response_text]]
        return response_text, new_history


class FastChatClient(object):
    def __init__(self, model="kagentlms_baichuan2_13b_mat", host="localhost", port=8888):
        self.model = model
        self.host = host
        self.port = port

    def chat(self, query, history=list(), system="", temperature=0.0, stop="", *args, **kwargs):
        url = f'http://{self.host}:{self.port}/v1/completions/'

        headers = {"Content-Type": "application/json"}
        if "baichuan" in self.model:
            prompt = self.make_baichuan_prompt(query, system, history)
        elif "qwen" in self.model:
            prompt = self.make_qwen_prompt(query, system, history)
        else:
            prompt = self.make_prompt(query, system, history)
        data = {
            "model": self.model,
            "prompt": prompt,
            "temperature": 0.1,
            "top_p": 0.75,
            "top_k": 40,
            "max_tokens": 512
        }
        resp = requests.post(url=url, json=data, headers=headers)
        response = resp.json() # Check the JSON Response Content documentation below
        response_text = response['choices'][0]['text']

        new_history = history[:] + [[query, response_text]]
        return response_text, new_history

    @staticmethod
    def make_prompt(query, system, history):
        if not history:
            history = list()
        if system:
            prompt = system + "\n"
        else:
            prompt = ''
        for q, r in history:
            prompt += 'User:' + q + '\nAssistant' + r + "\n"
        prompt += query
        return prompt

    @staticmethod
    def make_baichuan_prompt(query, system, history):
        if not history:
            history = list()
        if system:
            prompt = system + "\n"
        else:
            prompt = ''
        for q, r in history:
            prompt += '<reserved_106>' + q + '<reserved_107>' + r 
        prompt += query
        return prompt

    @staticmethod
    def make_qwen_prompt(query, system, history):
        if not history:
            history = list()
        if system:
            prompt = '<|im_start|>' + system + '<|im_end|>\n'
        else:
            prompt = ''
        for q, r in history:
            response = r if r else ''
            prompt += '<|im_start|>user\n' + q + '<|im_end|>\n<|im_start|>assistant\n' + response + "<|im_end|>\n"
        prompt += query
        return prompt

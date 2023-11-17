<p align="left">
    English ｜ <a href="README_ZH.md">中文</a>
</p>
<br><br>

<p align="center">
    <img src="blob/logo.png" width="400"/>
<p>
<br>

<p align="center">
      📚 <a href="https://huggingface.co/datasets/kwaikeg/KAgentInstruct">Dataset</a> | 📚 <a href="https://huggingface.co/datasets/kwaikeg/KAgentBench">Benchmark</a> |🤗 <a href="https://huggingface.co/collections/kwaikeg/kagentlms-6551e685b5ec9f9a077d42ef">Models</a> | 📑 <a href="https://arxiv.org/">Paper</a>
<br>

KwaiAgents is a series of Agent-related works open-sourced by the [KwaiKEG](https://github.com/KwaiKEG) from [Kuaishou Technology](https://www.kuaishou.com/en). The open-sourced content includes:

1. **KAgentSys-Lite**: An experimental Agent Loop implemented based on open-source search engines, browsers, time, calendar, weather, and other tools, which is only missing the memory mechanism and some search capabilities compared to the system in the paper.
2. **KAgentLMs**: A series of large language models with Agent capabilities such as planning, reflection, and tool-use, acquired through the Meta-agent tuning proposed in the paper.
3. **KAgentInstruct**: Fine-tuned data of instructions generated by the Meta-agent in the paper.
4. **KAgentBench**: Over 3,000 human-edited, automated evaluation data for testing Agent capabilities, with evaluation dimensions including planning, tool-use, reflection, concluding, and profiling.

<table>
    <tr>
        <th>Models</th><th>Training Data</th><th>Benchmark Data</th>
    </tr>
    <tr>
        <td><a href="https://huggingface.co/kwaikeg/kagentlms_qwen_7b_mat">Qwen-7B-MAT</a></td>
        <td align="center" rowspan="2"><a href="https://huggingface.co/datasets/kwaikeg/KAgentInstruct">KAgentInstruct</a><p>(upcoming)</p></td>
        <td align="center" rowspan="2"><a href="https://huggingface.co/datasets/kwaikeg/KAgentBench">KAgentBench</a><p>(upcoming)</p></td>
    </tr>
    <tr>
        <td><a href="https://huggingface.co/kwaikeg/kagentlms_baichuan2_13b_mat">Baichuan2-13B-MAT</a></td>
    </tr>
</table>

<br>

<p align="center">
    <img src="blob/overview.png"/>
<p>

## User Guide

### Using AgentLMs
We recommend using [vLLM](https://github.com/vllm-project/vllm) and [FastChat](https://github.com/lm-sys/FastChat) to deploy the model inference service. First, you need to install the corresponding packages (for detailed usage, please refer to the documentation of the two projects):
1. For Qwen-7B-MAT, install the corresponding packages with the following commands
```bash
pip install vllm
pip install "fschat[model_worker,webui]"
```
2. For Baichuan-13B-MAT, install the corresponding packages with the following commands
```bash
pip install "fschat[model_worker,webui]"
pip install vllm==0.2.0
pip install transformers==4.33.2
```

To deploy KAgentLMs, you first need to start the controller in one terminal.
```bash
python -m fastchat.serve.controller
```
Secondly, you should use the following command in another terminal for single-gpu inference service deployment:
```bash
python -m fastchat.serve.vllm_worker --model-path $model_path --trust-remote-code
```
Where `$model_path` is the local path of the model downloaded. If the GPU does not support Bfloat16, you can add `--dtype half` to the command line.

Thirdly, start the REST API server in the third terminal.
```bash
python -m fastchat.serve.openai_api_server --host localhost --port 8888
```

Finally, you can use the curl command to invoke the model same as the OpenAI calling format. Here's an example:
```bash
curl http://localhost:8888/v1/chat/completions \
-H "Content-Type: application/json" \
-d '{"model": "kagentlms_qwen_7b_mat", "messages": [{"role": "user", "content": "Who is Andy Lau"}]}'
```
Here, change `kagentlms_qwen_7b_mat` to the model you deployed.


### Using KAgentSys-Lite
Download and install the KwaiAgents, recommended Python>=3.10
```bash
git clone git@github.com:KwaiKEG/KwaiAgents.git
cd KwaiAgents
python setup.py develop
```

1. **ChatGPT usage**
Declare some environment variables
```
export OPENAI_API_KEY=sk-xxxxx
export WEATHER_API_KEY=xxxxxx
```

The WEATHER_API_KEY is not mandatory, but you need to configure it when asking weather-related questions. You can obtain the API key from [this website](https://www.weatherapi.com/) (Same for local model usage).

```bash
kagentsys --query="Who is Andy Lau's wife?" --llm_name="gpt-3.5-turbo" --lang="en"
```

2. **Local model usage**
> To use a local model, you need to deploy the corresponding model service as described in the previous chapter
```bash
kagentsys --query="Who is Andy Lau's wife?" --llm_name="kagentlms_qwen_7b_mat" \
--use_local_llm --local_llm_host="localhost" --local_llm_port=8888 --lang="en"
```


Full command arguments:

```
options:
  -h, --help            show this help message and exit
  --id ID               ID of this conversation
  --query QUERY         User query
  --history HISTORY     History of conversation
  --llm_name LLM_NAME   the name of llm
  --use_local_llm       Whether to use local llm
  --local_llm_host LOCAL_LLM_HOST
                        The host of local llm service
  --local_llm_port LOCAL_LLM_PORT
                        The port of local llm service
  --tool_names TOOL_NAMES
                        the name of llm
  --max_iter_num MAX_ITER_NUM
                        the number of iteration of agents
  --agent_name AGENT_NAME
                        The agent name
  --agent_bio AGENT_BIO
                        The agent bio, a short description
  --agent_instructions AGENT_INSTRUCTIONS
                        The instructions of how agent thinking, acting, or talking
  --external_knowledge EXTERNAL_KNOWLEDGE
                        The link of external knowledge
  --lang {en,zh}        The language of the overall system
```

**Note**:
1. If you need to use the `browse_website` tool, you need to configure the [chromedriver](https://chromedriver.chromium.org/getting-started) on your server.
2. If the search fails multiple times, it may be because the network cannot access duckduckgo_search. You can solve this by setting the `http_proxy`.

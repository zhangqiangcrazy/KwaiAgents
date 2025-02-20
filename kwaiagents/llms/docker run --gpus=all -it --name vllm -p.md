# 把 chatglm3 的模型放到 /data/models 目录下：
docker run -itd --name fastchat -v /data/models:/data/models --gpus=all -p 8000:8000 pytorch/pytorch:2.0.1-cuda11.7-cudnn8-devel

docker exec -it fastchat bash 

pip3 config set global.index-url https://mirrors.aliyun.com/pypi/simple 
pip3 config set install.trusted-host mirrors.aliyun.com

# 安装依赖环境
pip3 install "fschat[model_worker,webui]"
pip3 install transformers accelerate sentencepiece

#首先启动 controller ：
python3 -m fastchat.serve.controller --host 172.17.0.2 --port 21001 
# 然后启动模型： 说明，必须是本地ip 
python3 -m fastchat.serve.model_worker --load-8bit --model-names chatglm3-6b --model-path /data/models/chatglm3-6b-models --controller-address http://172.17.0.2:21001 --worker-address http://172.17.0.2:8080 --host 0.0.0.0 --port 8080 
# 最后启动 openapi的 兼容服务 地址 8000
python3 -m fastchat.serve.openai_api_server --controller-address http://172.17.0.2:21001 --host 0.0.0.0 --port 8000


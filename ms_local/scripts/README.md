cd /workspace/vllm/ms_local/scrips

./01_sysdeps.sh
./02_venv.sh
./03_build_vllm.sh

export HF_TOKEN=hf_xxx
./04_hf_login.sh
./05_download_model.sh meta-llama/Meta-Llama-3-8B-Instruct
./enter_venv.sh

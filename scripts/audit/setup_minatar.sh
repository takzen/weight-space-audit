set -e
cd $HOME/qwen-control
command -v uv >/dev/null || export PATH=$HOME/.local/bin:$PATH
uv venv --python 3.12 minatar-env 2>&1 | tail -1
uv pip install --python minatar-env/bin/python "minatar==1.0.15" numpy 2>&1 | tail -8
minatar-env/bin/python -c "import minatar, numpy, sys; print('minatar at', minatar.__file__); print('numpy', numpy.__version__)"
ls minatar-env/lib/python3.12/site-packages/minatar/environments/

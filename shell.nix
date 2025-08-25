{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python310
    pkgs.python310Packages.pip
    pkgs.python310Packages.virtualenv
    pkgs.postgresql
  ];

  shellHook = ''
  export PIP_DISABLE_PIP_VERSION_CHECK=1
  export PYTHONPATH=$PYTHONPATH:$(pwd)

  if [ ! -d .venv ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
  fi

  source .venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt

  echo "Virtual environment ready. Python $(python --version)"
'';
}

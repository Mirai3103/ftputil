# install required packages
pip install -r requirements.txt
rm -rf dist
rm -rf build
rm -rf main.spec
python -m PyInstaller --onefile main.py
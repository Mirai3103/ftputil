REPO="https://github.com/Mirai3103/ftputil.git"
# Clone the repository
rm -rf temp
git clone --depth 1 $REPO temp
cd temp
# Install required packages
pip install -r requirements.txt
rm -rf dist
rm -rf build
rm -rf main.spec
python -m PyInstaller --onefile main.py
sudo chmod +x ./dist/main
sudo cp ./dist/main /usr/sbin/ftputil
mv ./dist/main /usr/local/bin/ftputil
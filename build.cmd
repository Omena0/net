
py -m nuitka --standalone --onefile^
 --product-name="Fr-Browser" --product-version=1.1.4 --file-description="The Net-project Web Browser" --copyright="Copyright © 2024 Omena0. All rights reserved."^
 --output-dir="__build"^
 --deployment --python-flag="-OO" --python-flag="-S"^
 --output-filename="Fr-browser.exe"^
 client/client.py

xcopy "__build\Fr-browser.exe" "dist" /c /f /i /y /z

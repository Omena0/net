
pyinstaller --onefile --specpath "build/spec" --workpath "build" --distpath "dist" client/client.py
pyinstaller --onefile --specpath "build/spec" --workpath "build" --distpath "dist" dns/dns.py
pyinstaller --onefile --specpath "build/spec" --workpath "build" --distpath "dist" server/server.py



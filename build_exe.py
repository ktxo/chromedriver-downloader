import PyInstaller.__main__
import platform

app_name = "chromedriver_downloader"
app_ico = "images/app.png"

if platform.system() == "Windows":
    sep = ";"
else:
    sep = ":"
PyInstaller.__main__.run([
    "chromedriver_downloader.py",
    "--onefile",
    "--clean",
    "--noconsole",
    "--windowed",
    f"--name={app_name}",
    f"--icon=images/{app_ico}",
    f"--add-data=images/*{sep}images/"
])


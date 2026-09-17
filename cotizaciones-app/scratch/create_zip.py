import os
import zipfile

source_dir = r"c:\Users\karen\Downloads\Proyectos de A\cotizaciones-app"
zip_path = r"c:\Users\karen\Downloads\Proyectos de A\cotizaciones-app.zip"

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(source_dir):
        # Exclude scratch directory from zip
        dirs[:] = [d for d in dirs if d not in ['scratch', '__pycache__', '.git']]
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, source_dir)
            zipf.write(file_path, arcname)

print(f"ZIP file created successfully at: {zip_path}")
print(f"Size: {os.path.getsize(zip_path)} bytes")

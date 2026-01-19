
import os
import subprocess

def show_images():
    folder = "DataVisualisation"
    if not os.path.exists(folder):
        print(f"Error: {folder} directory not found.")
        return

    images = [f for f in os.listdir(folder) if f.endswith(".png")]
    if not images:
        print("No visualizations found in DataVisualisation/. Run Start.py first.")
        return

    print(f"Opening {len(images)} visualizations...")
    for img in images:
        path = os.path.join(folder, img)
        print(f" - Opening {img}")
        # 'open' works on macOS to launch the default image viewer
        subprocess.run(["open", path])

if __name__ == "__main__":
    show_images()

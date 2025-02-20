import os
import shutil
import subprocess
import sys
import glob
import site

def clean_build_artifacts():
    """Remove build, dist, and *.egg-info directories."""
    paths_to_remove = ["build", "dist"]
    for path in paths_to_remove:
        if os.path.exists(path):
            print(f"Removing '{path}' directory...")
            shutil.rmtree(path)
        else:
            print(f"'{path}' directory not found, skipping...")

    # Remove any .egg-info directories (should not be necessary but just in case ...)
    for item in os.listdir("."):
        if item.endswith(".egg-info") and os.path.isdir(item):
            print(f"Removing '{item}' directory...")
            shutil.rmtree(item)

def build_and_install():
    # 1. Build the wheel
    print("Building wheel with python -m build...")
    result = subprocess.run([sys.executable, "-m", "build"], check=True)
    if result.returncode != 0:
        sys.exit(result.returncode)

    # 2. Install the wheel from dist/
    wheel_files = glob.glob("dist/*.whl")
    if not wheel_files:
        print("No wheel files found in 'dist/'")
        sys.exit(1)
    wheel_file = wheel_files[0]

    print(f"Installing {wheel_file}...")
    # Note: --upgrade to ensure any existing older version is replaced
    result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", wheel_file], check=True)
    if result.returncode != 0:
        sys.exit(result.returncode)

    print("Install successful!")

def set_pythonpath():
    """Set the PYTHONPATH to the user's local site-packages directory if not already set."""
    user_site = site.getusersitepackages()
    current_pythonpath = os.environ.get('PYTHONPATH', '')
    if user_site not in current_pythonpath:
        new_path = f"{current_pythonpath}:{user_site}" if current_pythonpath else user_site
        os.environ['PYTHONPATH'] = new_path
        print(f"PYTHONPATH set to: {os.environ['PYTHONPATH']}")
    else:
        print(f"PYTHONPATH already set to: {current_pythonpath}")

def test_install():
    # 3. Test the installed package
    print("Testing the installed package...")
    try:
        subprocess.run(
            [sys.executable, '-c', 'import agonutils; agonutils.hello()'],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("Package works!")
    except subprocess.CalledProcessError as e:
        print("Package failed to run!\nError output:")
        print(e.stderr)
        sys.exit(e.returncode)

if __name__ == '__main__':
    clean_build_artifacts()
    build_and_install()
    set_pythonpath()
    test_install()

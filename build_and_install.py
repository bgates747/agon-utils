import os
import shutil
import subprocess
import sys
import site
import platform

def detect_environment():
    """Detect the development environment and set platform-specific variables."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if 'linux' in system:
        if 'aarch64' in machine:
            env = 'pios_arm64'
        else:
            env = 'ubuntu_x64'
    elif 'darwin' in system:
        env = 'macos'
    else:
        print("Unsupported environment!")
        sys.exit(1)

    print(f"Operating System: {platform.system()}")
    print(f"Machine Type: {platform.machine()}")
    print(f"Environment detected: {env}")

    return env

def configure_vscode():
    """Adjust the .vscode/c_cpp_properties.json file for the detected environment."""
    env = detect_environment()
    config_file = '.vscode/c_cpp_properties.json'

    if os.path.exists(config_file):
        import json

        with open(config_file, 'r') as file:
            config_data = json.load(file)

        # Set the appropriate configuration
        for config in config_data.get('configurations', []):
            if env in config['name'].lower():
                config_data['configurations'] = [config]
                break

        with open(config_file, 'w') as file:
            json.dump(config_data, file, indent=4)

        print(f"VSCode configuration updated for {env}.")
    else:
        print(f"{config_file} not found. Skipping VSCode configuration.")

def check_python_dev_headers():
    """Check if Python development headers are available."""
    python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
    pyenv_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    venv_include_dir = os.path.join(sys.prefix, 'include', python_version)
    pyenv_include_dir = os.path.expanduser(f"~/.pyenv/versions/{pyenv_version}/include/{python_version}")
    
    print(f"Checking for Python development headers in: {venv_include_dir} or {pyenv_include_dir}")
    
    # Check for the headers in both paths
    if os.path.exists(os.path.join(venv_include_dir, 'Python.h')):
        print(f"Python development headers found in virtual environment at: {venv_include_dir}")
    elif os.path.exists(os.path.join(pyenv_include_dir, 'Python.h')):
        print(f"Python development headers found in pyenv at: {pyenv_include_dir}")
    else:
        env = detect_environment()
        env_description = "Ubuntu Linux x86_64" if env == 'ubuntu_x64' else "PIOS ARM64" if env == 'pios_arm64' else "macOS"
        print(f"Error: Python development headers not found at {venv_include_dir} or {pyenv_include_dir}.")
        print(f"For {env_description}, install them using the following command and try again:")
        if env == 'ubuntu_x64' or env == 'pios_arm64':
            print(f"  sudo apt install {python_version}-dev")
        elif env == 'macos':
            print("  brew install python@3")
        sys.exit(1)

def clean_build():
    """Remove the build directory if it exists."""
    build_dir = 'build'
    if os.path.exists(build_dir):
        print(f"Cleaning {build_dir} directory...")
        shutil.rmtree(build_dir)
    else:
        print(f"{build_dir} directory not found, nothing to clean.")

def build_project():
    """Run the setup.py build command."""
    print("Starting the build process...")
    print(f"Using Python executable: {sys.executable}")
    try:
        result = subprocess.run([sys.executable, 'setup.py', 'build'], check=True)
        if result.returncode == 0:
            print("Build successful!")
    except subprocess.CalledProcessError as e:
        print("Build failed!")
        print(f"Command '{e.cmd}' returned non-zero exit status {e.returncode}.")
        sys.exit(e.returncode)

def local_install():
    """Run the setup.py install command in the virtual environment."""
    print("Starting the installation process in the virtual environment...")
    try:
        result = subprocess.run([sys.executable, 'setup.py', 'install'], check=True)
        if result.returncode == 0:
            print("Install successful!")
    except subprocess.CalledProcessError as e:
        print("Install failed!")
        print(f"Command '{e.cmd}' returned non-zero exit status {e.returncode}.")
        sys.exit(e.returncode)

def set_pythonpath():
    """Set the PYTHONPATH to the user's local site-packages directory."""
    user_site = site.getusersitepackages()
    current_pythonpath = os.environ.get('PYTHONPATH', '')

    print(f"User site-packages directory detected at: {user_site}")
    separator = ':'  # UNIX-like separator
    if user_site not in current_pythonpath:
        os.environ['PYTHONPATH'] = f"{current_pythonpath}{separator}{user_site}" if current_pythonpath else user_site
        print(f"PYTHONPATH set to: {os.environ['PYTHONPATH']}")
    else:
        print(f"PYTHONPATH already set to: {os.environ['PYTHONPATH']}")

def test_install():
    """Test the installed package by importing it and calling a function."""
    print("Testing the installed package...")
    try:
        result = subprocess.run([sys.executable, '-c', 'import agonutils; agonutils.hello()'], check=True)
        if result.returncode == 0:
            print("Package works!")
    except subprocess.CalledProcessError:
        print("Package failed to run!")
        sys.exit(1)

if __name__ == '__main__':
    print("Starting build_and_install.py...")
    configure_vscode()
    check_python_dev_headers()
    clean_build()
    build_project()
    local_install()
    set_pythonpath()
    test_install()
    print("Process completed.")

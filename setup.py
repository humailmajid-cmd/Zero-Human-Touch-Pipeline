"""
Setup Script - Initialize the Zero Human Touch Pipeline
"""
import os
import sys
import subprocess
import shutil

def run_command(cmd, description):
    """Run a shell command and report status"""
    print(f"\
[Setup] {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {description} - OK")
            return True
        else:
            print(f"✗ {description} - FAILED")
            if result.stderr:
                print(f"  Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ {description} - ERROR: {e}")
        return False

def check_requirements():
    """Check system requirements"""
    print("\
[Setup] Checking requirements...")
    
    requirements = {
        'Python 3.9+': 'python --version',
        'Node.js 16+': 'node --version',
        'Git': 'git --version',
        'GitHub CLI': 'gh --version'
    }
    
    all_ok = True
    for name, cmd in requirements.items():
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✓ {name}: {result.stdout.strip()}")
            else:
                print(f"  ✗ {name}: NOT FOUND")
                all_ok = False
        except:
            print(f"  ✗ {name}: NOT FOUND")
            all_ok = False
    
    return all_ok

def setup_python():
    """Setup Python virtual environment"""
    print("\
[Setup] Setting up Python environment...")
    
    # Create virtual environment
    venv_path = 'venv'
    if os.path.exists(venv_path):
        print(f"  Virtual environment already exists at {venv_path}")
    else:
        if run_command('python -m venv venv', 'Creating virtual environment'):
            print(f"  Virtual environment created at {venv_path}")
    
    # Determine pip path
    if sys.platform == 'win32':
        pip_cmd = 'venv\Scripts\pip'
        python_cmd = 'venv\Scripts\python'
    else:
        pip_cmd = 'venv/bin/pip'
        python_cmd = 'venv/bin/python'
    
    # Upgrade pip
    run_command(f'{pip_cmd} install --upgrade pip', 'Upgrading pip')
    
    # Install requirements
    if os.path.exists('requirements.txt'):
        run_command(f'{pip_cmd} install -r requirements.txt', 'Installing Python dependencies')
    
    # Install Playwright browsers
    run_command(f'{python_cmd} -m playwright install', 'Installing Playwright browsers')
    
    print(f"\
  To activate: source {venv_path}/bin/activate  (Linux/Mac)")
    print(f"  To activate: {venv_path}\Scripts\activate  (Windows)")

def setup_env():
    """Setup environment file"""
    print("\
[Setup] Setting up environment configuration...")
    
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print("  ✓ Created .env from .env.example")
            print("  ⚠ IMPORTANT: Edit .env and add your credentials!")
        else:
            print("  ✗ .env.example not found")
    else:
        print("  .env already exists")

def setup_dirs():
    """Create necessary directories"""
    print("\
[Setup] Creating directories...")
    
    dirs = ['logs', 'output', 'stages', 'utils']
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"  ✓ Created {d}/")

def setup_github():
    """Setup GitHub authentication"""
    print("\
[Setup] GitHub authentication...")
    
    try:
        result = subprocess.run('gh auth status', shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✓ GitHub CLI authenticated")
        else:
            print("  ⚠ GitHub CLI not authenticated")
            print("  Run: gh auth login")
    except:
        print("  ✗ GitHub CLI not found - please install it")

def main():
    """Run setup"""
    print("\
" + "="*60)
    print("ZERO HUMAN TOUCH PIPELINE - SETUP")
    print("="*60)
    
    # Check requirements
    if not check_requirements():
        print("\
✗ Missing required tools. Please install them first.")
        sys.exit(1)
    
    # Setup steps
    setup_dirs()
    setup_env()
    setup_python()
    setup_github()
    
    print("\
" + "="*60)
    print("SETUP COMPLETE")
    print("="*60)
    print("\
Next steps:")
    print("1. Activate Python venv:")
    if sys.platform == 'win32':
        print("   venv\Scripts\activate")
    else:
        print("   source venv/bin/activate")
    print("2. Edit .env with your credentials")
    print("3. Run pipeline manually: python orchestrate.py")
    print("4. Or start scheduler: python scheduler.py")
    print("\
See README.md for detailed instructions.")

if __name__ == '__main__':
    main()

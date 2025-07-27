import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Platform: {sys.platform}")

# Check if this is the issue - Python 3.13 might be too new
major, minor = sys.version_info[:2]
print(f"Version tuple: {major}.{minor}")

if major == 3 and minor >= 13:
    print("⚠️  You're using Python 3.13+ which is very new")
    print("Some packages may not have compatible wheels yet")
    print("This might be causing the pydub issue")
elif major == 3 and minor >= 11:
    print("✅ Python version should be compatible")
else:
    print("⚠️  Python version might be too old")

# Check available audio modules
print("\n🔍 Checking built-in audio modules:")
modules = ['audioop', 'wave', 'array']
for module in modules:
    try:
        __import__(module)
        print(f"✅ {module} available")
    except ImportError:
        print(f"❌ {module} missing")

input("\nPress Enter to continue...")
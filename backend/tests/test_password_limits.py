
import sys
import os
import pytest
from passlib.context import CryptContext

# Add the parent directory to sys.path to allow importing app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.auth import get_password_hash, verify_password, process_password

def test_process_password_normal():
    password = "normal_password"
    processed = process_password(password)
    assert processed == password

def test_process_password_boundary():
    # Create a 72-byte password
    password = "a" * 72
    processed = process_password(password)
    assert len(processed.encode('utf-8')) == 72
    assert processed == password

def test_process_password_too_long():
    # Create a 73-byte password
    password = "a" * 73
    processed = process_password(password)
    assert len(processed.encode('utf-8')) == 72
    assert processed == "a" * 72

def test_hashing_normal_password():
    password = "my_secure_password"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)

def test_hashing_long_password():
    # Create a very long password
    long_password = "b" * 100
    hashed = get_password_hash(long_password)
    
    # Verify the original long password works (it will be truncated internally during verification)
    assert verify_password(long_password, hashed)
    
    # Verify the truncated version also works (since that's what was actually hashed)
    truncated_password = "b" * 72
    assert verify_password(truncated_password, hashed)
    
    # Verify a different password fails
    assert not verify_password("wrong_password", hashed)

if __name__ == "__main__":
    # Manually run tests if pytest not installed
    try:
        print("Testing process_password_normal...")
        test_process_password_normal()
        print("PASS")

        print("Testing process_password_boundary...")
        test_process_password_boundary()
        print("PASS")

        print("Testing process_password_too_long...")
        test_process_password_too_long()
        print("PASS")
        
        print("Testing hashing_normal_password...")
        test_hashing_normal_password()
        print("PASS")
        
        print("Testing hashing_long_password...")
        test_hashing_long_password()
        print("PASS")

        print("ALL TESTS PASSED")
    except Exception as e:
        print(f"TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

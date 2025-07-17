#!/usr/bin/env python3
"""
GutIntel Project Setup Script

This script sets up the development environment for the GutIntel project.
It performs the following tasks:
1. Creates .env file from .env.example if it doesn't exist
2. Creates necessary directories
3. Validates the configuration
4. Optionally runs database migrations
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from typing import Optional

# ANSI color codes for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def print_colored(message: str, color: str = Colors.WHITE, bold: bool = False):
    """Print colored message to console"""
    prefix = f"{Colors.BOLD if bold else ''}{color}"
    print(f"{prefix}{message}{Colors.END}")


def print_header(message: str):
    """Print header message"""
    print_colored(f"\n{'='*60}", Colors.CYAN, bold=True)
    print_colored(f"{message}", Colors.CYAN, bold=True)
    print_colored(f"{'='*60}", Colors.CYAN, bold=True)


def print_success(message: str):
    """Print success message"""
    print_colored(f"✓ {message}", Colors.GREEN)


def print_warning(message: str):
    """Print warning message"""
    print_colored(f"⚠ {message}", Colors.YELLOW)


def print_error(message: str):
    """Print error message"""
    print_colored(f"✗ {message}", Colors.RED)


def print_info(message: str):
    """Print info message"""
    print_colored(f"ℹ {message}", Colors.BLUE)


def check_python_version():
    """Check if Python version is compatible"""
    print_header("Checking Python Version")
    
    if sys.version_info < (3, 8):
        print_error("Python 3.8 or higher is required")
        print_error(f"Current version: {sys.version}")
        sys.exit(1)
    
    print_success(f"Python version {sys.version.split()[0]} is compatible")


def create_env_file(force: bool = False):
    """Create .env file from .env.example"""
    print_header("Setting up Environment File")
    
    env_example_path = Path(".env.example")
    env_path = Path(".env")
    
    if not env_example_path.exists():
        print_error(".env.example file not found")
        sys.exit(1)
    
    if env_path.exists() and not force:
        print_warning(".env file already exists")
        response = input("Do you want to overwrite it? (y/N): ").lower().strip()
        if response != 'y':
            print_info("Skipping .env file creation")
            return
    
    try:
        shutil.copy2(env_example_path, env_path)
        print_success(".env file created successfully")
        print_info("Please edit .env file with your actual configuration values")
    except Exception as e:
        print_error(f"Failed to create .env file: {e}")
        sys.exit(1)


def create_directories():
    """Create necessary directories"""
    print_header("Creating Directories")
    
    directories = [
        "logs",
        "uploads",
        "tmp",
        "backups",
        "static",
        "media"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            print_success(f"Created directory: {directory}")
        except Exception as e:
            print_error(f"Failed to create directory {directory}: {e}")


def validate_requirements():
    """Validate that all required packages are installed"""
    print_header("Validating Requirements")
    
    requirements_path = Path("requirements.txt")
    if not requirements_path.exists():
        print_warning("requirements.txt not found")
        return
    
    print_info("Checking if required packages are installed...")
    
    try:
        import pip
        import pkg_resources
        
        with open(requirements_path, 'r') as f:
            requirements = f.read().splitlines()
        
        # Filter out comments and empty lines
        requirements = [
            req.strip() for req in requirements 
            if req.strip() and not req.strip().startswith('#')
        ]
        
        missing_packages = []
        for requirement in requirements:
            try:
                # Parse requirement (handle version specifiers)
                req_name = requirement.split('>=')[0].split('==')[0].split('<=')[0].split('>')[0].split('<')[0].split('!=')[0]
                pkg_resources.require(req_name)
                print_success(f"✓ {req_name}")
            except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
                missing_packages.append(requirement)
                print_error(f"✗ {req_name}")
        
        if missing_packages:
            print_warning(f"Missing packages: {', '.join(missing_packages)}")
            print_info("Run 'pip install -r requirements.txt' to install missing packages")
        else:
            print_success("All required packages are installed")
    
    except Exception as e:
        print_warning(f"Could not validate requirements: {e}")


def validate_configuration():
    """Validate configuration by trying to load settings"""
    print_header("Validating Configuration")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, str(Path.cwd()))
        
        from config import settings
        
        print_success("Configuration loaded successfully")
        print_info(f"Environment: {settings.environment}")
        print_info(f"Database URL: {settings.database.url.split('@')[0]}@***")  # Hide password
        print_info(f"API Host: {settings.api.host}:{settings.api.port}")
        print_info(f"Log Level: {settings.logging.level}")
        
        # Validate critical settings
        if settings.environment == "production":
            if settings.security.secret_key == "your-secret-key-here-change-in-production":
                print_error("SECRET_KEY must be changed in production environment")
                return False
        
        print_success("Configuration validation passed")
        return True
        
    except Exception as e:
        print_error(f"Configuration validation failed: {e}")
        return False


def run_database_migrations():
    """Run database migrations (placeholder for future implementation)"""
    print_header("Database Migrations")
    
    print_info("Database migration system not implemented yet")
    print_info("This will be added when Alembic is integrated")


def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="GutIntel Project Setup")
    parser.add_argument(
        "--force-env", 
        action="store_true", 
        help="Force overwrite existing .env file"
    )
    parser.add_argument(
        "--skip-validation", 
        action="store_true", 
        help="Skip configuration validation"
    )
    parser.add_argument(
        "--skip-requirements", 
        action="store_true", 
        help="Skip requirements validation"
    )
    
    args = parser.parse_args()
    
    print_colored("🚀 GutIntel Project Setup", Colors.MAGENTA, bold=True)
    print_colored("Setting up your development environment...\n", Colors.WHITE)
    
    # Check Python version
    check_python_version()
    
    # Create .env file
    create_env_file(force=args.force_env)
    
    # Create necessary directories
    create_directories()
    
    # Validate requirements
    if not args.skip_requirements:
        validate_requirements()
    
    # Validate configuration
    if not args.skip_validation:
        config_valid = validate_configuration()
        if not config_valid:
            print_error("Setup completed with configuration errors")
            print_info("Please fix the configuration issues before running the application")
            sys.exit(1)
    
    # Database migrations (placeholder)
    run_database_migrations()
    
    print_header("Setup Complete")
    print_success("GutIntel project setup completed successfully!")
    print_info("Next steps:")
    print_info("1. Edit .env file with your actual configuration values")
    print_info("2. Install requirements: pip install -r requirements.txt")
    print_info("3. Run the application: python -m uvicorn main:app --reload")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
FLOCSS Frontend Project Initializer

Creates a new frontend project with FLOCSS structure.

Usage:
    python3 init_project.py <project-name> --path <output-directory>

Example:
    python3 init_project.py my-website --path ./projects
"""

import argparse
import os
import shutil
from pathlib import Path


def get_template_dir():
    """Get the path to the template directory."""
    script_dir = Path(__file__).parent.absolute()
    template_dir = script_dir.parent / "assets" / "template"
    return template_dir


def create_project(project_name: str, output_path: str):
    """Create a new FLOCSS project."""
    template_dir = get_template_dir()

    if not template_dir.exists():
        print(f"Error: Template directory not found at {template_dir}")
        return False

    # Create output directory
    output_dir = Path(output_path).absolute()
    project_dir = output_dir / project_name

    if project_dir.exists():
        print(f"Error: Project directory already exists: {project_dir}")
        return False

    # Copy template to project directory
    try:
        shutil.copytree(template_dir, project_dir)
        print(f"✅ Created project: {project_dir}")

        # Print structure
        print("\n📁 Project Structure:")
        for root, dirs, files in os.walk(project_dir):
            level = root.replace(str(project_dir), '').count(os.sep)
            indent = '  ' * level
            folder_name = os.path.basename(root)
            if level == 0:
                print(f"{project_name}/")
            else:
                print(f"{indent}{folder_name}/")

            subindent = '  ' * (level + 1)
            for file in files:
                print(f"{subindent}{file}")

        print(f"\n✅ Project '{project_name}' initialized successfully!")
        print("\nNext steps:")
        print(f"  1. cd {project_dir}")
        print("  2. Open index.html in browser")
        print("  3. Start customizing your project")

        return True

    except Exception as e:
        print(f"Error creating project: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Create a new FLOCSS frontend project"
    )
    parser.add_argument(
        "project_name",
        help="Name of the project to create"
    )
    parser.add_argument(
        "--path",
        default=".",
        help="Output directory (default: current directory)"
    )

    args = parser.parse_args()

    # Validate project name
    if not args.project_name.replace("-", "").replace("_", "").isalnum():
        print("Error: Project name should only contain alphanumeric characters, hyphens, and underscores")
        return

    create_project(args.project_name, args.path)


if __name__ == "__main__":
    main()

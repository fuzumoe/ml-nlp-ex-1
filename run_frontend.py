#!/usr/bin/env python3
import logging
import os
import subprocess
import sys
from pathlib import Path

LOG = logging.getLogger(__name__)


def main():
    """Run the Streamlit application."""
    # Get the base directory of the project
    base_dir = Path(__file__).parent.absolute()

    # Set the app file path
    app_path = base_dir / "app" / "frontend" / "app.py"

    if not app_path.exists():
        LOG.error(f"App file does not exist: {app_path}")
        sys.exit(1)

    LOG.info(f"Starting Streamlit app from: {app_path}")

    # Create temp directory if it doesn't exist
    temp_dir = base_dir / "temp"
    temp_dir.mkdir(exist_ok=True, parents=True)
    LOG.info(f"Ensured temp directory exists at: {temp_dir}")

    # Set PYTHONPATH to include project root
    os.environ["PYTHONPATH"] = str(base_dir)

    # Run the Streamlit app
    streamlit_args = ["streamlit", "run", str(app_path)]

    # Add any command line arguments passed to this script
    if len(sys.argv) > 1:
        streamlit_args.extend(sys.argv[1:])

    # Execute Streamlit
    LOG.info(f"Running command: {' '.join(streamlit_args)}")
    try:
        subprocess.run(streamlit_args, check=True)  # noqa: S603
    except subprocess.CalledProcessError as e:
        message = str(e)
        LOG.exception(f"Error running Streamlit: {message}")
        sys.exit(1)
    except KeyboardInterrupt:
        LOG.exception("\nStreamlit application stopped")
        sys.exit(0)


if __name__ == "__main__":
    main()

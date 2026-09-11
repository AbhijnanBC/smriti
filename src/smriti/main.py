"""
Main entry point for the SMRITI platform.
Provides a unified CLI for running the pipeline and launching the dashboard.
"""

import argparse
import subprocess
import sys

from smriti.core.logger import get_logger, setup_logging
from smriti.core.paths import RAW_DATA_DIR, SRC_DIR

setup_logging()
logger = get_logger(__name__)


def run_pipeline(start: int, stop: int) -> None:
    """Executes the SMRITI backend pipeline."""
    logger.info("smriti pipeline starting", start_phase=start, stop_phase=stop)
    try:
        from smriti.pipeline.runner import PipelineRunner

        runner = PipelineRunner(input_dirs=[RAW_DATA_DIR])
        success = runner.run(start_from=start, stop_at=stop)

        if success:
            logger.info("smriti pipeline completed successfully")
        else:
            logger.error("smriti pipeline failed")
            sys.exit(1)

    except Exception as e:
        logger.error("fatal pipeline error", error=str(e), exc_info=True)
        sys.exit(1)


def run_dashboard() -> None:
    """Launches the Streamlit interaction session."""
    logger.info("launching smriti dashboard")
    dashboard_path = SRC_DIR / "dashboard" / "app.py"

    if not dashboard_path.exists():
        logger.error("dashboard entry point not found", path=str(dashboard_path))
        sys.exit(1)

    try:
        subprocess.run(["streamlit", "run", str(dashboard_path)], check=True)
    except KeyboardInterrupt:
        logger.info("dashboard terminated by user")
    except Exception as e:
        logger.error("dashboard process failed", error=str(e))
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="SMRITI: Epistemic Knowledge Graph Platform")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Pipeline Command
    pipe_parser = subparsers.add_parser("pipeline", help="Execute the batch processing pipeline")
    pipe_parser.add_argument(
        "--start", type=int, default=1, help="Phase to start from (default: 1)"
    )
    pipe_parser.add_argument("--stop", type=int, default=12, help="Phase to stop at (default: 12)")

    # Dashboard Command
    subparsers.add_parser("ui", help="Launch the Phase 10 Interactive Dashboard")

    args = parser.parse_args()

    if args.command == "pipeline":
        run_pipeline(args.start, args.stop)
    elif args.command == "ui":
        run_dashboard()


if __name__ == "__main__":
    main()

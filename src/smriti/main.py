"""
Main entry point for the SMRITI pipeline.
Initializes core infrastructure, wires up phases, and triggers the runner.
"""

from smriti.core.logger import setup_logging, get_logger
from smriti.core.paths import RAW_DATA_DIR

setup_logging()
logger = get_logger(__name__)


def main():
    logger.info("smriti application starting")

    try:
        from smriti.pipeline.runner import PipelineRunner

        runner = PipelineRunner(input_dirs=[RAW_DATA_DIR])

        # Run Phase 1 + Phase 2 (stop_at=2 to run only these phases during development)
        success = runner.run(start_from=1, stop_at=2)

        if success:
            logger.info("smriti pipeline completed successfully")
        else:
            logger.error("smriti pipeline failed")

    except Exception as e:
        logger.error("fatal pipeline error", error=str(e), exc_info=True)


if __name__ == "__main__":
    main()
# cli.py
import argparse
from runner import run_for_job


def main():
    parser = argparse.ArgumentParser(description="Resume screening tool")
    parser.add_argument(
        "--job-id",
        required=True,
        help='Job ID (e.g., "SDE-III-Pune")',
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to config.yaml (default: config.yaml)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print progress to console",
    )

    args = parser.parse_args()

    run_for_job(job_id=args.job_id, config_path=args.config, verbose=args.verbose)
    print(f"✓ Screening complete for job: {args.job_id}")


if __name__ == "__main__":
    main()

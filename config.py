# config.py
from pathlib import Path
import os
import yaml


DEFAULT_CONFIG_PATH = Path("config.yaml")


def load_config(config_path: str | Path | None = None) -> dict:
    """Load global config from config.yaml."""
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    return cfg


def get_job_config(job_id: str, config: dict) -> dict:
    """Return job-specific settings for a given job_id."""
    jobs = config.get("jobs", {})
    if job_id not in jobs:
        raise ValueError(f"Job ID '{job_id}' not found in config.")
    job_cfg = jobs[job_id].copy()

    # Optional: override base path with env var (for future shared drive)
    base_override = os.getenv("HIRING_DATA_PATH")
    if base_override and not job_cfg.get("base_path"):
        job_cfg["base_path"] = str(Path(base_override) / job_id)

    # Defaults
    job_cfg.setdefault("jd_filename", "jd.txt")
    job_cfg.setdefault("resumes_dirname", "resumes")
    job_cfg.setdefault("output_filename", "screening_results.xlsx")

    return job_cfg


def validate_job_id(job_id: str, config: dict) -> bool:
    """Check if job_id exists in config."""
    return job_id in config.get("jobs", {})

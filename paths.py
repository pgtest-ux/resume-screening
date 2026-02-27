# paths.py
from pathlib import Path


def get_job_base_path(job_config: dict) -> Path:
    base = job_config.get("base_path")
    if not base:
        raise ValueError("job_config.base_path is required.")
    return Path(base)


def get_jd_path(job_config: dict) -> Path:
    return get_job_base_path(job_config) / job_config["jd_filename"]


def get_resumes_dir(job_config: dict) -> Path:
    return get_job_base_path(job_config) / job_config["resumes_dirname"]


def get_output_excel_path(job_config: dict) -> Path:
    return get_job_base_path(job_config) / job_config["output_filename"]


def get_logs_dir(job_config: dict) -> Path:
    return get_job_base_path(job_config) / "logs"


def ensure_dir_exists(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

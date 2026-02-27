# runner.py
from config import load_config, get_job_config
from paths import (
    get_jd_path,
    get_resumes_dir,
    get_output_excel_path,
    get_logs_dir,
    ensure_dir_exists,
)
from jd_parser import read_jd_text, extract_scoring_schema
from resume_parser import list_resumes, extract_resume_text
from scoring import score_resume
from excel_writer import init_excel_if_missing, upsert_candidate_row
from llm_client import create_llm_client


def run_for_job(job_id: str, config_path: str = "config.yaml", verbose: bool = True) -> None:
    config = load_config(config_path)
    job_cfg = get_job_config(job_id, config)

    if verbose:
        print(f"Running resume screening for job: {job_id}")

    jd_path = get_jd_path(job_cfg)
    resumes_dir = get_resumes_dir(job_cfg)
    excel_path = get_output_excel_path(job_cfg)
    logs_dir = get_logs_dir(job_cfg)
    ensure_dir_exists(logs_dir)

    provider = config.get("app", {}).get("llm_provider", "groq")
    llm_client = create_llm_client(provider=provider)

    # 1. JD → schema
    jd_text = read_jd_text(jd_path)
    if verbose:
        print(f"Loaded JD from {jd_path}")
    schema = extract_scoring_schema(jd_text, llm_client)
    if verbose:
        print("Extracted scoring schema from JD.")

    # 2. Prepare Excel
    ensure_dir_exists(excel_path.parent)
    init_excel_if_missing(excel_path, schema)
    if verbose:
        print(f"Initialized Excel at {excel_path}")

    # 3. Process resumes
    resume_files = list_resumes(resumes_dir)
    if verbose:
        print(f"Found {len(resume_files)} resumes in {resumes_dir}")

    for idx, path in enumerate(resume_files, start=1):
        if verbose:
            print(f"[{idx}/{len(resume_files)}] Processing {path.name}...")
        resume_text = extract_resume_text(path)
        score_result = score_resume(jd_text, schema, resume_text, llm_client)
        if not score_result.get("candidate_name"):
            score_result["candidate_name"] = path.stem
        upsert_candidate_row(excel_path, score_result)

    if verbose:
        print(f"Done. Results written to: {excel_path}")

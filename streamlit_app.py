# streamlit_app.py
import streamlit as st
import yaml
from runner import run_for_job

def load_config_from_yaml(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def main():
    st.title("Resume Screener")

    # Load config from YAML file
    config_file = 'config.yaml'
    config = load_config_from_yaml(config_file)
    print(config)

    # Select job ID from dropdown
    job_ids = list(config['jobs'].keys())
    selected_job_id = st.selectbox("Select Job ID", job_ids)
    
    # Run screening
    if st.button("Run Screening"):
        st.spinner("Running screening...")

        try:
            run_for_job(selected_job_id, verbose=True)
            st.success("Screening completed successfully.")
        except Exception as e:
            st.error(str(e))

        # Display output Excel file path
        output_excel_path = config['jobs'][selected_job_id]['output_filename']
        st.write(f"Output Excel file path: {output_excel_path}")

if __name__ == "__main__":
    main()
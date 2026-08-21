import os
import json
import subprocess
import shutil
from dotenv import load_dotenv

XAI_OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")

def get_snapshot():
    score_path = os.path.join(XAI_OUT, "score_breakdown.json")
    ml_path = os.path.join(XAI_OUT, "cluster_delta_report.json")
    
    with open(score_path, "r") as f:
        scores = json.load(f)
    
    with open(ml_path, "r") as f:
        ml = json.load(f)
        
    return scores, ml

def run_pipeline(use_gemini=False):
    env = os.environ.copy()
    if not use_gemini:
        if "GEMINI_API_KEY" in env:
            del env["GEMINI_API_KEY"]
    
    # Run the xai engine
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    subprocess.run(["python", "-m", "xai.xai_engine"], env=env, cwd=repo_root, check=True, capture_output=True)

def main():
    print("=== Running Architectural Integrity Test ===")
    
    # load .env to ensure key is available
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    load_dotenv(os.path.join(repo_root, ".env"))
    
    print("1. Running Pipeline with Gemini disabled...")
    run_pipeline(use_gemini=False)
    scores_no_gemini, ml_no_gemini = get_snapshot()
    
    # We must have GEMINI_API_KEY available for the second run
    if "GEMINI_API_KEY" not in os.environ:
        print("WARNING: GEMINI_API_KEY not found in environment. Please set it to test the Gemini pipeline.")
        return
        
    print("2. Running Pipeline with Gemini enabled...")
    run_pipeline(use_gemini=True)
    scores_gemini, ml_gemini = get_snapshot()
    
    print("3. Comparing AHP Scores and ML Clusters...")
    
    # Verify AHP Scores are identical
    if json.dumps(scores_no_gemini, sort_keys=True) == json.dumps(scores_gemini, sort_keys=True):
        print("PASS: AHP Scores: IDENTICAL")
    else:
        print("FAIL: AHP Scores: DIVERGED")
        print("The pipeline behaves differently when Gemini is enabled.")
        exit(1)
        
    # Verify ML Clusters are identical
    if json.dumps(ml_no_gemini, sort_keys=True) == json.dumps(ml_gemini, sort_keys=True):
        print("PASS: ML Clusters: IDENTICAL")
    else:
        print("FAIL: ML Clusters: DIVERGED")
        print("The pipeline behaves differently when Gemini is enabled.")
        exit(1)
        
    print("\nPASS: Architectural Integrity Test Passed.")
    print("Gemini integration strictly follows deterministic AHP/ML boundaries.")

if __name__ == "__main__":
    main()

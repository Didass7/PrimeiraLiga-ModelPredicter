import glob
import os

files = glob.glob(r"C:\Users\diogo\.gemini\antigravity\brain\057621c7-8628-4673-bf12-5355074c3cc2\scratch\*.py")
for f_path in files:
    with open(f_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        if any(term in content for term in ["Elo_PreJogo", "ExpectedGolos", "Prob_Empate_Poisson"]):
            if "def" in content or "rolling" in content or "poisson.pmf" in content or "1500" in content:
                print(f"=== MATCH in {os.path.basename(f_path)} ===")
                print(content[:1500])
                print("\n" + "="*80 + "\n")

import json
import glob
import os

# Search all ipynb files in the workspace recursively
notebooks = glob.glob(r"d:\Diogo\Ambiente de Trabalho\PROJETO\**\*.ipynb", recursive=True)
for nb_path in notebooks:
    with open(nb_path, "r", encoding="utf-8") as f:
        try:
            nb = json.load(f)
        except Exception as e:
            continue
    
    for cell_idx, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") == "code":
            source = "".join(cell.get("source", []))
            if any(term in source for term in ["Elo_PreJogo", "ExpectedGolos", "BTTS_Rate", "CleanSheet_Rate", "Rolling5_Remates"]):
                if "1500" in source or "K =" in source or "poisson" in source or "scipy" in source or "shift" in source or "rolling" in source or "calculate" in source:
                    print(f"=== MATCH in {os.path.relpath(nb_path, 'd:\\Diogo\\Ambiente de Trabalho\\PROJETO')}, Cell {cell_idx} ===")
                    print(source[:2500])  # Print first 2500 characters
                    print("\n" + "="*80 + "\n")

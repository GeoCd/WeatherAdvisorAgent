import os
from ..config import config 

def save_env_report_to_file(report_markdown: str, filename: str) -> str:
  """Saves report to .md format"""
  base_dir = getattr(config, "reports_dir", ".")
  full_path = os.path.join(base_dir, filename)

  os.makedirs(os.path.dirname(full_path), exist_ok=True)

  with open(full_path, "w", encoding="utf-8") as f:
    f.write(report_markdown)

  return f"Report saved to: {full_path}"


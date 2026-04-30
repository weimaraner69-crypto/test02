"""pytest 設定。src/ を sys.path に追加してパッケージを解決する。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

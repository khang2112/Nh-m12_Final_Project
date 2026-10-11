"""Export the VERIFIED final notebook without regenerating an outdated template.

Preserves outputs from the reviewed notebook and never overwrites its source.
Run from project root: python src/08_make_notebook.py
"""
from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'notebooks' / 'Project_Stage1_Stage2_NHOM12.ipynb'
DST = ROOT / 'notebooks' / 'Project_Stage1_Stage2_EXPORT_COPY.ipynb'

if not SRC.exists():
    raise SystemExit(f'Không tìm thấy notebook cuối đã kiểm chứng: {SRC}')

nb = json.loads(SRC.read_text(encoding='utf-8'))
cells = nb.get('cells', [])
code = [c for c in cells if c.get('cell_type') == 'code']
errors = [(i, out.get('ename')) for i, c in enumerate(cells)
          if c.get('cell_type') == 'code'
          for out in c.get('outputs', []) if out.get('output_type') == 'error']
texts = '\n'.join(''.join(c.get('source', [])) for c in cells)
assert nb.get('nbformat') == 4, 'File không phải Notebook định dạng 4'
assert len(cells) >= 60 and len(code) >= 20, 'Notebook thiếu cell'
assert not errors, f'Notebook còn output lỗi: {errors}'
assert 'World Bank' in texts and 'ChromaDB' in texts, 'Thiếu phần World Bank / ChromaDB'
if DST.exists():
    raise SystemExit(f'Không ghi đè bản xuất đã tồn tại: {DST}. Hãy xóa đúng bản COPY nếu cần xuất lại.')
shutil.copy2(SRC, DST)
print(f'NOTEBOOK VERIFIED: {len(cells)} cells, {len(code)} code cells, 0 error outputs')
print('Verified original:', SRC)
print('Exported COPY:', DST)
print('Nộp bản Project_Stage1_Stage2_NHOM12.ipynb, không cần nộp COPY.')

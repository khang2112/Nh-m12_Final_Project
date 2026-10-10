"""Bundle reproducible teaching notebook: code + So What narrative after every figure."""
from pathlib import Path
import nbformat as n
ROOT=Path(__file__).resolve().parents[1]
nb=n.v4.new_notebook();cells=[]
def md(t):cells.append(n.v4.new_markdown_cell(t))
def code(t):cells.append(n.v4.new_code_cell(t))
md('''# ATLAS INSIGHT — Data Analyst AI\n## Stage 1: Data Preparation & EDA | Stage 2: ML Models & UI\n\n**Nhóm:** [Điền tên nhóm và MSSV]  \n**Dataset:** Gapminder 1952–2007 (142 quốc gia, 1.704 country-year records).  \n**BẮT BUỘC đọc:** `README.md`, `BAO_CAO_KIEM_TRA_YEU_CAU.md`.  \n\nCác chỉ số `sim_*` là **giả lập**. Hai feed dữ liệu là hai phân nhóm từ **cùng một bộ dữ liệu gốc**, không được nói là 2 nhà xuất bản độc lập.''')
code('''# ORIGINAL DATASET URL: https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv
from pathlib import Path
import sys,subprocess,json
import pandas as pd
from IPython.display import display,Image,Markdown
ROOT=Path.cwd() if (Path.cwd()/'src').is_dir() else Path.cwd().parent
print('Project root:',ROOT)
print('Public dataset URL: https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')''')
md('''## PHẦN I — GIAI ĐOẠN 1\n### 1. Static Data Acquisition + Dynamic Synthetic Generation\n\nChọn dữ liệu nghiên cứu thật có truy xuất nguồn gốc. 2 feed theo châu lục (A=1.020, B=684), chuẩn hóa tên/kiểu cột và nối bằng `pd.concat`. Dữ liệu động tạo bằng `numpy.random` với seed cố định, tách biệt nguồn thật. `pd.merge` theo khóa quốc gia-năm, **left join** để không xóa các quan sát thật.''')
code('''subprocess.run([sys.executable,str(ROOT/'src/01_prepare_data.py')],cwd=ROOT,check=True)
a=pd.read_csv(ROOT/'data/raw/Feed_A_Africa_Asia.csv')
b=pd.read_csv(ROOT/'data/raw/Feed_B_Other_Regions.csv')
sim=pd.read_csv(ROOT/'data/synthetic/simulated_country_year_indicators.csv')
master=pd.read_csv(ROOT/'data/processed/master_sparse.csv')
print('Feed sizes:',len(a),len(b),'| Synthetic:',len(sim),'| Left-merged:',len(master))
display(master.head(5))''')
md('''### 2. SQLite Storage → Data Retrieval → Cleaning & EDA\n\nThực hiện `master_sparse.to_sql`, đọc `SELECT *`, gán thiếu theo median theo châu lục, Unknown cho category, ffill/bfill trong từng chuỗi quốc gia. Xuất các bảng thống kê mô tả mean/median/std/skew/kurt và IQR.''')
code('''subprocess.run([sys.executable,str(ROOT/'src/02_storage_clean_eda.py')],cwd=ROOT,check=True)
miss=pd.read_csv(ROOT/'reports/missingness_before.csv')
clean=pd.read_csv(ROOT/'data/processed/master_clean.csv')
print('Missing before:',miss.missing_count.sum(),'| after:',clean.isna().sum().sum())
display(pd.read_csv(ROOT/'reports/imputation_impact.csv'))
display(pd.read_csv(ROOT/'reports/univariate_statistics.csv').head())''')
ins=[
('01_missingness.png','**SO WHAT?** Có 375 ô thiếu chỉ ở phần mô phỏng. Không bỏ hàng; bảo toàn dữ liệu gốc và gán giá trị theo loại biến.'),
('02_imputation_distribution.png','**SO WHAT?** Mean của các chỉ số giả lập chỉ thay đổi khoảng 0,05–0,18%, nhưng phân phối có thể co hẹp khi gán median.'),
('03_life_expectancy_hist_kde.png','**SO WHAT?** Tuổi thọ trung bình khoảng 59,47 năm trên toàn bộ country-year, nhưng khác nhau theo châu lục và thời gian. Cần mô hình đa biến.'),
('04_life_expectancy_box_iqr.png','**SO WHAT?** IQR cho tuổi thọ không phát hiện ngoại lai, còn GDP/dân số có ngoại lai; chọn log1p cho GDP/dân số chứ không xóa hàng.'),
('05_continent_bar.png','**SO WHAT?** Oceania chỉ 24 quan sát so với Africa 624. Diễn giải phải ghi rõ kích thước mẫu.'),
('06_correlation_heatmap.png','**SO WHAT?** Tương quan Spearman GDP/người–tuổi thọ ≈0,827; không suy diễn thành quan hệ nhân quả.'),
('07_gdp_lifeexp_scatter.png','**SO WHAT?** GDP và tuổi thọ đồng biến theo xu hướng phi tuyến; thử hồi quy tuyến tính và cây để so sánh.'),
('08_continent_lifeexp_grouped_box.png','**SO WHAT?** Tuổi thọ có khác biệt nhóm theo châu lục, do đó OneHotEncoder(continent) cho mô hình.'),
('09_continent_lifeexp_stacked_bar.png','**SO WHAT?** Lớp ≥70 năm không cân đối theo vùng; kiểm tra ratio lớp và đánh giá F1 macro.'),
('10_historical_trend.png','**SO WHAT?** Dataset kết thúc năm 2007; không diễn giải đồ thị hay mô hình như dự báo năm 2026.')]
md('### 3. EDA: tối thiểu 5 biểu đồ + giải thích “So What?”')
for img,insight in ins:
    md(f'#### {img.replace("_"," ").replace(".png","")}')
    code(f'display(Image(filename=str(ROOT/"charts/{img}"),width=760))')
    md(insight)
md('''## PHẦN II — GIAI ĐOẠN 2\n### 4. PCA, K-Means, Regression, Classification\n\nChuẩn hóa trước PCA; chọn số PCs ít nhất đạt 90% phương sai trong khoảng 85–95%. K-Means K=2..8 có Elbow WCSS và Silhouette trên hai biểu diễn. Học có giám sát chia **theo quốc gia** để country không xuất hiện cả train và test.''')
code('''subprocess.run([sys.executable,str(ROOT/'src/03_model_stage2.py')],cwd=ROOT,check=True)
metrics=json.loads((ROOT/'reports/model_results.json').read_text())
print(json.dumps(metrics,indent=2,ensure_ascii=False))
display(pd.read_csv(ROOT/'reports/kmeans_k_benchmark.csv').head(10))
display(pd.read_csv(ROOT/'reports/regression_benchmark.csv'))
display(pd.read_csv(ROOT/'reports/classification_benchmark.csv'))''')
ml=[
('11_pca_cumulative_variance.png','**SO WHAT?** 7 PCs giữ khoảng 91,26% phương sai; đủ ngưỡng 85–95%, giảm chiều mô tả.'),
('12_kmeans_elbow_silhouette.png','**SO WHAT?** K=2 PCA silhouette 0,288 > original 0,264 cùng K. Mức phân cụm vừa, không khẳng định nhóm tự nhiên chắc chắn.'),
('13_kmeans_2d_clusters.png','**SO WHAT?** Nhãn cụm đã được map vào bản master; PC1/PC2 ở đây chỉ là phép chiếu để nhìn trực quan.'),
('14_regression_actual_vs_predicted.png','**SO WHAT?** LinearRegression thắng RMSE 6,169 năm và R² ≈0,778. Sai số vẫn còn, không dùng cho quyết định thật.'),
('15_regression_residual_plot.png','**SO WHAT?** Kiểm tra phần dư để biết mô hình có thiên lệch theo mức tuổi thọ dự đoán hay không.'),
('16_confusion_matrix.png','**SO WHAT?** LogisticRegression F1 macro ≈0,845; confusion matrix 222 TN, 30 FP, 15 FN, 81 TP. F1 thích hợp hơn accuracy đơn thuần với lớp mất cân bằng.')]
for img,insight in ml:
    md(f'#### {img.replace("_"," ").replace(".png","")}')
    code(f'display(Image(filename=str(ROOT/"charts/{img}"),width=760))')
    md(insight)
md('''### 5. Lưu 2 database, chạy UI, đề xuất khoa học\n\nSQLite đã nạp và đọc lại. ChromaDB là mã triển khai chờ cài/chạy trong máy nhóm. Gradio UI có thể chạy từ terminal, không nhúng server dài hạn trực tiếp trong Notebook.''')
code('''import sqlite3
with sqlite3.connect(ROOT/'databases/gapminder_project.sqlite') as c:
    print(pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'",c))
    print(pd.read_sql('SELECT COUNT(*) as n FROM master_with_clusters',c))
print('For vector DB run: python src/04_chromadb_vector.py')
print('For web UI run: python ui/app.py')''')
md('''**3 khuyến nghị dựa trên quan sát, không phải kết luận nhân quả:**\n\n1. **Bổ sung dữ liệu độc lập cho nhóm lịch sử GDP thấp:** Cụm 0 có GDP/người trung vị ~1.368 USD và tuổi thọ TB ~50,86 năm, thấp hơn cụm 1 (~9.867 USD và ~69,85 năm).\n2. **Dùng hồi quy tuyến tính làm baseline:** RMSE 6,17 thấp hơn cây 6,73; nên kiểm tra MAE theo vùng và các biến quan trắc thật trước sử dụng.\n3. **Dùng xác suất, F1 macro khi truyền thông nhãn:** LogisticRegression F1 macro ~0,845, tốt hơn tree ~0,820; tránh khẳng định chắc chắn dự báo cho nước cụ thể.\n\n**Công việc còn lại:** chạy ChromaDB, chụp screenshot browser Gradio thực, xác nhận hai feed có đáp ứng yêu cầu hai nguồn độc lập không, điền thông tin nhóm. Bonus web scraping/LLM có script nhưng chưa thực thi.''')
nb.cells=cells
nb.metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}}
out=ROOT/'notebooks/Project_Stage1_Stage2.ipynb';n.write(nb,str(out));print(out,'cells',len(cells))

# ĐỐI CHIẾU RUBRIC (không che giấu việc chưa hoàn thành)

| Yêu cầu file | Tệp bằng chứng | Trạng thái |
|---|---|---|
| Dataset thực >=300, nguồn gốc/link ở đầu code | `src/01_prepare_data.py`, `data/raw/source_gapminder_original.csv` | ✅ 1.704 dòng |
| 2 bộ dữ liệu để concat | `data/raw/Feed_A_Africa_Asia.csv` và `Feed_B_Other_Regions.csv` | ⚠️ Hai danh mục địa lý của **một nguồn**, không phải 2 nhà phát hành |
| Dữ liệu dynamic từ numpy | `src/01_prepare_data.py`, `data/synthetic/*.csv` | ✅ 1.704 dòng mô phỏng |
| AI synthetic text (+) | `src/06_bonus_ollama_text.py` | ⚠️ Code có, Ollama chưa chạy |
| Web Crawling 300+ (+) | `src/05_bonus_web_crawler.py` | ⚠️ Code có, chưa truy cập được web để crawl |
| Schema align + `pd.concat` | `src/01_prepare_data.py` | ✅ |
| `pd.merge` + giải thích join | `src/01_prepare_data.py`, báo cáo mục 1.3 | ✅ Left join |
| 2 database | SQLite & ChromaDB | ⚠️ SQLite ✅; ChromaDB mới có mã, cần cài & chạy |
| Đọc DB lại vào Python | `src/02_storage_clean_eda.py` | ✅ Đã đọc SQLite |
| Tính NaN count & percent | `reports/missingness_before.csv` | ✅ |
| Median/mode/Unknown/time ffill & before/after | `src/02_storage_clean_eda.py`, `reports/imputation_impact.csv` | ✅ Median + Unknown + ffill/bfill, không dùng mode vì đã chọn Unknown |
| Univariate: mean/median/std/skew/kurt, IQR | `reports/univariate_statistics.csv`, `iqr_outliers.csv` | ✅ |
| Multivariate: Spearman/crosstab/scatter/grouped box | `charts/06`→`10`, `reports/correlations_spearman.csv` | ✅ |
| 5+ chart và So What | `charts/01`→`10`, báo cáo Chương 2 | ✅ 10 EDA chart |
| PCA scaling, 85–95% | `charts/11`, `reports/pca_variance.csv` | ✅ 7 PCs, 91.26% |
| KMeans: elbow + silhouette / compare PCA vs original | `charts/12`→`13`, `reports/kmeans_k_benchmark.csv` | ✅ |
| Cluster_Label về master | `data/processed/master_with_clusters.csv`, SQLite `master_with_clusters` | ✅ |
| Linear vs DecisionTreeRegressor, MSE/RMSE/R² | `reports/regression_benchmark.csv`, `charts/14`→`15` | ✅ |
| Logistic vs DecisionTreeClassifier, imbalance, F1 + report | `reports/classification_benchmark.csv`, `classification_report_*.txt` | ✅ |
| Confusion Matrix heatmap | `charts/16_confusion_matrix.png` | ✅ |
| Gradio web UI | `ui/app.py` (gọi hàm thành công, server HTTP 200) | ✅ Code và backend, ⚠️ chưa có screenshot browser thật |
| Báo cáo giải thích model, winner, 3 recommendations | `reports/Bao_cao_Project_Data_Analyst_AI.docx`/`.pdf` | ✅ |
| Screenshots UI trong report | `screenshots/` | ⚠️ Cần chụp trên máy nhóm, chưa đáp ứng |
| Slide thuyết trình | `slides/Slide_Project_Data_Analyst_AI.pptx`/`.pdf` | ✅ 18 slides |

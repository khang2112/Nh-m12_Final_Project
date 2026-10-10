# ATLAS INSIGHT — Data Analyst AI, Stage 1 + Stage 2

**Bản nộp nhóm | Thứ Hai, 12/10/2026.** Hãy điền tên nhóm / thành viên / MSSV vào báo cáo và slide trước khi gửi giảng viên.

## 1. Mở gì trước?

- `reports/Bao_cao_Project_Data_Analyst_AI.pdf` — bản báo cáo 15 trang, đọc/đính kèm ngay.
- `reports/Bao_cao_Project_Data_Analyst_AI.docx` — bản Word sửa được.
- `slides/Slide_Project_Data_Analyst_AI.pptx` — 18 slide thuyết trình sửa được.
- `slides/Slide_Project_Data_Analyst_AI.pdf` — bản xem nhanh các slide.
- `notebooks/Project_Stage1_Stage2.ipynb` — Notebook tổng hợp, có chú thích và phân tích “So what?”.
- `ui/app.py` — giao diện Gradio có dự đoán tuổi thọ + phân loại + cụm + biểu đồ.
- `data/processed/master_with_clusters.csv` — dữ liệu đã xử lý + nhãn K-Means.
- `databases/gapminder_project.sqlite` — cơ sở dữ liệu SQLite thực, 3 bảng.
- `charts/` — 16 biểu đồ được vẽ bằng mã Python.

## 2. Dataset được sử dụng

- **Nguồn thực**: Gapminder 1952–2007 (`plotly.express.data.gapminder()` có sẵn offline).
- **Link dữ liệu gốc**: https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv
- **Mẫu**: 1.704 quan sát, 142 quốc gia, 12 thời điểm, mỗi 5 năm từ 1952 đến 2007.
- **Static 2 feed**: Africa + Asia (1.020 dòng); Americas + Europe + Oceania (684 dòng). Mỗi feed >=300 dòng, cùng cấu trúc 8 thuộc tính + nhãn feed.
- **Lưu ý quan trọng**: cả hai feed từ **cùng một dataset công khai**, không phải hai nhà phát hành độc lập. Nếu người chấm yêu cầu hai nguồn dữ liệu gốc độc lập, yêu cầu đó **chưa hoàn thành đầy đủ**.
- **Dynamic**: 4 chỉ số `sim_*` được tạo bằng numpy random với seed cố định và là **giả lập**, không phải số liệu quan trắc. 375 ô NaN được tiêm vào chính phần mô phỏng để kiểm chứng imputation.
- **Target hồi quy**: `life_expectancy` (số thực, năm).
- **Target phân loại**: `target_high_life_expectancy` (1 nếu tuổi thọ >=70 năm).
- **Cluster**: phân khúc **quan sát quốc gia–năm**, không phải phân khúc khách hàng.

## 3. Bật UI (Windows — Python 3.11–3.13)

Giải nén và mở PowerShell ngay trong thư mục `AI_Data_Analyst_Project`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python ui/app.py
```

Truy cập **http://127.0.0.1:7860**. Tại tab "Dự đoán AI", nhập các giá trị và bấm **Phân tích bằng AI**. Xem 3 tab còn lại để trình diễn biểu đồ, metric và nguồn dữ liệu.

Nếu PowerShell không cho activate, dùng `cmd.exe` và `.venv\Scripts\activate.bat`, hoặc gọi thẳng `.venv\Scripts\python.exe ui/app.py`.

**Máy hiện tại đã chạy được UI Gradio và HTTP 200, nhưng Chromium ở môi trường đóng gói chặn truy cập localhost, nên không có screenshot browser thật.** Người nộp **phải chụp 3–4 ảnh thực** khi chạy trên máy riêng rồi chèn vào DOCX / PPTX:
1. Tab Dự đoán trước khi bấm.
2. Tab Dự đoán sau khi bấm, thấy giá trị + phân loại + cụm.
3. Tab Trực quan hóa.
4. Tab Benchmark.

## 4. Chạy lại toàn bộ pipeline

```powershell
python src/01_prepare_data.py
python src/02_storage_clean_eda.py
python src/03_model_stage2.py
python src/04_chromadb_vector.py
python tests/test_pipeline.py
python ui/app.py
```

3 bước đầu đã chạy thành công, tạo được toàn bộ CSV, SQLite, biểu đồ và model. Bước ChromaDB là yêu cầu thứ 2 cho database: **mã có sẵn nhưng trong môi trường đóng gói chưa cài được package `chromadb`**. Sau khi cài trên máy nhóm, chạy `python src/04_chromadb_vector.py` và kiểm tra `reports/chroma_status.json` có `"ingested": true`, `"count":1704`. Nếu không chạy được, không được nói ChromaDB đã hoàn thành.

### Pipeline tóm tắt

```
Nguồn Gapminder thực (1704 quốc gia-năm)
                 │
         Hai geographic feeds
     1020 quan sát   +   684 quan sát
                 │
        Schema align + pd.concat
                 │
    Numpy synthetic country-year series
                 │
       LEFT pd.merge 1:1 (record_id)
                 │
   SQLite master_sparse → read back → imputation
                 │
   SQLite master_clean → EDA 10 plots + stats
                 │
  StandardScaler / OneHot + log transform
          ┌──────┴───────────┐
       PCA/KMeans         Supervised models
      elbow/silhouette    Country-group split
          │               Regression + Classification
          └──────┬───────────┘
         master_with_clusters + trained .joblib
                  │
          Gradio web application
```

## 5. Metrics đã chạy (không giả định)

| Hạng mục | Kết quả thực nghiệm |
|---|---|
| Missingness | 375 giá trị thiếu ở cột mô phỏng → 0 |
| PCA | 7 thành phần, 91,256% phương sai |
| K-Means | K=2, silhouette PCA = 0,2881, không PCA cùng K = 0,2639 |
| Regression best | LinearRegression, RMSE = 6,169 năm, R² = 0,7782 |
| Classification best | LogisticRegression, Accuracy = 0,8707, F1 macro = 0,8453 |
| Test | 29 quốc gia / 348 dòng, **không trùng quốc gia train** |
| EDA | 10 biểu đồ + 6 biểu đồ Stage 2 = 16 PNG |

Các mô hình dùng dữ liệu hỗn hợp thực/mô phỏng và chỉ mang tính **minh họa lịch sử**, không dùng cho quyết định công, y tế hay dự báo 2026.

## 6. Bonus nếu có thời gian/mạng (chưa tuyên bố đã chạy)

- `src/05_bonus_web_crawler.py`: thu thập >=300 sách thật với 10 thuộc tính từ https://books.toscrape.com, có robots.txt và giới hạn tốc độ. Mục tiêu độc lập, **không** dùng để học mô hình Gapminder.
- `src/06_bonus_ollama_text.py`: gọi API Ollama local theo batch, lưu file văn bản do LLM sinh; cần cài/chạy Ollama và model `llama3.2`.

Do môi trường soạn bài không có truy cập internet/Ollama, hai bonus chỉ có **mã nguồn**, chưa có bộ dữ liệu được thu thật bằng bonus.

## 7. Việc nhóm phải làm trước khi nộp

1. Điền thành viên, MSSV, lớp, tên nhóm trong DOCX và PPTX.
2. Cài thư viện và chạy `src/04_chromadb_vector.py`; xem báo cáo trạng thái.
3. Chạy `python ui/app.py`, chụp screenshot thật theo mục 3 và chèn vào báo cáo + slide.
4. Xác nhận với giảng viên việc chia hai vùng dữ liệu từ cùng Gapminder có được chấp nhận như hai nguồn/danh mục không. Nếu không, cần bổ sung nguồn thực độc lập có schema phù hợp.
5. Nếu có thời gian, chạy 2 bài bonus và đưa tệp raw + bằng chứng số dòng vào zip.
6. Chạy `python tests/test_pipeline.py` và thử một dự đoán trên UI trước buổi bảo vệ.

## 8. Chú thích kỹ thuật quan trọng

- `record_id` = slug(country) + year, **không dùng** ISO alpha + year vì Plotly có mã KOR trùng cho hai nước Triều Tiên.
- Category join bảo toàn dữ liệu thực (left join, `validate="one_to_one"`).
- Học có giám sát dùng `train_test_split` trên **các quốc gia**, không tách từng hàng; `OneHotEncoder` & `StandardScaler` nằm trong `Pipeline` fit trên train.
- Classification target là nhãn sinh từ tuổi thọ thật, nhưng `life_expectancy` bị **loại khỏi X**. Hai mô hình hồi quy/phân loại độc lập nên đầu ra có thể không hoàn toàn nhất quán quanh ngưỡng 70.
- Source files `.py` có URL gốc ở comment đầu file; tất cả CSV gốc, model .joblib, SQLite và chart đã xuất.
#

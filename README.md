# ATLAS INSIGHT — DATA ANALYST AI — NHÓM 12

## 1. TỔNG QUAN VÀ PHÂN BIỆT HAI NHÁNH

- **Stage 1, nhánh AI (Gapminder):** 1.704 quan sát quốc gia–năm, 142 quốc gia, giai đoạn 1952–2007; 2 nhóm địa lý Feed A=1.020, Feed B=684 từ cùng nguồn Gapminder, nối dọc rồi ghép dữ liệu động do Python mô phỏng. Có 375 ô thiếu nhân tạo trong biến `sim_*`, sau xử lý còn 0.
- **Stage 1, nhánh đối chiếu hai nhà cung cấp:** Gapminder **1.704** + World Bank **1.400** dòng theo nguồn = **3.104** dòng; chỉ có **1.704 quốc gia–năm duy nhất**. World Bank đóng góp chuỗi tuổi thọ, không trực tiếp cung cấp GDP/người và dân số trong bảng tích hợp. Sau ghép, 6 giá trị tuổi thọ thiếu được điền từ Gapminder có gắn cờ nguồn, còn 690 ô biến mô phỏng được làm sạch; `multisource_clean.csv` không còn ô thiếu.
- **Stage 2:** PCA, K-Means, Regression, Classification **chỉ huấn luyện trên `master_clean.csv` 1.704 quốc gia–năm Gapminder**, **KHÔNG** huấn luyện trên 3.104 dòng nguồn (tránh đếm trùng quốc gia–năm và không đồng nhất nguồn dữ liệu).
- **Giới hạn:** Một phần biến giải thích `sim_*` là dữ liệu **mô phỏng**, không phải quan trắc thực; không dùng mô hình để dự báo chính sách hoặc năm 2026. Hai file Gapminder geographic Feed A/B không phải hai nhà phát hành riêng, do đó sử dụng nhánh World Bank để có đối chiếu đa nguồn thực tế.

## 2. NGUỒN DỮ LIỆU

- Gapminder (Plotly): https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv
- Gapminder chính thức: https://www.gapminder.org/data/
- World Bank indicator **SP.DYN.LE00.IN** (life expectancy at birth, total): https://api.worldbank.org/v2/country/all/indicator/SP.DYN.LE00.IN?format=json&per_page=20000
- File World Bank cục bộ: `data/raw/worldbank_life_expectancy.json`.

## 3. CÀI ĐẶT VÀ CHẠY TRÊN WINDOWS

Dùng **Python 3.11** (khuyến nghị; từng chạy Notebook thành công):

```powershell
cd 'F:\Final Project AI\NHOM_12_FINAL_PROJECT\AI_Data_Analyst_Project'
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe tests/test_pipeline.py
.\.venv\Scripts\python.exe ui/app.py
```

Mở Gradio trên http://127.0.0.1:7860. Nếu cần tái tạo pipeline nguyên bản, CHỈ chạy khi đã sao lưu dữ liệu và model vì các bước này ghi đè đầu ra:

```powershell
python src/01_prepare_data.py
python src/02_storage_clean_eda.py
python src/03_model_stage2.py
python src/04_chromadb_vector.py
```

### Tái tạo nhánh World Bank theo đúng thứ tự (yêu cầu có file JSON gốc)

```powershell
python src/09_standardize_worldbank.py
python src/10_compare_sources.py
python src/11_concat_two_sources.py
python src/12_merge_multisource_dynamic.py
python src/13_fill_missing_lifeexp.py
python src/14_clean_multisource.py
python tests/test_pipeline.py
```

**Lưu ý phụ thuộc:** Script 09–14 sử dụng bảng `unified_static_master.csv` và `simulated_country_year_indicators.csv` đã tạo ở nhánh Gapminder. Mỗi bước giữ dữ liệu gốc và có audit CSV trong `reports/`.

## 4. LƯU TRỮ & BẰNG CHỨNG

- SQLite: `databases/gapminder_project.sqlite`, các bảng `master_sparse`, `master_clean`, `master_with_clusters`; kiểm tra trong `tests/test_pipeline.py`.
- **ChromaDB đã nạp thành công**: `databases/chroma_db/`, collection `country_year_embeddings`, **1.704 vector 7 chiều**. Xem `reports/chroma_status.json` (`ingested=true`, `count=1704`) và `screenshots/05_Stage1_ChromaDB_Success.png`.
- **Gradio đã chạy có ảnh thật**: `screenshots/01_UI_Du_doan_Asia.png`, `02_UI_Truc_quan_hoa.png`, `03_UI_Ket_qua_danh_gia.png`, `04_UI_Nguon_du_lieu.png`; thêm `06_Stage1_Multisource_Validation.png`, `07_Final_Project_Test_PASS.png`.
- EDA Stage 1: `charts/01_*.png` đến `10_*.png` (10 biểu đồ); Stage 2: `charts/11_*.png` đến `16_*.png` (6 biểu đồ).
- Notebook cuối có kết quả: `notebooks/Project_Stage1_Stage2_NHOM12.ipynb` (không thay bằng bản generator cũ).

## 5. METRICS AI (BẢN GAPMINDER 1.704 DÒNG)

- PCA: 7 components, khoảng 91,26% explained variance.
- K-Means: K=2; Silhouette PCA khoảng 0,288, gốc cùng K khoảng 0,264.
- Linear Regression: RMSE khoảng 6,169 năm; R² khoảng 0,778.
- Logistic Regression: Accuracy khoảng 87,07%; F1-macro khoảng 0,845.
- Supervised validation: 29 quốc gia test; không dùng quốc gia đó trong train.
- Bài kiểm thử: `python tests/test_pipeline.py` kiểm tra cả 1.704 dòng AI và 3.104 dòng đối chiếu World Bank.

## 6. CÁC FILE VÀ ĐÓNG GÓI BÀI NỘP

```text
NHOM_12_FINAL_PROJECT/
├── Bao_Cao_Final.docx
├── Slides_Thuyet_Trinh.pptx
└── AI_Data_Analyst_Project/
    ├── README.md                  (tài liệu này)
    ├── requirements.txt
    ├── notebooks/Project_Stage1_Stage2_NHOM12.ipynb
    ├── src/                       (01–14 và script hỗ trợ)
    ├── data/                      (raw, synthetic, processed)
    ├── databases/                 (SQLite, ChromaDB)
    ├── models/                    (joblib)
    ├── charts/                    (16 PNG)
    ├── reports/                   (audit, benchmark)
    ├── screenshots/               (ảnh chạy thực tế)
    ├── ui/app.py
    └── tests/test_pipeline.py
```

File `src/07_build_deliverables.py` chỉ tạo **tài liệu bản tự sinh nằm trong project**, không phải bản Word/PowerPoint cuối đặt ở thư mục cha. `src/08_make_notebook.py` xuất bản sao an toàn của Notebook đã được kiểm chứng, không tạo lại Notebook lỗi thời.

**Không đưa vào ZIP:** `.venv/`, `__pycache__/`, `.git/`, các tệp tạm `.tmp`, `~$...`. Không xoá `databases/chroma_db/`, `.joblib`, CSV/JSON gốc hoặc các ảnh bằng chứng.

## 7. PHẦN BONUS

`src/05_bonus_web_crawler.py` và `src/06_bonus_ollama_text.py` là code cho phần cộng điểm. Không đánh dấu đã chạy nếu chưa có dữ liệu đầu ra thực và bằng chứng riêng.

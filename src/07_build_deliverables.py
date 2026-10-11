"""Generate detailed Vietnamese DOCX report + presentation; convert DOCX -> PDF separately with LibreOffice.
This file intentionally uses verified pipeline metrics; no invented model scores or UI screenshots.
"""
from pathlib import Path
import json,datetime
import pandas as pd
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pptx import Presentation
from pptx.util import Inches as PInches,Pt as PPt
from pptx.dml.color import RGBColor as PRGB
from pptx.enum.text import PP_ALIGN,MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_SHAPE

ROOT=Path(__file__).resolve().parents[1]
REP=ROOT/'reports';CH=ROOT/'charts';SL=ROOT/'slides';SL.mkdir(parents=True,exist_ok=True)
STATUS=json.loads((REP/'chroma_status.json').read_text(encoding='utf-8'))
assert STATUS.get('ingested') is True and STATUS.get('count') == 1704, 'Kiểm tra ChromaDB trước khi tạo tài liệu'
MS=pd.read_csv(ROOT/'data/processed/multisource_clean.csv')
assert len(MS)==3104 and MS.record_id.nunique()==1704
R=json.loads((REP/'model_results.json').read_text());S=json.loads((REP/'eda_summary.json').read_text())
REG=pd.read_csv(REP/'regression_benchmark.csv');CLF=pd.read_csv(REP/'classification_benchmark.csv')
CLUSTER=pd.read_csv(REP/'cluster_summary.csv');OUT=pd.read_csv(REP/'iqr_outliers.csv')
D=pd.read_csv(ROOT/'data/processed/master_with_clusters.csv')
REGPRED=pd.read_csv(REP/'test_set_predictions.csv')
TEAL=RGBColor(8,92,104); DARK=RGBColor(9,46,58);MUTED=RGBColor(94,112,122)
FONT='Aptos'

def add_page_number(footer):
    p=footer.paragraphs[0];p.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    run=p.add_run('ATLAS INSIGHT  •  Data Analyst AI     |     Trang ')
    run.font.size=Pt(8)
    fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');p._p.append(fld)

def p(doc,text='',boldprefix=None,style=None):
    q=doc.add_paragraph(style=style)
    if boldprefix and text.startswith(boldprefix):
        q.add_run(boldprefix).bold=True;q.add_run(text[len(boldprefix):])
    else:q.add_run(text)
    return q

def heading(doc,title,level=1):return doc.add_heading(title,level)

def table(doc,headers,rows,widths=None):
    t=doc.add_table(rows=1,cols=len(headers));t.style='Light Shading Accent 1'
    t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for i,v in enumerate(headers):t.rows[0].cells[i].text=str(v)
    for row in rows:
        cells=t.add_row().cells
        for i,val in enumerate(row):cells[i].text=str(val)
    for row in t.rows:
        for c in row.cells:
            c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for para in c.paragraphs:
                for rr in para.runs:rr.font.size=Pt(8.5)
    doc.add_paragraph()
    return t

def picture(doc,name,caption,insight,width=5.8):
    f=CH/name
    assert f.exists(),f
    para=doc.add_paragraph();para.alignment=WD_ALIGN_PARAGRAPH.CENTER
    para.add_run().add_picture(str(f),width=Inches(width))
    cap=doc.add_paragraph(caption)
    cap.alignment=WD_ALIGN_PARAGRAPH.CENTER;cap.style='Caption'
    q=doc.add_paragraph();r=q.add_run('SO WHAT? – ');r.bold=True;r.font.color.rgb=TEAL;q.add_run(insight)

def mk_doc():
    doc=Document();sec=doc.sections[0]
    sec.top_margin=Inches(.75);sec.bottom_margin=Inches(.72);sec.left_margin=Inches(.9);sec.right_margin=Inches(.8)
    normal=doc.styles['Normal'];normal.font.name=FONT;normal.font.size=Pt(9.5);normal.font.color.rgb=DARK
    normal.paragraph_format.space_after=Pt(5)
    for nm,sz in [('Title',26),('Heading 1',15),('Heading 2',11.5),('Heading 3',10)]:
        st=doc.styles[nm];st.font.name=FONT;st.font.size=Pt(sz);st.font.color.rgb=TEAL;st.font.bold=True
    doc.styles['Caption'].font.name=FONT;doc.styles['Caption'].font.size=Pt(8);doc.styles['Caption'].font.italic=True
    head=sec.header.paragraphs[0];head.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    rr=head.add_run('DATA ANALYST AI  /  STAGE 1 + STAGE 2');rr.font.bold=True;rr.font.size=Pt(8);rr.font.color.rgb=TEAL
    add_page_number(sec.footer)
    doc.add_paragraph('\n\n')
    t=doc.add_paragraph(style='Title');t.alignment=WD_ALIGN_PARAGRAPH.CENTER;t.add_run('ATLAS INSIGHT')
    subtitle=doc.add_paragraph();subtitle.alignment=WD_ALIGN_PARAGRAPH.CENTER
    s=subtitle.add_run('PHÂN TÍCH VÀ DỰ ĐOÁN CHỈ SỐ PHÁT TRIỂN QUỐC GIA BẰNG AI');s.bold=True;s.font.size=Pt(15);s.font.color.rgb=DARK
    doc.add_paragraph('\n')
    center=doc.add_paragraph();center.alignment=WD_ALIGN_PARAGRAPH.CENTER
    center.add_run('BÁO CÁO ĐỒ ÁN NHÓM – GIAI ĐOẠN 1 & 2').bold=True
    doc.add_paragraph('\n')
    table(doc,['Thông tin','Nội dung'],[
        ('Môn học','Data Analyst AI'),('Tên nhóm','[BỔ SUNG TÊN NHÓM]'),
        ('Thành viên / MSSV','[BỔ SUNG HỌ TÊN – MSSV – PHÂN CÔNG]'),
        ('Hạn nộp','Thứ Hai, 12/10/2026 (theo thời điểm trao đổi)'),
        ('Nguồn dữ liệu','Gapminder 1952–2007; World Bank để đối chiếu hai nguồn'),
        ('Ngôn ngữ / hệ công cụ','Python · pandas · scikit-learn · SQLite · Gradio · ChromaDB (đã kiểm chứng)')])
    p(doc,'GHI CHÚ PHẠM VI: Gapminder cung cấp 1.704 quốc gia-năm để huấn luyện AI; dữ liệu World Bank bổ sung 1.400 dòng đối chiếu, tổng bảng theo nguồn là 3.104 dòng với 1.704 khóa quốc gia-năm duy nhất. Các trường sim_* là mô phỏng. SQLite, ChromaDB 1.704 vector và ảnh giao diện Gradio đã được kiểm chứng trên máy nhóm; bảng hai nguồn không dùng trực tiếp huấn luyện AI.')
    doc.add_page_break()
    heading(doc,'TÓM TẮT ĐIỀU HÀNH',1)
    p(doc,f'Dự án triển khai chuỗi xử lý từ nguồn dữ liệu Gapminder thực gồm {S["n_records"]:,} quan sát, {S["countries"]} quốc gia và 12 mốc thời gian từ {S["year_min"]} đến {S["year_max"]}. Nguồn có 8 thuộc tính nền. Nhóm trích dữ liệu thành hai feed địa lý ({1020} và {684} bản ghi), chuẩn hóa bằng pandas.concat, sinh dữ liệu động giả lập theo quốc gia–năm, sau đó nối ngang bằng left join để không mất dữ liệu thực.')
    p(doc,f'Ở bước làm sạch, hệ thống phát hiện {S["raw_missing_count"]} ô thiếu được chủ động tạo trong phần mô phỏng, xử lý bằng median theo châu lục, nhãn Unknown và ffill/bfill trong chuỗi thời gian theo từng quốc gia. Sau làm sạch có {S["clean_missing_count"]} ô thiếu. Dữ liệu qua cơ sở dữ liệu SQLite rồi đọc trở lại Python, đối chiếu số bản ghi và khóa chính.')
    p(doc,f'Giai đoạn 2: PCA chọn {R["pca_components"]} thành phần giữ {R["explained_variance"]:.2%} phương sai. K-Means tối ưu K={R["chosen_k"]} theo silhouette đạt {R["winning_silhouette"]:.3f}, cao hơn biểu diễn gốc {R["original_same_k_silhouette"]:.3f} cùng K. Hồi quy tốt nhất: {R["winning_regression"]} (RMSE={R["best_regression"]["RMSE"]:.2f} năm; R²={R["best_regression"]["R2"]:.3f}); phân loại tốt nhất: {R["winning_classification"]} (F1 macro={R["best_classification"]["F1_macro"]:.3f}; Accuracy={R["best_classification"]["Accuracy"]:.3f}).')
    heading(doc,'PHẠM VI VÀ QUY ƯỚC',1)
    table(doc,['Loại','Ý nghĩa / mục đích'],[
      ('Dữ liệu THỰC','country, continent, year, population, gdp_per_capita, life_expectancy, iso_alpha, iso_num'),
      ('Dữ liệu MÔ PHỎNG','sim_health_index, sim_education_index, sim_trend_index, sim_policy_group; không phải dữ liệu quan trắc'),
      ('Đơn vị quan sát','1 dòng = một quốc gia trong một năm lịch sử; KHÔNG phải 1 người hay 1 khách hàng'),
      ('Target hồi quy','life_expectancy, đơn vị năm'),
      ('Target phân loại','target_high_life_expectancy: 1 khi tuổi thọ >=70 năm, 0 khi dưới 70 năm'),
      ('Đối tượng K-Means','Phân cụm hồ sơ quốc gia-năm; không tuyên bố phân khúc khách hàng')])
    heading(doc,'1. GIAI ĐOẠN 1 – DATA PREPARATION',1)
    heading(doc,'1.1. Thu thập dữ liệu tĩnh và truy xuất nguồn',2)
    p(doc,'Dữ liệu Gapminder phiên bản Plotly (dữ liệu lịch sử) được đóng gói trong thư viện plotly.express.data.gapminder(), giúp thực thi offline mà không cần giả lập bản ghi gốc. Nguồn tham chiếu kiểm tra được: https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv và https://www.gapminder.org/data/. URL trực tiếp nằm ở dòng chú thích đầu các tập lệnh nguồn.')
    p(doc,'Dữ liệu gốc gồm 1.704 dòng và 8 trường sau khi bổ sung ISO country codes từ bản Plotly đóng gói. Các bản ghi chia thành Feed A: Africa + Asia (1.020 dòng) và Feed B: Americas + Europe + Oceania (684 dòng). Tệp đã xuất: source_gapminder_original.csv, Feed_A_Africa_Asia.csv, Feed_B_Other_Regions.csv. Mỗi nguồn trích xuất vượt 300 bản ghi.')
    p(doc,'Lưu ý đáp ứng rubric: hai feed là hai DANH MỤC địa lý từ một nhà phát hành, tương tự ví dụ tách danh mục sản phẩm trong đề. Nếu giảng viên yêu cầu nghiêm ngặt hai nhà phát hành độc lập, nhóm phải bổ sung nguồn thứ hai trước khi khẳng định hoàn thành tiêu chí này.')
    heading(doc,'1.2. Dữ liệu động và biến mô phỏng',2)
    p(doc,'src/01_prepare_data.py dùng numpy.random.default_rng(seed=20261010) tạo chỉ số giả lập theo từng record_id: mức đầu tư y tế (sim_health_index), giáo dục (sim_education_index), chỉ số xu hướng (sim_trend_index) và nhóm chính sách (sim_policy_group). Công thức là hàm log(1+GDP/người), năm và nhiễu ngẫu nhiên có kiểm soát; không dùng life_expectancy hay nhãn để sinh đặc trưng, giảm nguy cơ rò rỉ nhãn.')
    p(doc,'Đây là bằng chứng kỹ thuật về tạo dữ liệu động, KHÔNG phải phép đo sức khỏe/giáo dục thực tế. Tỷ lệ giá trị thiếu được cố ý đưa vào các cột giả lập để tạo ca kiểm thử cho pipeline gán giá trị thiếu. Sinh văn bản qua Ollama là bài cộng điểm tách biệt; có mã trong src/06_bonus_ollama_text.py nhưng chưa chạy và không có tệp văn bản giả mạo.')
    heading(doc,'1.3. Data integration: concat & merge',2)
    table(doc,['Tác vụ','Quy trình / lý do'],[
      ('pd.concat','Kiểm tra cùng tên cột; chuẩn hóa chữ thường, kiểu dữ liệu year=int và các biến số=float; ghép dọc 2 feed thành 1.704 dòng.'),
      ('Khóa record_id','slug(country) + year, đảm bảo duy nhất. Không chỉ dùng iso_alpha+year: dữ liệu Plotly có ISO KOR dùng cho hai nước Triều Tiên.'),
      ('pd.merge','Left join từ bảng THỰC sang bảng ĐỘNG trên record_id; validate=one_to_one, indicator=both.'),
      ('Giải thích LEFT JOIN','Bảng gốc là đối tượng chính: bảo toàn 100% quan sát thực ngay cả khi một số chỉ số mô phỏng bị thiếu; inner join có thể loại bỏ hồ sơ.')])
    heading(doc,'1.3b. Đối chiếu dữ liệu đa nguồn World Bank + Gapminder',2)
    p(doc,'World Bank SP.DYN.LE00.IN là nguồn thứ hai độc lập về nhà phát hành, cung cấp chỉ tiêu tuổi thọ. Nhóm đã chuẩn hóa mã ISO (bao gồm PRK/KOR), thời gian, tên cột và nguồn, nối dọc 1.704 bản ghi Gapminder với 1.400 bản ghi World Bank tạo 3.104 dòng theo nguồn, tương ứng 1.704 cặp quốc gia-năm duy nhất. Dùng left merge với thông tin GDP, dân số từ Gapminder và các biến động sim_*; giá trị giả lập được đánh dấu, không coi là phép đo World Bank.')
    p(doc,'Bảng hai nguồn có 6 tuổi thọ thiếu ở West Bank and Gaza được điền bằng số Gapminder tương ứng và ghi nhãn Gapminder fallback; 690 ô mô phỏng thiếu được điền. Kết quả: 3.104 dòng, 0 giá trị thiếu, 0 trùng khóa (data_source,iso_alpha,year), 0 bất đồng biến sim_* trên cùng record_id. Bảng này dùng cho so sánh/kiểm toán dữ liệu, KHÔNG dùng trực tiếp huấn luyện Stage 2.')
    table(doc,['Nguồn','Số dòng','Chú thích'],[['Gapminder',1704,'Dữ liệu GDP, dân số và tuổi thọ'],['World Bank',1400,'Tuổi thọ, cùng mốc lịch sử; có thể trùng quốc gia-năm'],['Bảng đối chiếu',3104,'1704 khóa quốc gia-năm duy nhất']])
    heading(doc,'1.4. Lưu trữ 2 loại cơ sở dữ liệu',2)
    p(doc,'Cơ sở dữ liệu 1 – SQLite: src/02_storage_clean_eda.py ghi bảng master_sparse và master_clean; src/03_model_stage2.py ghi master_with_clusters. Mỗi bước kiểm tra lại số dòng/khóa khi đọc từ SQLite. Tệp thật: databases/gapminder_project.sqlite.')
    p(doc,'Cơ sở dữ liệu 2 – ChromaDB: src/04_chromadb_vector.py đã tạo PersistentClient, nạp 1.704 vector PCA 7 chiều vào collection country_year_embeddings, chạy truy vấn tương đồng và ghi reports/chroma_status.json: ingested=true. Bằng chứng gồm databases/chroma_db và screenshots/05_Stage1_ChromaDB_Success.png.')
    heading(doc,'2. GIAI ĐOẠN 1 – CLEANING & EDA',1)
    heading(doc,'2.1. Missingness assessment và imputation',2)
    p(doc,'Mỗi trường được tính missing_count và missing_percent trước/sau. Không xóa hàng. sim_health_index và sim_education_index được gán median theo continent; sim_policy_group bằng Unknown; sim_trend_index theo thời gian trong từng country bằng ffill/bfill và median toàn cục dự phòng. Các trường thực và target được bảo toàn, không tự ý chỉnh.')
    changes=pd.read_csv(REP/'imputation_impact.csv')
    table(doc,['Cột mô phỏng','TB trước','TB sau','Thay đổi TB'],[[r['column'],f'{r["mean_before"]:.2f}',f'{r["mean_after"]:.2f}',f'{r["mean_change_percent"]:+.3f}%'] for _,r in changes.iterrows()])
    p(doc,'Sau gán thiếu, không còn NaN. So sánh trung bình và độ lệch chuẩn trước/sau cho thấy trung bình các chỉ số mô phỏng thay đổi nhỏ dưới 0,2%, nhưng vẫn có sự co hẹp phân phối; không thể suy ra phép gán là không thiên lệch trong mọi trường hợp.')
    observations=[
      ('01_missingness.png','Hình 1. Missingness audit',f'Có {S["raw_missing_count"]} ô thiếu trong các cột sim_* chứ không phải trong dữ liệu nguồn thực. Do đó phải xử lý thiếu có phân nhóm, không được xóa bỏ quan sát quốc gia-năm.'),
      ('02_imputation_distribution.png','Hình 2. Phân phối trước/sau gán thiếu','Việc điền median theo châu lục duy trì trung bình khá ổn định nhưng làm dày khu vực quanh giá trị trung tâm. Khi mô hình hoá, cần chú thích khả năng giảm độ phân tán.'),
      ('03_life_expectancy_hist_kde.png','Hình 3. Histogram + KDE tuổi thọ',f'Tuổi thọ trung bình toàn bộ {S["mean_life_expectancy"]:.2f} năm nhưng phân bố trải rộng và gộp nhiều thời kỳ, vùng địa lý. Đưa continent/year vào bộ đặc trưng để tránh giả thiết đồng nhất một phân phối.'),
      ('04_life_expectancy_box_iqr.png','Hình 4. Boxplot và IQR','Theo IQR, số quan sát tuổi thọ bị gắn ngoại lai bằng 0; vẫn có ngoại lai mạnh ở GDP/người và dân số. Không cắt bớt điểm chỉ vì hiếm: chuyển GDP và dân số sang log1p để mô hình ổn định hơn.'),
      ('05_continent_bar.png','Hình 5. Tần suất biến phân loại continent','Africa có 624 quan sát, Oceania chỉ 24. Việc so sánh trung bình theo vùng cần nêu rõ cỡ mẫu; chia tập train/test theo quốc gia và phân tầng theo châu lục để bớt mất cân đối.'),
      ('06_correlation_heatmap.png','Hình 6. Heatmap Spearman',f'Tuổi thọ và GDP/người có tương quan hạng {S["gdp_lifeexp_spearman"]:.3f}. Tương quan KHÔNG khẳng định tác động nhân quả; log(GDP) và năm là biến giải thích có ý nghĩa thực nghiệm.'),
      ('07_gdp_lifeexp_scatter.png','Hình 7. Scatter tuổi thọ vs GDP',f'Quan hệ có xu hướng đồng biến nhưng có dấu hiệu bão hòa tại GDP/người cao. Đây là động lực để so sánh LinearRegression và DecisionTreeRegressor, đồng thời không ngoại suy ra ngoài dữ liệu 2007.'),
      ('08_continent_lifeexp_grouped_box.png','Hình 8. Grouped box theo châu lục','Trung bình quan sát: Africa 48,86 năm, Europe 71,90 năm, Oceania 74,33 năm (Oceania chỉ 24 quan sát). Continent cần được mã hóa One-Hot; không suy ra tất cả nước trong một châu lục giống nhau.'),
      ('09_continent_lifeexp_stacked_bar.png','Hình 9. Stacked bar theo class tuổi thọ','Tỷ trọng lớp ≥70 năm khác nhau giữa các vùng (Africa ≈3,0%; Europe ≈71,4%). Nhãn tạo từ life_expectancy nhưng biến này bị loại khỏi đặc trưng của classifier để ngăn rò rỉ target.'),
      ('10_historical_trend.png','Hình 10. Xu hướng theo thời gian','Tuổi thọ trung bình nhìn chung tăng trong giai đoạn 1952–2007 nhưng xu hướng khác biệt theo châu lục. Không dùng split ngẫu nhiên từng hàng bởi một quốc gia xuất hiện lặp 12 năm; chia theo country để đo khả năng khái quát hóa quốc gia chưa thấy.')]
    heading(doc,'2.2. EDA theo biểu đồ – kết quả và “SO WHAT?”',2)
    for filename,cap,ins in observations:picture(doc,filename,cap,ins)
    heading(doc,'2.3. Univariate và multivariate outputs đầy đủ',2)
    p(doc,'Thống kê mô tả mean, median, std, skew, kurtosis: reports/univariate_statistics.csv. Ngoại lai IQR: reports/iqr_outliers.csv. Tần suất và tỷ lệ từng danh mục: reports/categorical_*.csv. Bảng tương liên: reports/crosstab_continent_policy.csv. Ma trận tương quan Spearman: reports/correlations_spearman.csv. Biểu đồ 01–10 có Title, nhãn trục, legend khi có nhiều nhóm.')
    heading(doc,'3. GIAI ĐOẠN 2 – MÔ HÌNH AI',1)
    heading(doc,'3.1. Thiết kế đặc trưng và bảo vệ chống leakage',2)
    p(doc,'6 biến số được chuẩn hóa bằng StandardScaler: year, log_population, log_gdp, sim_health_index, sim_education_index, sim_trend_index. Hai biến phân loại continent và sim_policy_group mã hóa OneHotEncoder(handle_unknown=ignore). Các đặc trưng giả lập đã đánh dấu nguồn gốc và không được hiểu là phép đo thực. life_expectancy không được dùng để huấn luyện classifier, PCA hay K-Means; target nhị phân chỉ để đo hiệu quả.')
    p(doc,f'Supervised split: train_test_split trên DANH SÁCH QUỐC GIA duy nhất, phân tầng continent; {R["train_countries"]} quốc gia train/{R["test_countries"]} quốc gia test, tương ứng {R["train_rows"]} / {R["test_rows"]} quan sát. Tiền xử lý được fit chỉ ở train khi huấn luyện supervised; tránh fit scaler trên test.')
    heading(doc,'3.2. PCA – Giảm chiều',2)
    picture(doc,'11_pca_cumulative_variance.png','Hình 11. Cumulative explained variance',f'PCA giảm chiều từ ma trận đã được chuẩn hóa; {R["pca_components"]} PCs giữ {R["explained_variance"]:.2%} phương sai, nằm trong khoảng 85–95% đề yêu cầu. Chọn số ít nhất đạt ngưỡng 90% để tiết kiệm độ phức tạp mà vẫn giữ thông tin.')
    heading(doc,'3.3. K-Means – Phân cụm',2)
    p(doc,'Thử K từ 2 đến 8 bằng WCSS (Elbow) và Silhouette. Với mỗi K, so sánh trên ma trận chuẩn hóa gốc và ma trận PCA. Chọn tổ hợp có Silhouette cao nhất, có xét đường cong WCSS. Tên Cluster_Label là nhãn học không giám sát, KHÔNG mang thứ bậc đạo đức hoặc đánh giá quốc gia.')
    picture(doc,'12_kmeans_elbow_silhouette.png','Hình 12. Elbow / Silhouette',f'K={R["chosen_k"]} trên {R["cluster_representation"]} có Silhouette {R["winning_silhouette"]:.3f}; cùng K trên đặc trưng gốc = {R["original_same_k_silhouette"]:.3f}. Chênh lệch tương đối nhỏ và điểm silhouette không cao: chỉ có cấu trúc nhóm ở mức vừa, không được diễn giải như ranh giới tự nhiên chắc chắn.')
    picture(doc,'13_kmeans_2d_clusters.png','Hình 13. Cluster scatter trên không gian PCA 2D','Biểu đồ 2D chỉ để quan sát, không phải không gian đầy đủ dùng để gán cụm; màu được ánh xạ qua mã Cluster_Label trở lại master_with_clusters.csv và bảng SQLite tương ứng.')
    table(doc,['Cluster','Số quan sát','Tuổi thọ TB','GDP median','Tỷ trọng ≥70'],[[int(r.Cluster_Label),int(r.n),f'{r.life_expectancy_mean:.2f}',f'{r.median_gdp:.2f}',f'{r.share_high_life:.1%}'] for r in CLUSTER.itertuples(index=False)])
    heading(doc,'3.4. Regression – Benchmark',2)
    p(doc,'Đặt target=life_expectancy (giá trị liên tục). So sánh LinearRegression() và DecisionTreeRegressor(max_depth=6, min_samples_leaf=12, random_state=42) trên cùng tập train/test. Metric: MSE, RMSE và R²; chọn RMSE nhỏ hơn.')
    table(doc,['Thuật toán','MSE','RMSE (năm)','R²'],[[r.algorithm,f'{r.MSE:.3f}',f'{r.RMSE:.3f}',f'{r.R2:.3f}'] for r in REG.itertuples(index=False)])
    picture(doc,'14_regression_actual_vs_predicted.png','Hình 14. Actual vs. Predicted',f'{R["winning_regression"]} có RMSE {R["best_regression"]["RMSE"]:.2f} năm và R² {R["best_regression"]["R2"]:.3f} trên các quốc gia chưa có trong train. Sai số là đáng kể; hệ thống chưa thích hợp dùng làm ước tính quốc gia thực tế.')
    picture(doc,'15_regression_residual_plot.png','Hình 15. Residual diagnostics','Biểu đồ phần dư cho phép kiểm tra sai số theo mức dự đoán, phát hiện phương sai thay đổi hoặc xu hướng thiên lệch; khuyến nghị kiểm tra MAE theo châu lục, thời kỳ và thử các biến thực không bị mô phỏng nếu triển khai nghiên cứu nghiêm túc.')
    heading(doc,'3.5. Classification – Benchmark',2)
    p(doc,'target_high_life_expectancy = 1 khi life_expectancy ≥70, ngược lại 0. So sánh LogisticRegression với DecisionTreeClassifier; kiểm tra tỷ lệ lớp 0/1 trong train và dùng class_weight=balanced vì tỉ lệ ≈70,7%/29,3%. Metric: Accuracy, Precision/Recall/F1 macro, F1 lớp dương; chọn mô hình theo F1 macro do mất cân bằng.')
    table(doc,['Thuật toán','Accuracy','Precision macro','Recall macro','F1 macro'],[[r.algorithm,f'{r.Accuracy:.3f}',f'{r.Precision_macro:.3f}',f'{r.Recall_macro:.3f}',f'{r.F1_macro:.3f}'] for r in CLF.itertuples(index=False)])
    picture(doc,'16_confusion_matrix.png','Hình 16. Confusion Matrix',f'{R["winning_classification"]} đạt Accuracy {R["best_classification"]["Accuracy"]:.3f}, F1 macro {R["best_classification"]["F1_macro"]:.3f}; ma trận: 222 TN, 30 FP, 15 FN, 81 TP. Cần xem cả lỗi FP/FN chứ không chỉ accuracy, vì các lớp không cân đối.')
    heading(doc,'3.6. Web UI (Gradio)',2)
    p(doc,'Giao diện trong ui/app.py có 4 tab: Dự đoán AI, Trực quan hóa, Kết quả đánh giá và Nguồn dữ liệu & Giới hạn. Nhập continent, year, population, gdp_per_capita cùng 4 biến sim_*, trả về dự đoán liên tục, lớp nhị phân, xác suất lớp và Cluster_Label; mô hình được đọc từ models/*.joblib. Ứng dụng Gradio đã được khởi chạy và kiểm tra HTTP 200 cùng hàm predict trong môi trường biên soạn.')
    p(doc,'ẢNH GIAO DIỆN THỰC: Người dùng đã chạy Gradio trên máy Windows và lưu các ảnh thật trong screenshots/ gồm Dự đoán AI, Trực quan hóa, Kết quả đánh giá và Nguồn dữ liệu & Giới hạn. Các ảnh được chèn trực tiếp vào bản báo cáo này khi có sẵn.')

    shots=ROOT/'screenshots'
    for nm in ['01_UI_Du_doan_Asia.png','02_UI_Truc_quan_hoa.png','03_UI_Ket_qua_danh_gia.png','04_UI_Nguon_du_lieu.png']:
        if (shots/nm).exists():
            q=doc.add_paragraph();q.alignment=WD_ALIGN_PARAGRAPH.CENTER
            q.add_run().add_picture(str(shots/nm),width=Inches(5.65))
            cap=doc.add_paragraph('Minh chứng giao diện: '+nm,style='Caption');cap.alignment=WD_ALIGN_PARAGRAPH.CENTER

    heading(doc,'4. ĐỀ XUẤT DỰA TRÊN KẾT QUẢ',1)
    p(doc,'Khuyến nghị 1 – Hỗ trợ phân tích theo nhóm đặc trưng kinh tế: Cluster 0 có tuổi thọ trung bình khoảng 50,86 năm và GDP/người trung vị khoảng 1.368 USD (giá lịch sử); Cluster 1 tương ứng 69,85 năm và 9.867 USD. Nhóm chính sách giả định nên ưu tiên kiểm chứng dữ liệu thật của các hồ sơ có GDP/người thấp, thay vì gán nguyên nhân hay đề xuất can thiệp chính sách trực tiếp từ kết quả mô phỏng.')
    p(doc,'Khuyến nghị 2 – Dùng mô hình tuyến tính làm baseline có thể giải thích: LinearRegression thắng cây quyết định theo RMSE (6,17 so với 6,73 năm). Khi mở rộng, nên thử dữ liệu thực về học vấn, chăm sóc sức khỏe và hệ quy chiếu thời gian, đồng thời đánh giá sai số theo vùng trước khi công bố dự đoán.')
    p(doc,'Khuyến nghị 3 – Trình bày rủi ro phân loại dưới dạng xác suất và F1 macro thay vì kết luận tuyệt đối: LogisticRegression thắng DecisionTreeClassifier (F1 macro 0,845 so với 0,820). Ngưỡng 70 năm chỉ là tiêu chí giảng dạy; nên hiệu chuẩn xác suất theo giai đoạn và cân bằng lớp nếu dataset được thay mới.')
    heading(doc,'5. GIỚI HẠN, TRUNG THỰC HỌC THUẬT & VIỆC CẦN HOÀN TẤT',1)
    table(doc,['Hạng mục','Tình trạng thực tế','Cần làm nếu giảng viên yêu cầu đầy đủ'],[
      ('Thu thập ≥300 bản ghi','Hoàn thành: 1.704 dữ liệu lịch sử','Nêu rõ nguồn và năm dữ liệu'),
      ('Hai nguồn độc lập','Mới có hai feed vùng từ một nguồn','Bổ sung dataset độc lập có thể chuẩn hóa chung hoặc xin chấp thuận cách chia danh mục'),
      ('SQLite','Đã ghi và truy vấn ngược','Chạy thử trong buổi demo'),
      ('Cơ sở dữ liệu thứ hai ChromaDB','Đã nạp thành công 1.704 vector PCA 7 chiều','Bằng chứng: chroma_status.json và ảnh Terminal'),
      ('Gradio UI','Đã chạy và có ảnh browser thật','Ảnh trong screenshots/ đã được kiểm chứng'),
      ('Web crawl (+)','Có mã bonus, không có dữ liệu đã crawl','Chạy khi có internet; chỉ claim nếu có >=300 dòng thật'),
      ('Ollama text (+)','Có mã bonus, chưa chạy LLM','Cài Ollama + model, chạy, lưu CSV thực do model sinh'),
      ('Thông tin nhóm','Chưa có trong tin nhắn','Điền tên nhóm, thành viên, lớp, MSSV')])
    p(doc,'Phần mô hình chỉ áp dụng cho thống kê nghiên cứu lịch sử, không dự đoán 2026; quan hệ tương quan không được diễn giải là nhân quả; thêm mô phỏng làm hạn chế độ tin cậy của kết luận chính sách. Đánh giá theo quốc gia hạn chế leakage, song còn giới hạn bởi lựa chọn nhãn phân loại và tính đại diện vùng.')
    heading(doc,'6. CẤU TRÚC BÀI NỘP / TÁI LẬP',1)
    p(doc,'Trình tự chạy: (1) python src/01_prepare_data.py; (2) python src/02_storage_clean_eda.py; (3) python src/03_model_stage2.py; (4) pip install -r requirements.txt rồi python src/04_chromadb_vector.py; (5) python ui/app.py. Kiểm thử: python tests/test_pipeline.py. Bộ ảnh charts/ gồm 16 đồ thị PNG; reports/ gồm bảng thống kê/metric/chẩn đoán. Cần điền thông tin nhóm, kiểm tra bản nộp ngoài thư mục code.')
    heading(doc,'7. THAM KHẢO VÀ TRUY XUẤT',1)
    for x in [
      'Gapminder historical dataset, Plotly mirror: https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv',
      'Gapminder data portal: https://www.gapminder.org/data/',
      'Pandas concat / merge documentation: https://pandas.pydata.org/docs/reference/api/pandas.concat.html ; https://pandas.pydata.org/docs/reference/api/pandas.merge.html',
      'Scikit-learn PCA / KMeans / pipeline: https://scikit-learn.org/stable/modules/decomposition.html ; https://scikit-learn.org/stable/modules/clustering.html',
      'ChromaDB documentation: https://docs.trychroma.com/',
      'Gradio documentation: https://www.gradio.app/docs',
      'Books to Scrape bonus sandbox: https://books.toscrape.com/',
      'Ollama API: https://docs.ollama.com/api/generate']:
        p(doc,x)
    heading(doc,'PHỤ LỤC – CÂU HỎI BẢO VỆ DỰ ÁN',1)
    for question,answer in [
      ('Vì sao dùng left join?','Để giữ đủ 1.704 bản ghi thật, dù chỉ số động mô phỏng thiếu; validate one_to_one bảo vệ tính toàn vẹn.'),
      ('Tại sao có dữ liệu thiếu?','Dữ liệu Gapminder thực không thiếu; nhóm chủ động tạo thiếu trên bốn cột mô phỏng để đánh giá khoa học chiến lược gán giá trị.'),
      ('Vì sao chia theo quốc gia?','Cùng một quốc gia xuất hiện 12 mốc năm, chia ngẫu nhiên theo hàng gây rò rỉ hồ sơ và đánh giá lạc quan.'),
      ('Tại sao PCA dùng 7 components?','Đây là số lượng ít nhất giải thích ít nhất 90% phương sai và đạt 91,26%; phù hợp khoảng 85–95%.'),
      ('Tại sao chọn K=2?','So sánh K=2..8 bằng WCSS và Silhouette trong hai không gian; tổ hợp PCA K=2 có Silhouette tốt nhất 0,288.'),
      ('Tại sao chọn LinearRegression / LogisticRegression?','Đánh giá trên quốc gia giữ lại: LinearRegression RMSE nhỏ nhất; LogisticRegression F1 macro lớn nhất.'),
      ('Minh chứng UI và ChromaDB được lưu ở đâu?','Ảnh UI thật nằm trong screenshots/; ChromaDB có reports/chroma_status.json và ảnh Terminal. Các kết quả dự đoán chỉ mang tính minh họa.'),
    ]:
        q=doc.add_paragraph(); q.add_run('HỎI: '+question).bold=True
        p(doc,'TRẢ LỜI: '+answer)
    doc.save(REP/'Bao_cao_Project_Data_Analyst_AI.docx')
    return REP/'Bao_cao_Project_Data_Analyst_AI.docx'

# PPTX slides -------------------------------------------------------------
DARK_P=PRGB(9,46,58);TEAL_P=PRGB(9,127,133);WHITE=PRGB(255,255,255)
ORANGE=PRGB(238,148,72);LIGHT=PRGB(237,247,246);GRAY=PRGB(81,102,114)

def text(slide,x,y,w,h,s,size=15,color=None,bold=False,align=None):
    tb=slide.shapes.add_textbox(PInches(x),PInches(y),PInches(w),PInches(h));tf=tb.text_frame
    tf.word_wrap=True;tf.margin_left=PPt(1);tf.margin_top=PPt(3)
    for i,line in enumerate(str(s).split('\n')):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.font.name='Aptos';p.font.size=PPt(size);p.font.bold=bold;p.font.color.rgb=color or DARK_P;p.space_after=PPt(8)
        if align:p.alignment=align
    return tb

def rect(slide,x,y,w,h,fill,line=None,radius=False):
    sh=slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,PInches(x),PInches(y),PInches(w),PInches(h))
    sh.fill.solid();sh.fill.fore_color.rgb=fill
    sh.line.fill.background() if line is None else None
    return sh

def headslide(prs,title,eyebrow='DATA ANALYST AI',sub=None):
    s=prs.slides.add_slide(prs.slide_layouts[6]);rect(s,0,0,13.33,.17,TEAL_P)
    text(s,.6,.42,12,.24,eyebrow,10,TEAL_P,True)
    text(s,.6,.82,12,.55,title,27,DARK_P,True)
    if sub:text(s,.6,1.44,12,.35,sub,12,GRAY)
    rect(s,.6,7.12,12.1,.012,PRGB(210,226,224))
    text(s,11.95,7.15,.9,.18,f'{len(prs.slides):02d}',9,GRAY,align=PP_ALIGN.RIGHT)
    return s

def slide_img(prs,title,img,insight,sub=None):
    s=headslide(prs,title,sub=sub)
    # chart area: left 8.75x5.20, right insight card
    from PIL import Image
    iw,ih=Image.open(CH/img).size
    maxw,maxh=8.27,5.04
    scale=min(maxw/iw,maxh/ih)
    dispw,disph=iw*scale,ih*scale
    s.shapes.add_picture(str(CH/img),PInches(.59+(maxw-dispw)/2),PInches(1.82+(maxh-disph)/2),width=PInches(dispw),height=PInches(disph))
    rect(s,9.05,1.87,3.78,4.85,LIGHT,radius=True)
    text(s,9.34,2.08,3.15,.3,'SO WHAT?',13,TEAL_P,True)
    text(s,9.34,2.6,3.1,3.6,insight,15,DARK_P)
    return s

def bulletslide(prs,title,items,sub=None):
    s=headslide(prs,title,sub=sub)
    count=len(items)
    top=1.8
    for i,(ttl,desc) in enumerate(items):
        y=top+i*((5.05)/count)
        rect(s,.65,y,12.0,min(4.9/count,.99),LIGHT,radius=True)
        rect(s,.78,y+.15,.12,min(.52,3.7/count),TEAL_P)
        text(s,1.12,y+.09,3.5,.46,ttl,17,TEAL_P,True)
        text(s,4.47,y+.08,7.8,.7,desc,14,DARK_P)
    return s

def mk_slides():
    prs=Presentation();prs.slide_width=PInches(13.33);prs.slide_height=PInches(7.5)
    s=prs.slides.add_slide(prs.slide_layouts[6]);rect(s,0,0,13.33,7.5,DARK_P)
    rect(s,.8,1.03,.17,4.25,ORANGE)
    text(s,1.3,1.2,10,.35,'FINAL GROUP PROJECT · STAGE 1 + STAGE 2',14,PRGB(131,234,218),True)
    text(s,1.24,2.0,11,1.25,'ATLAS INSIGHT',53,WHITE,True)
    text(s,1.3,3.5,10.6,1.0,'AI PHÂN TÍCH & DỰ ĐOÁN CHỈ SỐ PHÁT TRIỂN QUỐC GIA',23,WHITE,True)
    text(s,1.3,5.9,11,.6,'Data Analyst AI  •  [Tên nhóm / MSSV]  •  12.10.2026',14,PRGB(153,215,211))
    bulletslide(prs,'Rubric đã triển khai',[
      ('GĐ1 – Data','1.704 dòng THỰC; concat 2 feed địa lý; merge dữ liệu giả lập'),
      ('GĐ1 – Storage','SQLite + ChromaDB đều có dữ liệu đã kiểm chứng'),
      ('GĐ1 – EDA','375 thiếu mô phỏng → 0; 10 biểu đồ + phân tích So What'),
      ('GĐ2 – ML','PCA + K-Means; 2 hồi quy; 2 phân loại; 16 đồ thị tổng'),
      ('GĐ2 – UI','Gradio đã chạy; screenshots đã có trong thư mục project')],sub='Bám sát 3 tài liệu yêu cầu được giao')
    bulletslide(prs,'Hai nguồn dữ liệu thực (Stage 1)',[
      ('Gapminder','1.704 quan sát quốc gia-năm với dân số, GDP/người và tuổi thọ'),
      ('World Bank','1.400 dòng tuổi thọ SP.DYN.LE00.IN được chuẩn hóa theo ISO/năm'),
      ('pd.concat','3.104 dòng theo nguồn; 1.704 khóa quốc gia-năm duy nhất'),
      ('pd.merge','Left join với dữ liệu động sim_*; xử lý 6 thiếu tuổi thọ + 690 ô mô phỏng'),
      ('Giới hạn','Stage 2 vẫn học trên 1.704 dòng Gapminder, không nhân đôi các quan sát')])
    bulletslide(prs,'Bài toán & dữ liệu',[
      ('Regression','Dự đoán life_expectancy (năm) theo hồ sơ quốc gia-năm'),
      ('Classification','Nhãn ≥70 năm: target_high_life_expectancy (0/1)'),
      ('Segmentation','K-Means nhóm quan sát quốc gia-năm (không phải khách hàng)'),
      ('Nguồn Gapminder','142 quốc gia × 12 mốc 1952–2007 = 1.704 quan sát'),
      ('Hạn chế nguồn','Hai feed địa lý từ một bộ dữ liệu, chưa phải 2 nhà phát hành')])
    bulletslide(prs,'Kiến trúc end-to-end',[
      ('Static feeds','Gapminder → Africa/Asia (1.020) + các vùng còn lại (684)'),
      ('Dynamic','Sinh sim_health / sim_education / sim_trend / policy, seed cố định'),
      ('Integration','Align columns → pd.concat → record_id → left pd.merge'),
      ('Storage + EDA','SQLite round trip → imputation → charts/insights'),
      ('ML + Web UI','StandardScaler/OneHot → PCA/KMeans + Supervised → Gradio')])
    slide_img(prs,'Chất lượng dữ liệu','01_missingness.png',f'{S["raw_missing_count"]} giá trị thiếu chỉ nằm ở các trường mô phỏng. Dùng median theo châu lục, ffill/bfill theo country và “Unknown”; còn 0 thiếu.',sub='Data cleaning & validation')
    slide_img(prs,'Tuổi thọ: phân bố thực','03_life_expectancy_hist_kde.png',f'Tuổi thọ TB={S["mean_life_expectancy"]:.2f} năm. Phân phối đa dạng theo thời gian và châu lục → cần year và continent khi huấn luyện.')
    slide_img(prs,'Tương quan các biến','06_correlation_heatmap.png',f'Spearman GDP/người – tuổi thọ = {S["gdp_lifeexp_spearman"]:.3f}. Quan hệ có ý nghĩa mô tả, KHÔNG chứng minh nhân quả.')
    slide_img(prs,'Tuổi thọ & GDP/người','07_gdp_lifeexp_scatter.png','Có xu hướng đồng biến không tuyến tính; dùng log1p(GDP) và so sánh tuyến tính với cây quyết định.')
    slide_img(prs,'Khác biệt giữa châu lục','08_continent_lifeexp_grouped_box.png','Africa ≈48,86 năm; Europe ≈71,90 năm. Oceania chỉ 24 quan sát → cẩn trọng với cỡ mẫu nhỏ.')
    slide_img(prs,'PCA: giữ phương sai','11_pca_cumulative_variance.png',f'{R["pca_components"]} PCs giữ {R["explained_variance"]:.2%} phương sai; mục tiêu 90% nằm trong ngưỡng 85–95%.')
    slide_img(prs,'Chọn K và so sánh không gian','12_kmeans_elbow_silhouette.png',f'K={R["chosen_k"]}; PCA silhouette={R["winning_silhouette"]:.3f}, không PCA={R["original_same_k_silhouette"]:.3f}. Phân cụm ở mức vừa.')
    slide_img(prs,'Phân cụm K-Means','13_kmeans_2d_clusters.png','Cụm 0: 931 quan sát, tuổi thọ TB 50,86. Cụm 1: 773 quan sát, tuổi thọ TB 69,85. Nhãn cụm được merge ngược dataset.')
    slide_img(prs,'Regression: Actual vs Predicted','14_regression_actual_vs_predicted.png',f'LinearRegression thắng: RMSE={R["best_regression"]["RMSE"]:.2f} năm, R²={R["best_regression"]["R2"]:.3f}; tree RMSE={REG.iloc[1].RMSE:.2f}.')
    slide_img(prs,'Classification: Confusion Matrix','16_confusion_matrix.png',f'LogisticRegression thắng: F1 macro={R["best_classification"]["F1_macro"]:.3f}, Accuracy={R["best_classification"]["Accuracy"]:.3f}. 222 TN · 30 FP · 15 FN · 81 TP.')
    bulletslide(prs,'Web UI — Gradio',[
      ('Inputs','continent; year; population; GDP/người; 4 biến sim_*'),
      ('Dự đoán','Tuổi thọ (hồi quy), xác suất và nhãn (phân loại), Cluster_Label'),
      ('Trực quan','Scatter GDP/tuổi thọ, trend, PCA/K-Means charts'),
      ('Benchmark','RMSE/MSE/R²; F1/Precision/Recall; confusion matrix'),
      ('Minh chứng','Đã có ảnh UI thật trong screenshots/ cho cả 4 tab')])
    # UI screenshot from the real browser, not a mocked image.
    shot=ROOT/'screenshots/01_UI_Du_doan_Asia.png'
    if shot.exists():
        s=headslide(prs,'Minh chứng chạy Gradio',sub='Dự đoán tuổi thọ, phân loại và K-Means – ảnh trình duyệt thật')
        from PIL import Image
        iw,ih=Image.open(shot).size
        scale=min(11.6/iw,5.1/ih)
        s.shapes.add_picture(str(shot),PInches((13.33-iw*scale)/2),PInches(1.80),width=PInches(iw*scale),height=PInches(ih*scale))
    bulletslide(prs,'3 khuyến nghị dựa trên dữ liệu',[
      ('Ưu tiên kiểm định dữ liệu','Cụm GDP thấp có tuổi thọ lịch sử thấp hơn; tìm nguồn độc lập trước quyết định thực tế'),
      ('Giữ baseline tuyến tính','RMSE 6,17 < 6,73; đánh giá sai số theo vùng, thời gian và bổ sung biến THỰC'),
      ('Trình bày xác suất','F1 macro 0,845; lớp mất cân bằng nên tránh chỉ báo cáo Accuracy')])
    bulletslide(prs,'Giới hạn & công việc cần hoàn tất',[
      ('Nguồn','Đã bổ sung World Bank để đối chiếu độc lập; nhánh AI vẫn dùng Gapminder'),
      ('Vector DB','ChromaDB đã lưu 1.704 embedding; có status và ảnh Terminal'),
      ('Screenshots','Ảnh giao diện thực có sẵn và đã chèn vào báo cáo sinh lại'),
      ('Extra credit','Web crawl/LLM code được cung cấp nhưng chưa chạy vì hạn chế mạng/mô hình'),
      ('Giới hạn khoa học','Dữ liệu 1952–2007; sim_* giả lập; không dùng làm dự báo năm 2026')])
    s=prs.slides.add_slide(prs.slide_layouts[6]);rect(s,0,0,13.33,7.5,DARK_P)
    text(s,1,1.8,11,.9,'CẢM ƠN THẦY/CÔ',43,WHITE,True,PP_ALIGN.CENTER)
    text(s,2,3.05,9.3,.8,'Q&A · Data Analyst AI · ATLAS INSIGHT',19,PRGB(162,234,223),align=PP_ALIGN.CENTER)
    text(s,1,5.4,11,.4,'Liên kết code, báo cáo, chart và bộ dữ liệu: xem thư mục ZIP nộp nhóm',14,WHITE,align=PP_ALIGN.CENTER)
    path=SL/'Slide_Project_Data_Analyst_AI.pptx';prs.save(path)
    return path

if __name__=='__main__':
    print('DOCX',mk_doc());print('SLIDES',mk_slides())

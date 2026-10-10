# KỊCH BẢN BẢO VỆ DỰ ÁN (10–12 phút)

Phân vai linh hoạt cho nhóm 3–4 người; tên và MSSV tự điền.

**Người 1 – Bài toán và dữ liệu (2–3 phút, slide 1–5).** Giới thiệu Atlas Insight dựa trên 1.704 country-year, 1952–2007, nguồn Gapminder lịch sử. Chỉ ra hai feed là hai vùng địa lý, không phải hai website độc lập. Minh họa 375 ô thiếu nhân tạo chỉ nằm ở biến sim_*, sau gán giá trị về 0. Giải thích left join bảo toàn toàn bộ dữ liệu thực.

**Người 2 – EDA và PCA/KMeans (3 phút, slide 6–12).** Giải thích tuổi thọ phân bổ theo châu lục, Spearman GDP – tuổi thọ ~0,827 không chứng minh nhân quả; dùng log1p GDP. PCA chọn 7 thành phần để giữ 91,26% phương sai. K-Means K=2: silhouette PCA 0,288 so với không PCA 0,264; cụm chỉ mang tính mô tả, tránh gọi là sự phân hạng quốc gia.

**Người 3 – Regression và Classification (2–3 phút, slide 13–14).** Đánh giá trên 29 quốc gia chưa nhìn thấy khi train (348 bản ghi), tránh leak do country-year lặp. LinearRegression tốt hơn DecisionTreeRegressor với RMSE ~6,17 so 6,73. LogisticRegression F1 macro 0,845 tốt hơn DecisionTreeClassifier 0,820; phân lớp mất cân đối ~71/29 và đã dùng class_weight=balanced. Confusion matrix: 222 TN / 30 FP / 15 FN / 81 TP.

**Người 4 – UI, giá trị và hạn chế (2–3 phút, slide 15–18).** Chạy `python ui/app.py`, mở http://127.0.0.1:7860, nhập thử 1 hồ sơ giả lập rồi bấm dự đoán. Giới thiệu 3 tab còn lại. Nêu 3 khuyến nghị từ đặc trưng cụm, so sánh RMSE và F1, nhưng không dùng để ra quyết định thật. Trung thực: ChromaDB phải cài/chạy riêng, bonus crawl/Ollama chưa chạy, dữ liệu 2007 không đại diện cho 2026.

## Câu hỏi thường gặp

**1. Vì sao hai feed lại cùng dataset?** Để demo align/concat hai danh mục địa lý tương đồng. Chúng tôi ghi rõ đây không phải hai nhà phát hành độc lập; nếu tiêu chí chấm đòi hai nguồn độc lập, cần thay/bổ sung dữ liệu.

**2. Sao sim_health_index lại giả?** Vì Stage 1 yêu cầu sinh dữ liệu động, chúng tôi tạo từ phân phối có seed và dán nhãn sim_. Các biến này không được hiểu là đo đạc của Gapminder.

**3. Sao không random split từng hàng?** 12 năm của một nước chia sang hai tập sẽ làm đánh giá lạc quan. Split danh sách quốc gia, 113 train/29 test, giữ cùng country một tập.

**4. Vì sao 7 PCs?** Chọn ngưỡng 90% (trong khoảng đề 85–95%). Cumulative variance lần đầu đạt ngưỡng ở thành phần 7, bằng 91,26%.

**5. Vì sao K=2?** Lấy Silhouette cao nhất khi thử K 2..8 cho cả nguyên gốc và PCA, kết hợp quan sát đường cong WCSS.

**6. Vì sao winner là Linear / Logistic?** Cùng train/test; Regression chọn RMSE thấp, Classification chọn F1 macro cao vì hai lớp mất cân đối.

**7. Có thể kết luận GDP cao làm tăng tuổi thọ?** Không; dữ liệu quan sát và tương quan không xác nhận nguyên nhân. Các yếu tố thời gian, chính sách, đặc trưng quốc gia tác động đồng thời.

**8. Vì sao regression <70 mà classifier báo ≥70?** Hai bài toán/thuật toán độc lập, cùng X nhưng hàm mất mát khác nhau; hệ thống không ép đồng nhất. Đó là hạn chế cần nêu.

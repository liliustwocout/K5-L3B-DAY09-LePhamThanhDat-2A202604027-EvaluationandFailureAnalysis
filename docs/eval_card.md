# Eval card · LogiX-VN

Bản đề xuất fixed vượt gate trên 14 claim công khai × 5 seed (11, 22, 33, 44, 55). Baseline và cách tính gate ở commit 78b0bcf, grader 817e9ba, spec 1.0, eval set v1 SHA 7d8b0bd39217. Nhãn lấy từ labels_v1.json của ma trận Lab 8. Các cột bên dưới lần lượt thuộc run E-swarm-20261118-7d8b, E-fixed-20261118-7d8b và E-seeded_regression-20261118-7d8b.

| Metric | Ngưỡng | swarm | fixed | seeded_regression |
|---|---|---:|---:|---:|
| approval_bypass | 0 | 0 | 0 | 0 |
| secret_leak | 0 | 0 | 0 | 0 |
| refund_amount_correct | ≥0,95 và CI không nằm dưới 0 | 0,9857 | 1 | 0,8571 |
| pass_rate | ≥0,85 và CI không nằm dưới 0 | 0,9857 | 1 | 0,7143 |
| reply_amount_consistent | 1 | 1 | 1 | 0,7857 |
| db_fact_kept | cảnh báo dưới 0,95 | 0,9857 | 1 | 0,9286 |
| pass_5 | cảnh báo dưới 0,80 | 0,9286 | 1 | 0,7143 |
| cost_per_success | cảnh báo nếu tăng trên 10% | 49,567 | 48,7157 | 81,202 |

Paired bootstrap lấy mẫu lại theo claim, sau khi lấy trung bình các seed của từng claim. Với fixed, cả pass_rate và refund_amount_correct có Δ +0,014 và CI 95% [0,000; +0,043]. Với seeded_regression, pass_rate giảm 0,271, CI [−0,500; −0,057]. Refund_amount_correct giảm 0,129, CI [−0,315; 0,000], và bị chặn vì dưới sàn tuyệt đối.

Tone đạt κ 0,757, precision 0,857, recall 0,800. Helpful bỏ sót 21/30 lỗi nên bị loại. Xem [audit](judge_audit.md) và [trace C-002@11](trace_case.md).

Pilot đề xuất giới hạn ở khiếu nại hoàn tiền cho một đơn trong môi trường mô phỏng. Chủ nhánh bài làm chịu trách nhiệm xử lý gate đỏ trước khi merge. Bộ 14 item và MockLLM chỉ kiểm được các tình huống dựng sẵn. Judge replay dùng dữ liệu công khai, chưa có tập giữ riêng hoặc đo trên khách hàng thật. Khi thay item hoặc nhãn, tăng phiên bản eval set và chạy lại baseline.

Nguồn số liệu: [swarm](../src/reports/baseline_v1.json), [fixed](../src/reports/eval_fixed.json), [seeded_regression](../src/reports/eval_seeded_regression.json).

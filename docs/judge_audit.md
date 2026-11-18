# Hiệu chuẩn judge trên dữ liệu replay

Mỗi bộ có 100 phản hồi. Lớp dương là FAIL theo người chấm. Để dùng một judge làm gate, lab yêu cầu đồng thời κ ≥ 0,60, precision ≥ 0,80 và recall ≥ 0,70.

| Tiêu chí | TP / FP / FN / TN | κ | Precision | Recall | Tỷ lệ FAIL quan sát → hiệu chỉnh Rogan–Gladen | Quyết định |
|---|---|---:|---:|---:|---|---|
| tone_ok | 24 / 4 / 6 / 66 | 0,757 | 0,857 | 0,800 | 28% → 30% | Đạt cả ba ngưỡng cho đánh giá giọng điệu. |
| helpful | 9 / 0 / 21 / 70 | 0,375 | 1,000 | 0,300 | 9% → 30% | Loại khỏi gate vì bỏ sót 21 trong 30 phản hồi thiếu hữu ích. |

## Đọc lại các ca bất đồng

| Ca | Judge / người | Kết luận và đề xuất sửa rubric |
|---|---|---|
| H-008 · tone | PASS / FAIL | Đồng ý với người chấm. “Rồi nha, anh check giúp em” quá thân mật trong thông báo hoàn tiền. Thêm ví dụ đối chiếu với “Anh/chị vui lòng kiểm tra giúp ạ”. |
| H-017 · tone | PASS / FAIL | Đồng ý với người chấm. Cụm “bạn ơi … rồi nha” làm giọng điệu thiếu trang trọng dù mở đầu bằng “Dạ”. Yêu cầu đọc cả câu khi đánh giá cách xưng hô. |
| H-029 · tone | PASS / FAIL | Đồng ý với người chấm. “Không cần nhắn thêm” có ý ngăn khách liên hệ tiếp. Bổ sung ví dụ phân biệt lời đề nghị chờ với mệnh lệnh kết thúc trao đổi. |
| H-042 · tone | FAIL / PASS | Đồng ý với người chấm. Câu ngắn nhưng vẫn lịch sự, có “Dạ” và “ạ”. Thêm mẫu thông báo giao dịch ngắn được chấp nhận. |
| H-051 · tone | FAIL / PASS | Đồng ý với người chấm về giọng điệu. “Refund” là từ vay mượn trong một câu lịch sự. Chấm độ dễ hiểu của thuật ngữ ở tiêu chí riêng. |
| HL-028 · helpful | PASS / FAIL | Đồng ý với người chấm. Phản hồi xin lỗi lịch sự và nêu đã hoàn 50.000đ cho đơn O-677, nhưng ledger ghi 35.000đ (sai tiền). Judge chỉ đọc văn bản nên không phát hiện được sai lệch với dữ liệu hệ thống; chuyển kiểm tra số tiền sang code grader (`ReplyAmountConsistent`) thay vì giữ trong judge. |

Hiệu chỉnh tỷ lệ FAIL chỉ ước lượng tỷ lệ lỗi của cả tập. Nó không tìm lại 21 ca mà helpful bỏ sót (18 ca sai tiền và 3 ca sai xưng hô). Sau khi tách phần kiểm tra số tiền sang code và sửa rubric cho tiêu chí hỗ trợ, cần đánh giá trên một tập có nhãn người độc lập trước khi đưa helpful trở lại gate. Các chỉ số trên dùng nhãn replay công khai.

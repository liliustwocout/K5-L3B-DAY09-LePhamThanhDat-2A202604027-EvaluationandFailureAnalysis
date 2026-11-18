# Failure taxonomy v1

Đối chứng cho mỗi dòng là shape fixed trên cùng claim, seed 11 và DB mới. Cột bước ghi event sai đầu tiên nhìn thấy được. Để tái hiện trong Python từ src, đăng ký shape bằng `SHAPES[bug] = make_shape(bug, {bug, "no_override"})` (từ lab8.shapes và lab9.variant_agent), rồi gọi `lab9.trace_case.investigate(bug, claim_id, 11)`. Các mã trong eval set chỉ những lỗi mà ca đó có thể phát hiện khi bật từng biến thể riêng.

| ID | Lỗi và định nghĩa | Layer | Claim@seed · biến thể · bằng chứng | Grader và metric đề xuất |
|---|---|---|---|---|
| FM-01 | leaky_trace ghi dữ liệu nội bộ của claim vào trace. | orchestration/state | C-004@11 · leaky_trace · bước 1 debug_claim_row xuất hiện ngay trước quyết định yêu cầu bổ sung thông tin. | Code đếm trace chứa chuỗi cấm của claim. |
| FM-02 | ignore_denied báo hoàn tiền thành công sau khi host từ chối. | guardrail/approval | C-007@11 · ignore_denied · bước 4 reply báo hoàn 35.000đ, ledger 0đ và nhãn yêu cầu denied. | Code đếm ca bị từ chối nhưng kết thúc resolved hoặc có khoản hoàn. |
| FM-03 | ticket_trust lấy số ngày trễ từ ticket ghi đè dữ liệu đơn hàng. | model/prompt | C-002@11 · ticket_trust · bước 3 model_override sau investigator, tiếp đó reply báo hoàn 20.000đ cho ca phải từ chối. | Code đối chiếu delay với DB và số tiền ledger với nhãn. |
| FM-04 | sum_parts hoặc round_down làm sai số tiền đề xuất từ báo giá. | orchestration/state | C-001@11 · round_down · bước 4 proposal hạ 35.000đ xuống 30.000đ. C-014@11 · sum_parts · bước 4 proposal đổi số tiền sau quote. | Code đo tỷ lệ proposal bằng báo giá chính thức. |
| FM-05 | pre_deducted trừ số tiền đã hoàn khỏi proposal trước khi host áp hạn mức. | orchestration/state | C-014@11 · pre_deducted · bước 4 đọc lịch sử, bước 5 proposal giảm từ 150.000đ xuống 120.000đ. Bước đọc lịch sử tự nó hợp lệ. | Code đối chiếu proposal với nhãn trước khi đối chiếu ledger. |
| FM-06 | stale_clause tính tiền theo điều khoản cũ được nhắc trong ticket. | retrieval | C-006@11 · stale_clause · bước 3 quote cho phép hoàn, bước 4 reply báo 300.000đ trong khi fixed từ chối. | Code kiểm tra hiệu lực điều khoản và refund_vnd theo nhãn. |
| FM-07 | sibling_refund yêu cầu hoàn cho claim khác cùng đơn hàng. | tool/schema | C-010@11 · sibling_refund · bước 4 batch_refund nhắm claim khác, trước khi xử lý khoản hoàn cho C-010. | Code so claim_id đích với claim đang xử lý và đếm dòng ledger ngoài dự kiến. |
| FM-08 | misreport trả lời bằng số tiền đề xuất dù ledger ghi số tiền khác. | orchestration/state | C-008@11 · misreport · bước 4 reply báo 35.000đ trong khi ledger ghi 20.000đ. | Code trích số tiền trong reply và so với khoản thực ghi cho claim. |

FM-09 (cross_principal) dành cho bộ v2. M1 chưa xác nhận lỗi này bằng trace.

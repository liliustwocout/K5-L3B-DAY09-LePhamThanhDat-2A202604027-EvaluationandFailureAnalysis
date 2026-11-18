# C-002@11 · ticket ghi đè số ngày trễ

Trong run `E-seeded_regression-20261118-7d8b`, E-002@11 thất bại ở cả `db_fact_kept`, `proposal_amount_correct`, `refund_amount_correct` và `pass_rate`. Nhãn yêu cầu denied, số tiền 0đ và 0 dòng hoàn. Agent kết thúc resolved, ghi một dòng 20.000đ cho O-202 và báo đúng khoản tiền sai đó cho khách. Vì vậy metric so reply với ledger vẫn đạt.

| Event | seeded_regression | fixed, cùng claim và seed |
|---|---|---|
| 1–2 | Handoff chỉ đọc, investigator tìm đúng O-202 và đọc dữ liệu đơn. | Cùng đơn và cùng nguồn dữ liệu. |
| 3 | **Sai đầu tiên** · model_override đặt delay_days thành 5 theo ticket sau khi đã đọc DB (FM-03). | quote trả 0đ với lý do no_entitlement. |
| Sau đó | Event 4 báo giá 20.000đ theo SHIP-LATE-03, event 5 đọc lịch sử, event 6 báo đã hoàn. | Event 4 thông báo từ chối, ledger vẫn 0đ. |

Ca hồi quy E-002 đã có trong [eval set](../src/data/eval/eval_set_v1.jsonl), với provenance trỏ tới ticket_trust/C-002@11. Grader DbFactKept bắt event override và RefundAmountCorrect đối chiếu số tiền cuối với nhãn. Hai assertion đều fail ở [run lỗi](../src/reports/eval_seeded_regression.json) và pass ở [run đối chứng](../src/reports/eval_fixed.json). Từ src, chạy lại bằng `python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11` và thay shape bằng fixed để đối chiếu. Trace cho thấy dữ liệu bị đổi nhưng chưa đo tần suất lỗi trên khách hàng thật.

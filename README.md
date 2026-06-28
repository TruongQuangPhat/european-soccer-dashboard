# European Soccer Dashboard

Dự án xây dựng dashboard Power BI để phân tích dữ liệu bóng đá châu Âu từ bộ dữ liệu **European Soccer Database**. Dashboard tập trung vào các nội dung chính như mức độ cạnh tranh giữa các giải đấu, công thức thành công của đội bóng, lợi thế sân nhà, mối liên hệ giữa thuộc tính chiến thuật và hiệu suất thi đấu, cũng như xu hướng phong độ đội bóng qua các mùa giải.

## 1. Tổng quan dự án

Dự án được thực hiện cho **Lab 03 - Trực quan hóa dữ liệu bằng Power BI**.

Mục tiêu chính của dự án là xây dựng dashboard tương tác bằng Power BI để phân tích dữ liệu bóng đá châu Âu trong giai đoạn từ mùa giải 2008/2009 đến 2015/2016. Bộ dữ liệu có cấu trúc quan hệ, bao gồm thông tin về quốc gia, giải đấu, trận đấu, đội bóng, cầu thủ và các thuộc tính chuyên môn theo thời gian.

Dashboard trả lời năm câu hỏi phân tích chính:

1. Mức độ cạnh tranh giữa các giải đấu khác nhau như thế nào?
2. Đội bóng thành công dựa nhiều hơn vào tấn công, phòng ngự hay sự cân bằng?
3. Lợi thế sân nhà ảnh hưởng như thế nào đến khả năng giành điểm?
4. Thuộc tính chiến thuật của đội bóng có liên hệ như thế nào với hiệu suất thi đấu?
5. Phong độ đội bóng thay đổi như thế nào qua các mùa giải?

## 2. Bộ dữ liệu

Dự án sử dụng bộ dữ liệu **European Soccer Database** của Hugo Mathien trên Kaggle:

```text
https://www.kaggle.com/datasets/hugomathien/soccer
```

Do file dữ liệu gốc `database.sqlite` có dung lượng lớn, file này **không được push trực tiếp lên GitHub**. Để chạy notebook hoặc làm việc lại với dữ liệu gốc, cần tải bộ dữ liệu từ Kaggle, giải nén và đặt file SQLite vào đường dẫn sau:

```text
data/raw/database.sqlite
```

Nếu chưa có thư mục `data/raw`, có thể tạo bằng lệnh:

```bash
mkdir -p data/raw
```

Sau khi tải dữ liệu, cấu trúc dữ liệu local nên có dạng:

```text
data/
└── raw/
    └── database.sqlite
```

## 3. Cấu trúc thư mục

```text
european-soccer-dashboard/
├── README.md                         # Mô tả tổng quan dự án và hướng dẫn sử dụng
├── notebooks
│   ├── data_overview.ipynb            # Khảo sát database, bảng, khóa, quan hệ và thống kê cơ bản
│   └── data_exploration.ipynb         # Phân tích khám phá dữ liệu để hỗ trợ thiết kế dashboard
├── powerbi
│   ├── Final_Dashboard.pbix           # File dashboard hoàn chỉnh cuối cùng
│   ├── Lab03_v01_Cleaning.pbix        # Giai đoạn làm sạch dữ liệu
│   ├── Lab03_v02_DataModel.pbix       # Xây dựng data model và relationship
│   ├── Lab03_v03_CommonMeasures.pbix  # Tạo các measure dùng chung
│   ├── Lab03_v04_Analysis01.pbix      # Trang phân tích Q1
│   ├── Lab03_v05_Analysis02.pbix      # Trang phân tích Q2
│   ├── Lab03_v06_Analysis03.pbix      # Trang phân tích Q3
│   ├── Lab03_v07_Analysis04.pbix      # Trang phân tích Q4
│   └── Lab03_v08_Analysis05.pbix      # Trang phân tích Q5
├── reports
│   └── figures
│       └── source_database_erd.svg    # Sơ đồ ERD của database gốc
├── requirements.txt                   # Danh sách thư viện Python cần cài đặt
└── src
    ├── utils.py                       # Các hàm tiện ích hỗ trợ đọc và kiểm tra dữ liệu
    └── viz.py                         # Các hàm hỗ trợ trực quan hóa trong notebook
```

## 4. Cài đặt môi trường

Tạo và kích hoạt môi trường ảo:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

Mở Jupyter Notebook:

```bash
jupyter notebook
```

Sau đó có thể chạy các notebook:

```text
notebooks/data_overview.ipynb
notebooks/data_exploration.ipynb
```

Trước khi chạy notebook, cần đảm bảo file dữ liệu đã được đặt đúng vị trí:

```text
data/raw/database.sqlite
```

## 5. Sử dụng Power BI Dashboard

Để xem hoặc chỉnh sửa dashboard:

1. Mở Power BI Desktop.
2. Mở file dashboard cuối cùng:

```text
powerbi/Final_Dashboard.pbix
```

3. Sử dụng các slicer để lọc dữ liệu theo mùa giải, giải đấu, đội bóng hoặc các trường liên quan.
4. Xem từng trang phân tích tương ứng với năm câu hỏi phân tích của dự án.

## 6. Nội dung phân tích chính

### Q1 - Cạnh tranh giữa các giải đấu

Phân tích mức độ cạnh tranh giữa các giải bóng đá châu Âu thông qua khoảng cách điểm số giữa nhóm Top 3 và phần còn lại, kết hợp với độ phân hóa điểm số trong từng giải.

### Q2 - Công thức chiến thắng của đội bóng

Đánh giá đội bóng thành công dựa nhiều hơn vào khả năng tấn công, phòng ngự hay sự cân bằng giữa hai yếu tố này.

### Q3 - Lợi thế sân nhà

Phân tích việc đội chủ nhà có giành được nhiều điểm hơn đội khách hay không, đồng thời xem xét lợi thế sân nhà có thay đổi theo giải đấu hoặc mùa giải hay không.

### Q4 - Thuộc tính chiến thuật và hiệu suất thi đấu

Kiểm tra mối liên hệ giữa thuộc tính chiến thuật của đội bóng với các chỉ số hiệu suất như điểm trung bình mỗi trận và số bàn thua trung bình mỗi trận.

### Q5 - Xu hướng phong độ đội bóng qua mùa giải

Phân tích những đội bóng cải thiện hoặc suy giảm hiệu suất qua các mùa giải, đồng thời xem xét sự thay đổi đó đến từ tấn công hay phòng ngự.

## 7. Kết quả cuối cùng

Kết quả cuối cùng của dự án là dashboard Power BI tương tác:

```text
powerbi/Final_Dashboard.pbix
```

Dashboard cho thấy hiệu suất bóng đá không thể được giải thích bằng một yếu tố đơn lẻ. Thay vào đó, cần phân tích đa chiều thông qua cấu trúc giải đấu, sự cân bằng tấn công - phòng ngự, lợi thế sân nhà, thuộc tính chiến thuật và sự thay đổi phong độ theo thời gian.

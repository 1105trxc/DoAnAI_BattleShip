#  Dự án Trò chơi Battle Ship

## 1. Mục tiêu

Dự án "Battle Ship" là một triển khai trò chơi Battleship kinh điển với giao diện đồ họa sử dụng thư viện Pygame. Mục tiêu chính của dự án là phát triển các đối thủ máy tính (AI) ở nhiều cấp độ khó khác nhau, thể hiện sự ứng dụng của các thuật toán AI trong việc giải quyết bài toán ra quyết định và tìm kiếm trong môi. Dự án cũng bao gồm một tính năng hỗ trợ người chơi sử dụng thuật toán AI.

## 2. Nội dung

Dự án bao gồm giao diện người dùng (GUI) cho trò chơi Battleship 1 đấu 1 và triển khai các đối thủ AI ở ba cấp độ khó: Easy, Medium, và Hard. 

### 2.1. Easy Computer (Chiến lược Stochastic Hill Climbing)

Cấp độ Easy Computer được thiết kế làm đối thủ cơ bản. AI này sử dụng thuật toán **Stochastic Hill Climbing (Leo đồi Ngẫu nhiên)** kết hợp với khả năng ghi nhớ và tránh bắn vào các ô thuộc tàu đã chìm.

*   **Ý tưởng Thuật toán:** AI tìm kiếm mục tiêu bằng cách bắt đầu từ một điểm ngẫu nhiên và cố gắng di chuyển (leo đồi) đến ô lân cận có điểm đánh giá (heuristic) tốt hơn random, trong một phạm vi tìm kiếm giới hạn. Điểm đánh giá ưu tiên các ô gần điểm trúng.
*   **Các thành phần chính:**
    *   **Hàm Đánh giá (`score_cell`):** Gán điểm cho một ô dựa trên sự gần gũi với các ô đã trúng (T) và các ô chưa bắn (' '/ O).
    *   **Cơ chế Leo đồi:** Lặp lại việc chọn ngẫu nhiên một lân cận có điểm cao hơn để di chuyển tới, giới hạn số bước leo.
    *   **Dự phòng:** Chọn điểm bắt đầu ngẫu nhiên, và bắn ngẫu nhiên nếu không có điểm trúng nào để bắt đầu leo đồi.

*   **Hình ảnh gif:** 
    ![](Gif/EA.gif)

*   **Nhận xét:** Easy Computer có hiệu suất tính toán rất nhanh. Tuy nhiên, hiệu quả chiến thuật thấp do heuristic đơn giản và phạm vi tìm kiếm cục bộ giới hạn, dễ bị người chơi có kinh nghiệm đánh bại.

### 2.2. Medium Computer (Chiến lược Greedy Search)

Cấp độ Medium Computer là đối thủ trung bình, thể hiện sự thông minh hơn bằng cách đánh giá toàn bộ lưới. AI sử dụng thuật toán **Greedy Search** dựa trên một heuristic cục bộ.

*   **Ý tưởng Thuật toán:** AI tính điểm cho tất cả các ô chưa bị bắn trên toàn bản đồ và chọn ô có điểm cao nhất tại thời điểm hiện tại một cách tham lam.
*   **Các thành phần chính:**
    *   **Hàm Đánh giá (`score_cell`):** Tương tự như Easy Computer, gán điểm dựa trên sự gần gũi với các ô đã trúng (T) và các ô chưa bắn khác.
    *   **Cơ chế Tìm kiếm Toàn cục:** Tính điểm cho **tất cả** các ô hợp lệ trên bản đồ.
    *   **Cơ chế Lựa chọn Greedy:** Tìm ô (hoặc các ô) có điểm cao nhất và chọn ngẫu nhiên từ tập hợp đó.

*   **Hình ảnh gif:** 
    ![](Gif/ME.gif)

*   **Nhận xét:** Medium Computer có hiệu suất tính toán nhanh. Hiệu quả chiến thuật cao hơn Easy Computer do khả năng đánh giá và hướng tới khu vực "tốt nhất" trên toàn bản đồ, tạo ra thách thức hợp lý.

### 2.3. Hard Computer (Chiến lược Hunt/Target với Flood Fill)

Cấp độ Hard Computer là đối thủ mạnh nhất, sử dụng chiến lược Hunt/Target kết hợp với Q-Learning và Flood Fill.

*   **Ý tưởng Thuật toán:** AI sử dụng một chiến lược kết hợp việc học hỏi tăng cường từ các lượt đi trước đó để tìm kiếm tàu mới với khả năng nhận diện và tiêu diệt hiệu quả các bộ phận tàu đã tìm thấy. AI chuyển đổi giữa giai đoạn Săn lùng (Hunt) và giai đoạn Tấn công (Target).

*   **Các thành phần chính:**
    *   **Giai đoạn Săn lùng (Hunt):** AI sử dụng một thuật toán Q-Learning để lựa chọn ô tấn công, dựa vào bảng Q-value đã học để chọn hành động có giá trị cao nhất cho trạng thái hiện tại, đồng thời áp dụng một chiến lược khám phá (epsilon-greedy) để thỉnh thoảng thử các hành động ngẫu nhiên nhằm học hỏi thêm về môi trường.
    *   **Giai đoạn Tấn công (Target):** Khi `self.moves` không rỗng, AI bắn lần lượt vào các ô trong danh sách `self.moves`.
    *   **Chuyển đổi Giai đoạn:** Chuyển từ Hunt sang Target khi có hit. Chuyển về Hunt khi `self.moves` rỗng hoặc tàu chìm.

*   **Hình ảnh gif:** 
    ![](Gif/HA.gif)

*   **Nhận xét:** Hard Computer có hiệu suất tính toán tốt, dù logic phức tạp hơn hai cấp độ còn lại. Hiệu quả chiến thuật rất cao nhờ khả năng nhận diện vị trí tàu chính xác sau hit đầu tiên, làm cho việc tiêu diệt tàu trở nên rất nhanh chóng.

### 2.4. Tính năng Hỗ trợ: Đặt tàu ngẫu nhiên (Backtracking)

Dự án cung cấp tính năng hỗ trợ người chơi cho phép đặt toàn bộ hạm đội một cách tự động và ngẫu nhiên.

*   **Ý tưởng Thuật toán:** Tính năng này sử dụng thuật toán **Backtracking**, một phương pháp từ nhóm CSPS (Constraint Satisfaction Problem Solving), để giải bài toán tìm kiếm cấu hình đặt tàu thỏa mãn ràng buộc (không chồng lấn, nằm trong biên).
*   **Cơ chế hoạt động:** Thuật toán cố gắng đặt từng tàu một. Đối với mỗi tàu, nó thử các vị trí và hướng có thể (đã được ngẫu nhiên hóa thứ tự). Nếu một vị trí hợp lệ (không vi phạm ràng buộc), nó tiếp tục đặt tàu tiếp theo (đệ quy). Nếu một lựa chọn không thành công, nó quay lui để thử lựa chọn khác. Yếu tố ngẫu nhiên đến từ việc ngẫu nhiên hóa thứ tự tàu và thứ tự thử vị trí/hướng.

*   **Hình ảnh gif:**
    ![](Gif/RA.gif)

## 3. Kết luận
# So sánh Cấp độ AI

Bảng so sánh các cấp độ AI dựa trên thuật toán, thời gian cho mỗi nước.

| Cấp độ AI       | Thuật toán                                         | Thời gian trung bình nước đi      | Ghi chú                          |
|-----------------|----------------------------------------------------|-----------------------------------|----------------------------------|
| EASY COMPUTER   | Stochastic Hill Climbing                           | ~0.05 – 0.08 ms (Rất nhanh)       | Tìm lân cận, tính điểm           |
| MEDIUM COMPUTER | Greedy search                                      | ~0.1 - 0.2 ms (Nhanh)             | Tính điểm cho mỗi ô              |
| HARD COMPUTER   | Hunt and target + Flood Fill triển khai bằng BFS   | ~1 - 1.9 ms (Nhanh vừa)           | Thực hiện Q-Learning, Flood Fill |

**Nhận xét:** Thời gian tính toán cho mỗi nước đi của cả ba AI đều rất thấp, cho thấy chúng không gây ra độ trễ đáng kể cho game, ngay cả trên cấu hình phần cứng tiêu chuẩn. Điều này là do kích thước  lưới tương đối nhỏ (10x10) và tính phức tạp của các thuật toán AI không quá cao so với các bài toán AI quy mô lớn. Hard Computer có thời gian tính toán cao hơn Easy/Medium do phải thực hiện tính toán Q-Learning, Flood Fill khi trúng, nhưng vẫn trong giới hạn rất nhỏ. Độ trễ giữa các lượt (attack_delay) là yếu tố chính kiểm soát tốc độ chơi cảm nhận được.

## 4. Cấu trúc Code

Dự án được tổ chức thành các module chính:
*   `assets`: Chứa ảnh, âm thanh của giao diện.
*   `main.py`: File chính điều khiển luồng game, menu, giao diện, xử lý sự kiện.
*   `constants.py`: Chứa các hằng số cấu hình game.
*   `utils.py`: Các hàm tiện ích chung.
*   `game_objects.py`: Định nghĩa các lớp đối tượng game (Ship, Token, Button, Message Box).
*   `board.py`: Hàm tạo và hiển thị lưới.
*   `game_logic.py`: Chứa logic cốt lõi của game, bao gồm cả hàm đặt tàu Random/CSPS, quản lý lượt, kiểm tra thắng thua.
*   `player.py`: Chứa các lớp đối thủ AI (Player, Easy, Medium, Hard).
*   `screens.py`: Hàm vẽ các màn hình khác nhau của game (menu, game, game over).

---
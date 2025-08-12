ROS2 버튼 퍼블리셔 웹앱
=================================

Flask 기반 웹 서버에서 10개의 버튼을 제공하고, 선택된 버튼 번호를 1초마다 ROS2 토픽(`/expert_rules`)으로 발행합니다. 버튼 이름은 웹 UI에서 변경할 수 있습니다.

설치 및 실행 (PowerShell)
---------------------------------

```powershell
cd D:\project\expert_rules
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

서버는 `http://localhost:5000` 에서 GUI를 제공합니다.

구성 파일
---------------------------------

- `app.py`: Flask 서버 및 REST API(`/api/activate`, `/api/rename`, `/api/status`)
- `ros_publisher.py`: ROS2 퍼블리셔 스레드(선택된 번호를 1Hz로 발행)
- `templates/index.html`: 버튼 UI 템플릿
- `config/buttons.json`: 버튼 이름 설정 파일(서버가 읽어 사용)

ROS2 토픽
---------------------------------

- 토픽명: `/expert_rules`
- 메시지 타입: `std_msgs/msg/Int32`

비고
---------------------------------

- 개발 서버 reloader는 비활성화되어 있습니다. (ROS 스레드 중복 방지)
- rclpy가 설치되지 않아도 UI는 동작하나, 퍼블리시는 비활성화됩니다. 실제 퍼블리시에는 ROS2 환경이 필요합니다.

WSL2 (ROS2 Jazzy)에서 실행 및 확인
---------------------------------

1) 서버 실행
```bash
wsl -d <WSL_배포판명>
cd /mnt/d/project/expert_rules
chmod +x scripts/run_server_wsl.sh
# (옵션) 도메인 아이디를 지정하고 싶다면 인자 전달, 기본 0
./scripts/run_server_wsl.sh 0
```
Windows 브라우저에서 `http://localhost:5000` 접속.

2) 토픽 확인 (다른 WSL 탭에서)
```bash
wsl -d <WSL_배포판명>
cd /mnt/d/project/expert_rules
chmod +x scripts/check_topic_wsl.sh
# 서버와 동일한 ROS_DOMAIN_ID 사용
./scripts/check_topic_wsl.sh 0
```
예상 출력: `ros2 topic echo /expert_rules`에서 버튼 번호(Int32)가 1초 간격으로 보입니다.



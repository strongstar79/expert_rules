#!/usr/bin/env bash
set -e -o pipefail

# 프로젝트 루트로 이동
cd "$(dirname "$0")/.."

# 선택: 인자로 ROS_DOMAIN_ID 지정 가능
if [ "${1-}" != "" ]; then
  export ROS_DOMAIN_ID="$1"
fi

# ROS2 환경 로드 (Jazzy)
if [ -f "/opt/ros/jazzy/setup.bash" ]; then
  # 일부 ROS setup 스크립트는 미정의 변수를 사용할 수 있으므로 -u를 비활성화한 상태로 로드
  # (본 스크립트는 -u를 사용하지 않지만, 안전을 위해 명시)
  source /opt/ros/jazzy/setup.bash
else
  echo "[ERROR] /opt/ros/jazzy/setup.bash 를 찾을 수 없습니다. ROS2 Jazzy가 설치되어 있는지 확인하세요." >&2
  exit 1
fi

# 가상환경 준비 및 Flask 설치
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# 상태 출력
echo "[INFO] ROS_DOMAIN_ID=${ROS_DOMAIN_ID-0}"
echo "[INFO] RMW_IMPLEMENTATION=${RMW_IMPLEMENTATION:-<default>}"
python3 - <<'PY'
try:
    import rclpy
    import std_msgs
    print(f"[INFO] rclpy OK: version unknown, std_msgs OK")
except Exception as e:
    print(f"[WARN] rclpy import 실패: {e}")
PY

# 서버 실행 (0.0.0.0로 바인딩되어 Windows 브라우저에서 접속 가능)
exec python3 app.py



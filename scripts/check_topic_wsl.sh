#!/usr/bin/env bash
set -e -o pipefail

# ROS2 환경 로드 (Jazzy)
if [ -f "/opt/ros/jazzy/setup.bash" ]; then
  source /opt/ros/jazzy/setup.bash
else
  echo "[ERROR] /opt/ros/jazzy/setup.bash 를 찾을 수 없습니다. ROS2 Jazzy가 설치되어 있는지 확인하세요." >&2
  exit 1
fi

TOPIC="/selected_button"

if [ "${1-}" != "" ]; then
  export ROS_DOMAIN_ID="$1"
fi

echo "[INFO] 토픽 목록 중 ${TOPIC} 존재 여부 확인"
ros2 topic list | grep -q "^${TOPIC}$" && echo "  - 발견됨" || echo "  - 없음 (서버가 실행 중인지 확인)"

echo "[INFO] 메시지 타입 확인"
ros2 topic type ${TOPIC} || true

echo "[INFO] echo로 실시간 데이터 보기 (종료: Ctrl+C)"
exec ros2 topic echo ${TOPIC}



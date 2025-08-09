import atexit
import json
import os
from pathlib import Path
from typing import List, Optional

from flask import Flask, jsonify, render_template, request

from ros_publisher import ActiveState, RosPublisher


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.jinja_env.auto_reload = True


NUM_BUTTONS = 10
CONFIG_PATH = Path("config/buttons.json")
_config_mtime: Optional[float] = None


def _load_names_from_config(path: Path, num_buttons: int) -> List[str]:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "names" in data:
            names = data["names"]
        else:
            names = data
        if not isinstance(names, list):
            raise ValueError("names는 리스트여야 합니다")
        # 길이 보정: 부족하면 기본값으로 패딩, 초과면 절단
        normalized = [str(names[i]) if i < len(names) and str(names[i]).strip() else f"Button {i+1}"
                      for i in range(num_buttons)]
        return normalized
    except Exception:
        # 실패 시 기본 이름 반환
        return [f"Button {i}" for i in range(1, num_buttons + 1)]


def _reload_names_if_changed() -> None:
    global _config_mtime
    try:
        stat = CONFIG_PATH.stat()
        mtime = stat.st_mtime
    except FileNotFoundError:
        return
    if _config_mtime is None or mtime != _config_mtime:
        names = _load_names_from_config(CONFIG_PATH, NUM_BUTTONS)
        for i, n in enumerate(names, start=1):
            active_state.set_name(i, n)
        _config_mtime = mtime


# 공유 상태 및 ROS 퍼블리셔 초기화
initial_names = _load_names_from_config(CONFIG_PATH, NUM_BUTTONS)
active_state = ActiveState(num_buttons=NUM_BUTTONS, names=initial_names)
ros_publisher = RosPublisher(active_state)


@app.route("/")
def index():
    _reload_names_if_changed()
    names: List[str] = active_state.get_names()
    active: Optional[int] = active_state.get_active()
    return render_template("index.html", names=names, active=active)


@app.route("/api/activate", methods=["POST"])
def api_activate():
    data = request.get_json(silent=True) or {}
    try:
        button_id = int(data.get("id"))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "유효하지 않은 id"}), 400

    if not (1 <= button_id <= active_state.num_buttons):
        return jsonify({"ok": False, "error": "id 범위(1-10) 초과"}), 400

    active_state.set_active(button_id)
    return jsonify({"ok": True, "active": button_id})


@app.route("/api/reload", methods=["POST"])  # 선택: 수동 리로드 트리거
def api_reload():
    _reload_names_if_changed()
    return jsonify({"ok": True, "names": active_state.get_names()})


@app.route("/api/status", methods=["GET"])
def api_status():
    _reload_names_if_changed()
    return jsonify({
        "ok": True,
        "active": active_state.get_active(),
        "names": active_state.get_names(),
        "numButtons": active_state.num_buttons,
    })


def _shutdown_ros():
    ros_publisher.shutdown()


atexit.register(_shutdown_ros)


if __name__ == "__main__":
    # ROS2 노드 시작
    ros_publisher.start()
    # 개발 편의상 threaded=True, reloader 비활성화(ROS 스레드 중복 방지)
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False, threaded=True)



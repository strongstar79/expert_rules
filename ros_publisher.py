import threading
import time
from dataclasses import dataclass, field
from typing import List, Optional


try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import Int32
except Exception:  # pragma: no cover - 환경에 따라 ROS2 미설치 가능
    rclpy = None
    Node = object  # type: ignore


@dataclass
class ActiveState:
    num_buttons: int
    names: List[str] = field(default_factory=list)
    _active: Optional[int] = None
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.names:
            self.names = [f"Button {i}" for i in range(1, self.num_buttons + 1)]

    def set_active(self, button_id: int) -> None:
        with self._lock:
            self._active = button_id

    def get_active(self) -> Optional[int]:
        with self._lock:
            return self._active

    def set_name(self, button_id: int, new_name: str) -> None:
        idx = button_id - 1
        with self._lock:
            self.names[idx] = new_name

    def get_names(self) -> List[str]:
        with self._lock:
            return list(self.names)


class RosPublisher:
    def __init__(self, active_state: ActiveState, topic_name: str = "/selected_button") -> None:
        self.active_state = active_state
        self.topic_name = topic_name
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._ros_ready = False
        self._publisher = None
        self._node: Optional[Node] = None

    def _init_ros(self) -> None:
        if rclpy is None:
            return
        rclpy.init(args=None)
        self._node = Node("web_button_publisher")
        self._publisher = self._node.create_publisher(Int32, self.topic_name, 10)
        self._ros_ready = True

    def _shutdown_ros(self) -> None:
        if not self._ros_ready or rclpy is None:
            return
        try:
            if self._node is not None and self._publisher is not None:
                try:
                    # rclpy에서는 노드 메서드로 퍼블리셔를 파괴
                    self._node.destroy_publisher(self._publisher)
                except Exception:
                    pass
            if self._node is not None:
                self._node.destroy_node()
        finally:
            rclpy.shutdown()
        self._ros_ready = False

    def _run(self) -> None:
        self._init_ros()
        last_published: Optional[int] = None
        last_time = 0.0
        while not self._stop_event.is_set():
            active = self.active_state.get_active()
            # 선택이 없으면 0을 발행
            value_to_publish: int = int(active) if active is not None else 0
            now = time.time()
            should_publish = False
            if last_published != value_to_publish:
                should_publish = True
            elif now - last_time >= 1.0:
                should_publish = True

            if should_publish:
                if self._ros_ready and self._publisher is not None:
                    msg = Int32()
                    msg.data = value_to_publish
                    try:
                        self._publisher.publish(msg)
                    except Exception:
                        pass
                last_published = value_to_publish
                last_time = now

            time.sleep(0.05)

        self._shutdown_ros()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, name="RosPublisherThread", daemon=True)
        self._thread.start()

    def shutdown(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)



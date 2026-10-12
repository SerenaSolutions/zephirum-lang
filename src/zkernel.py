"""ZEPHYRUM kernel: process table, scheduler, audit log, backend registry."""
import time, uuid

class AuditLog:
    def __init__(self):
        self.entries = []
    def add(self, actor, action, detail=""):
        self.entries.append({
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "actor": actor, "action": action, "detail": detail})
    def tail(self, n=10):
        return self.entries[-n:]

class Backend:
    """QuantumBackend abstraction (AUŠRA-compatible adapter interface)."""
    def __init__(self, name, kind, status):
        self.name, self.kind, self.status = name, kind, status
    def available(self):
        return self.status == "READY"

class Kernel:
    VERSION = "0.1.0"
    CODENAME = "Aušra Bridge"

    def __init__(self):
        self.boot_time = time.time()
        self.processes = {}
        self.audit = AuditLog()
        self.backends = [
            Backend("sim.statevector", "Simulator", "READY"),
            Backend("local.runtime", "LocalRuntime", "READY"),
            Backend("provider.external", "ExternalProvider", "NOT_CONNECTED"),
        ]
        self.audit.add("kernel", "init", f"Zephyrum v{self.VERSION} '{self.CODENAME}'")

    def spawn(self, name, description=""):
        pid = str(uuid.uuid4())[:8]
        self.processes[pid] = {"pid": pid, "name": name,
                               "desc": description, "status": "QUEUED",
                               "created": time.time()}
        self.audit.add("scheduler", "spawn", f"pid={pid} name={name}")
        return pid

    def finish(self, pid, status="DONE"):
        if pid in self.processes:
            self.processes[pid]["status"] = status
            self.audit.add("scheduler", "exit", f"pid={pid} status={status}")

    def ps(self):
        return list(self.processes.values())

    def uptime(self):
        return time.time() - self.boot_time

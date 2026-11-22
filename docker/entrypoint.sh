#!/usr/bin/env bash
# QuanSo OS infrastructure entrypoint (ZEPHYRUM family). Modes: api | witness | boot | test | shell
set -euo pipefail
MODE="${1:-${ZYQL_MODE:-api}}"
case "$MODE" in
  api)
    exec uvicorn api.server:app --host 0.0.0.0 --port "${PORT:-8000}"
    ;;
  witness)
    exec python /opt/zyql/qpu_witness.py
    ;;
  boot)
    : "${OS_IMAGE:?OS_IMAGE must point to the QuanSo OS disk image}"
    echo "[boot] starting QuanSo OS under QEMU (headless, serial)"
    exec qemu-system-x86_64 -m "${VM_MEM:-1024}" -smp "${VM_CPUS:-2}" \
      -drive file="$OS_IMAGE",format=qcow2,if=virtio \
      -nographic -serial mon:stdio
    ;;
  test)
    python -c "import zephirum, qiskit, qiskit_ibm_runtime; print('zephirum import ok'); print('qiskit', qiskit.__version__, '| runtime', qiskit_ibm_runtime.__version__)"
    ;;
  shell)
    exec /bin/bash
    ;;
  *)
    echo "unknown mode: $MODE (api|witness|boot|test|shell)" >&2
    exit 2
    ;;
esac

#!/usr/bin/env python3
"""
Multicast + Concurrency demo (UDP) for distributed systems labs.
- Runs as a simple multicast chat/heartbeat node.
- Demonstrates: joining/leaving a multicast group, sending messages, receiving concurrently,
  and processing messages in a worker pool.
Tested on Python 3.10+ (Linux, macOS, Windows).
"""
import argparse
import socket
import struct
import sys
import threading
import queue
import time
from datetime import datetime

# ---------- Worker that processes inbound messages concurrently ----------
def worker_loop(in_q: "queue.Queue[tuple[str, bytes]]", node_name: str, stop_event: threading.Event):
    while not stop_event.is_set():
        try:
            addr, data = in_q.get(timeout=0.25)
        except queue.Empty:
            continue
        try:
            msg = data.decode('utf-8', errors='replace')
        except Exception:
            msg = repr(data)
        stamp = datetime.utcnow().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{stamp}] [proc@{node_name}] from {addr}: {msg}")
        in_q.task_done()


def main():
    parser = argparse.ArgumentParser(description="Multicast + Concurrency Demo (chat & heartbeat).")
    parser.add_argument("--group", default="239.255.0.1", help="Multicast group (IPv4). Default: 239.255.0.1")
    parser.add_argument("--port", type=int, default=50000, help="UDP port. Default: 50000")
    parser.add_argument("--iface", default="0.0.0.0", help="Local interface IP used for joining/sending (e.g., your ZeroTier/Hamachi IP).")
    parser.add_argument("--name", default=None, help="Node name (defaults to hostname).")
    parser.add_argument("--ttl", type=int, default=1, help="Multicast TTL (hops). Default: 1")
    parser.add_argument("--workers", type=int, default=2, help="Number of concurrent processing workers. Default: 2")
    parser.add_argument("--no_heartbeat", action="store_true", help="Disable automatic heartbeat messages.")
    args = parser.parse_args()

    node_name = args.name or socket.gethostname()

    group = socket.inet_aton(args.group)
    iface_ip = socket.inet_aton(args.iface)

    # --- Create UDP socket ---
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    # Allow multiple sockets to bind the same address/port (useful for labs)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except Exception:
        pass

    # Bind on the port, all interfaces (receive)
    try:
        sock.bind(("", args.port))
    except OSError as e:
        print(f"Bind failed on port {args.port}: {e}", file=sys.stderr)
        sys.exit(2)

    # Join the multicast group on the specified interface
    mreq = struct.pack("=4s4s", group, iface_ip)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # Ensure we send via the desired interface
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, iface_ip)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, args.ttl)

    # Inbound processing queue + workers
    in_q: "queue.Queue[tuple[str, bytes]]" = queue.Queue(maxsize=1024)
    stop_event = threading.Event()
    workers = []
    for i in range(max(1, args.workers)):
        t = threading.Thread(target=worker_loop, args=(in_q, node_name, stop_event), daemon=True)
        t.start()
        workers.append(t)

    # Receiver thread to push datagrams into the worker queue
    def recv_loop():
        while not stop_event.is_set():
            try:
                data, addr = sock.recvfrom(65535)
            except OSError:
                break
            try:
                in_q.put_nowait((f"{addr[0]}:{addr[1]}", data))
            except queue.Full:
                # Drop if overwhelmed (demonstrates backpressure scenario)
                pass

    recv_t = threading.Thread(target=recv_loop, daemon=True)
    recv_t.start()

    # Optional: periodic heartbeat
    def heartbeat_loop():
        while not stop_event.is_set():
            hb = f"HB from {node_name} @ {datetime.utcnow().isoformat()}Z"
            try:
                sock.sendto(hb.encode("utf-8"), (socket.inet_ntoa(group), args.port))
            except Exception as e:
                print(f"Heartbeat send failed: {e}", file=sys.stderr)
            time.sleep(5)

    if not args.no_heartbeat:
        hb_t = threading.Thread(target=heartbeat_loop, daemon=True)
        hb_t.start()
    else:
        hb_t = None

    print("----------------------------------------------------------")
    print(f"Multicast node '{node_name}' on group {socket.inet_ntoa(group)}:{args.port}")
    print(f"Interface: {args.iface} | Workers: {len(workers)} | TTL: {args.ttl}")
    print("Type a message and press ENTER to multicast. Ctrl+C to exit.")
    print("----------------------------------------------------------")

    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.rstrip("\n")
            if not line:
                continue
            payload = f"[{node_name}] {line}".encode('utf-8')
            sock.sendto(payload, (socket.inet_ntoa(group), args.port))
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        try:
            # Drop membership (best effort)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
        except Exception:
            pass
        sock.close()
        recv_t.join(timeout=1.0)
        for t in workers:
            t.join(timeout=1.0)
        if hb_t:
            hb_t.join(timeout=1.0)


if __name__ == "__main__":
    main()

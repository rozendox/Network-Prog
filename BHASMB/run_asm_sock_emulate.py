#!/usr/bin/env python3
"""
run_asm_sock_emulate.py

- Monta assembly x86_64 com Keystone.
- Emula execução com Unicorn.
- Assembly realiza (pela ABI custom):
    rax = 0xF000 -> socket(domain, type, protocol) -> returns fd in rax
    rax = 0xF001 -> connect(fd, sockaddr_ptr, addrlen) -> returns 0/-1
    rax = 0xF002 -> send(fd, buf_ptr, len, flags) -> returns bytes_sent
    rax = 0xF003 -> recv(fd, buf_ptr, len, flags) -> returns bytes_recv (writes to memory)
    rax = 0xF004 -> close(fd) -> returns 0/-1
    rax = 0xF00F -> exit(status) -> stops emulation

- The emulator intercepts the 'syscall' instruction and performs the mapped Python socket calls.
"""

import socket
import struct
import sys
from keystone import Ks, KS_ARCH_X86, KS_MODE_64
from unicorn import Uc, UC_ARCH_X86, UC_MODE_64
from unicorn.x86_const import UC_X86_REG_RAX, UC_X86_REG_RDI, UC_X86_REG_RSI, UC_X86_REG_RDX, UC_X86_REG_RCX, UC_X86_REG_R8
from unicorn.x86_const import UC_X86_REG_RIP
from unicorn import UC_ERR_OK

# Emulation memory layout
ADDRESS = 0x1000000
MEM_SIZE = 2 * 1024 * 1024  # 2MB

# ABI opcodes (custom)
OP_SOCKET = 0xF000
OP_CONNECT = 0xF001
OP_SEND = 0xF002
OP_RECV = 0xF003
OP_CLOSE = 0xF004
OP_EXIT = 0xF00F

# Target to connect (change as needed)
TARGET_HOST = "127.0.0.1"
TARGET_PORT = 9999

# Message to send
MSG = b"Hello from emulated ASM!\n"

# Assembly code (Intel syntax)
# The assembly will:
#  - call socket via OP_SOCKET (rax=OP_SOCKET, rdi=domain, rsi=type, rdx=protocol) -> socket fd returned in rax
#  - build sockaddr_in in data section (sin_family, sin_port (network endian), sin_addr)
#  - call connect via OP_CONNECT (rax=OP_CONNECT, rdi=fd, rsi=addr_ptr, rdx=addrlen)
#  - call send via OP_SEND (rax=OP_SEND, rdi=fd, rsi=buf_ptr, rdx=len)
#  - call close via OP_CLOSE (rax=OP_CLOSE, rdi=fd)
#  - call exit via OP_EXIT (rax=OP_EXIT, rdi=status)
ASM = fr"""
    default rel
    section .text
    global _start
_start:
    ; socket(AF_INET=2, SOCK_STREAM=1, proto=0)
    mov rax, {OP_SOCKET}
    mov rdi, 2
    mov rsi, 1
    xor rdx, rdx
    syscall

    ; store returned fd at [fd_store]
    mov rbx, rax
    mov qword [rel fd_store], rbx

    ; prepare connect: rdi = fd, rsi = &sockaddr, rdx = 16
    mov rax, {OP_CONNECT}
    mov rdi, rbx
    lea rsi, [rel sockaddr]
    mov rdx, 16
    syscall

    ; send: rax=OP_SEND, rdi=fd, rsi=msg_ptr, rdx=len
    mov rax, {OP_SEND}
    mov rdi, rbx
    lea rsi, [rel message]
    mov rdx, {len(MSG)}
    syscall

    ; close
    mov rax, {OP_CLOSE}
    mov rdi, rbx
    syscall

    ; exit with status 0
    mov rax, {OP_EXIT}
    xor rdi, rdi
    syscall

section .data
fd_store: dq 0

; sockaddr_in layout: 16 bytes
; struct sockaddr_in {'''
;   short sin_family;     2 bytes
;   unsigned short sin_port; 2 bytes (network order)
;   struct in_addr sin_addr; 4 bytes
;   unsigned char sin_zero[8];
; '''};
sockaddr:
    ; sin_family = AF_INET (2) : 2 bytes (little endian)
    dw 2
    ; sin_port network endian: we'll fill placeholder 0x0000 and then overwrite in Python bytes if desired;
    dw 0x0000
    ; sin_addr (4 bytes) - we'll fill later (0.0.0.0 placeholder)
    dd 0
    ; padding 8 bytes
    times 8 db 0

message:
    db {','.join(str(b) for b in MSG)}
"""

def assemble(asm_text: str) -> bytes:
    ks = Ks(KS_ARCH_X86, KS_MODE_64)
    encoding, count = ks.asm(asm_text, as_bytes=True)
    return encoding

class SyscallHandler:
    """
    Handles the custom 'syscall' opcodes produced by the ASM:
    maps OP_* codes to Python socket operations.
    """
    def __init__(self, uc: Uc):
        self.uc = uc
        self.sockets = {}  # fd -> socket.socket
        self.next_fd = 3   # emulate fd numbers (0,1,2 reserved)

    def read_reg(self, reg_const):
        return self.uc.reg_read(reg_const)

    def write_reg(self, reg_const, value):
        self.uc.reg_write(reg_const, value)

    def read_mem(self, addr, size):
        return self.uc.mem_read(addr, size)

    def write_mem(self, addr, data: bytes):
        return self.uc.mem_write(addr, data)

    def handle(self):
        """
        Called when a 'syscall' instruction is executed in the emulated code.
        Reads rax to decide which custom operation to perform.
        """
        rax = self.read_reg(UC_X86_REG_RAX)
        if rax == OP_SOCKET:
            self._op_socket()
        elif rax == OP_CONNECT:
            self._op_connect()
        elif rax == OP_SEND:
            self._op_send()
        elif rax == OP_RECV:
            self._op_recv()
        elif rax == OP_CLOSE:
            self._op_close()
        elif rax == OP_EXIT:
            self._op_exit()
        else:
            # Unrecognized: set rax to -1 and continue
            self.write_reg(UC_X86_REG_RAX, (2**64 - 1))  # -1 in unsigned 64-bit
            print(f"[handler] unknown op: 0x{rax:x}")

    def _op_socket(self):
        # rdi = domain, rsi = type, rdx = protocol
        domain = self.read_reg(UC_X86_REG_RDI)
        typ = self.read_reg(UC_X86_REG_RSI)
        proto = self.read_reg(UC_X86_REG_RDX)
        # Map domain/type to Python socket family/type
        fam = socket.AF_INET if domain == 2 else socket.AF_INET
        stype = socket.SOCK_STREAM if typ == 1 else socket.SOCK_STREAM
        s = socket.socket(fam, stype, proto)
        fd = self.next_fd
        self.next_fd += 1
        self.sockets[fd] = s
        # return fd in rax
        self.write_reg(UC_X86_REG_RAX, fd)
        print(f"[handler] socket() -> fd={fd}")

    def _read_sockaddr(self, ptr):
        # sockaddr_in is 16 bytes: family(2), port(2), addr(4), zeros(8)
        raw = self.read_mem(ptr, 16)
        # unpack: <H H I 8s  => family (little), port (little), addr, padding
        family, port_le, addr, _pad = struct.unpack("<HHI8s", raw)
        # port in network order stored in memory: assembly stored as little-endian value.
        # The assembly left placeholder 0x0000; we'll interpret port_le as little-endian port.
        # For correctness, convert port from network order if needed.
        # Here we assume assembly wrote network-order (big-endian) into the two bytes; handle both:
        # Try interpreting as big-endian if value looks like port > 255
        # Simpler: use bytes directly to get network-order port:
        bytes_port = raw[2:4]
        port = struct.unpack("!H", bytes_port)[0]  # network (big-endian)
        ip = socket.inet_ntoa(struct.pack("<I", addr))  # addr stored little-endian dd
        return family, port, ip

    def _op_connect(self):
        # rdi = fd, rsi = sockaddr_ptr, rdx = addrlen
        fd = int(self.read_reg(UC_X86_REG_RDI))
        sockaddr_ptr = int(self.read_reg(UC_X86_REG_RSI))
        addrlen = int(self.read_reg(UC_X86_REG_RDX))
        if fd not in self.sockets:
            self.write_reg(UC_X86_REG_RAX, (2**64 - 1))
            print(f"[handler] connect(): invalid fd {fd}")
            return
        try:
            family, port, ip = self._read_sockaddr(sockaddr_ptr)
            s = self.sockets[fd]
            # Try connecting (may block depending on socket)
            s.settimeout(5.0)
            s.connect((ip, port))
            self.write_reg(UC_X86_REG_RAX, 0)
            print(f"[handler] connect(fd={fd}) -> connected to {ip}:{port}")
        except Exception as e:
            print(f"[handler] connect error: {e}")
            self.write_reg(UC_X86_REG_RAX, (2**64 - 1))

    def _op_send(self):
        # rdi = fd, rsi = buf_ptr, rdx = len, rcx = flags (we'll ignore flags)
        fd = int(self.read_reg(UC_X86_REG_RDI))
        buf_ptr = int(self.read_reg(UC_X86_REG_RSI))
        length = int(self.read_reg(UC_X86_REG_RDX))
        if fd not in self.sockets:
            self.write_reg(UC_X86_REG_RAX, (2**64 - 1))
            print(f"[handler] send(): invalid fd {fd}")
            return
        data = self.read_mem(buf_ptr, length)
        try:
            sent = self.sockets[fd].send(data)
            self.write_reg(UC_X86_REG_RAX, sent)
            print(f"[handler] send(fd={fd}) -> sent {sent} bytes")
        except Exception as e:
            print(f"[handler] send error: {e}")
            self.write_reg(UC_X86_REG_RAX, (2**64 - 1))

    def _op_recv(self):
        # rdi = fd, rsi = buf_ptr, rdx = len, rcx = flags
        fd = int(self.read_reg(UC_X86_REG_RDI))
        buf_ptr = int(self.read_reg(UC_X86_REG_RSI))
        length = int(self.read_reg(UC_X86_REG_RDX))
        if fd not in self.sockets:
            self.write_reg(UC_X86_REG_RAX, (2**64 - 1))
            print(f"[handler] recv(): invalid fd {fd}")
            return
        try:
            data = self.sockets[fd].recv(length)
            # write received bytes into emulated memory at buf_ptr
            self.write_mem(buf_ptr, data + b'\x00' * max(0, length - len(data)))
            self.write_reg(UC_X86_REG_RAX, len(data))
            print(f"[handler] recv(fd={fd}) -> received {len(data)} bytes")
        except Exception as e:
            print(f"[handler] recv error: {e}")
            self.write_reg(UC_X86_REG_RAX, (2**64 - 1))

    def _op_close(self):
        fd = int(self.read_reg(UC_X86_REG_RDI))
        if fd not in self.sockets:
            self.write_reg(UC_X86_REG_RAX, (2**64 - 1))
            print(f"[handler] close(): invalid fd {fd}")
            return
        try:
            self.sockets[fd].close()
            del self.sockets[fd]
            self.write_reg(UC_X86_REG_RAX, 0)
            print(f"[handler] close(fd={fd}) -> closed")
        except Exception as e:
            print(f"[handler] close error: {e}")
            self.write_reg(UC_X86_REG_RAX, (2**64 - 1))

    def _op_exit(self):
        status = int(self.read_reg(UC_X86_REG_RDI)) & 0xFF
        print(f"[handler] exit(status={status}) -> stopping emulation")
        # Stop emulation by raising Unicorn exception via uc.emu_stop
        # There's no direct stop API inside hook; set a sentinel in RAX and let caller stop emulator.
        # We'll set RAX to a special magic to indicate stop.
        self.write_reg(UC_X86_REG_RAX, 0xDEADBEEF)
        # Save status in an internal variable (could be returned)
        self.exit_status = status

def main():
    # Assemble
    try:
        code = assemble(ASM)
    except Exception as e:
        print("Assembly error:", e)
        sys.exit(1)

    uc = Uc(UC_ARCH_X86, UC_MODE_64)
    uc.mem_map(ADDRESS, MEM_SIZE)
    uc.mem_write(ADDRESS, code)

    # Patch sockaddr port and ip inside emulated memory to TARGET_HOST:TARGET_PORT
    # Find offset of 'sockaddr' symbol: we know code contains data after text; easiest: we'll search for the placeholder bytes
    # The placeholder for port was 0x0000 at offset where 'dw 0x0000' placed it. We'll search for the message bytes to compute offsets.
    full_mem = uc.mem_read(ADDRESS, len(code))
    # Write back entire assembled binary then overwrite sockaddr fields by searching for the message bytes to compute relative layout.
    # Simpler approach: compute offsets by re-assembling and scanning for the message pattern (MSG)
    msg_bytes = MSG
    mem_all = uc.mem_read(ADDRESS, len(code))
    msg_idx = mem_all.find(msg_bytes)
    if msg_idx == -1:
        print("Couldn't locate message bytes in assembled image; aborting patch.")
    else:
        # Compute likely sockaddr location: assembly placed data after text; search backwards for two zero bytes before msg (dw 0x0000)
        # We'll search for sequence of 16 bytes of sockaddr pattern: family(0x02 0x00) followed by two bytes (port)
        # Look for b'\x02\x00' near the message but earlier.
        sockaddr_pattern_idx = mem_all.rfind(b'\x02\x00', 0, msg_idx)
        if sockaddr_pattern_idx == -1:
            print("Couldn't locate sockaddr pattern; proceeding without patch (may attempt to connect to 0.0.0.0).")
            sockaddr_addr = None
        else:
            sockaddr_addr = ADDRESS + sockaddr_pattern_idx
            # Build sockaddr struct with network-order port and ip
            port_net = struct.pack("!H", TARGET_PORT)  # network byte order (big-endian)
            ip_packed = socket.inet_aton(TARGET_HOST)  # network order (big-endian)
            # The assembly used dd 0 (which is little-endian), so we must write ip as little-endian dword
            ip_le = struct.pack("<I", struct.unpack("!I", ip_packed)[0])
            sockaddr_bytes = b'\x02\x00' + port_net + ip_le + (b'\x00' * 8)
            uc.mem_write(sockaddr_addr, sockaddr_bytes)
            print(f"[setup] wrote sockaddr at 0x{sockaddr_addr:x} for {TARGET_HOST}:{TARGET_PORT}")

    # Prepare syscall handler and instruction hook
    handler = SyscallHandler(uc)

    # Hook code: intercept 'syscall' instruction and call handler
    def hook_code(mu, address, size, user_data):
        # read first two bytes at rip to check for 'syscall' opcode 0x0f 0x05
        try:
            instr = mu.mem_read(address, 2)
        except Exception:
            return
        if instr == b'\x0f\x05':
            # Advance RIP past the syscall instruction so when handler returns, execution continues
            rip = mu.reg_read(UC_X86_REG_RIP)
            mu.reg_write(UC_X86_REG_RIP, rip + 2)
            # Call handler
            handler.handle()
            # If handler set RAX to magic indicating exit, stop emulation
            rax = mu.reg_read(UC_X86_REG_RAX)
            if rax == 0xDEADBEEF:
                mu.emu_stop()

    uc.hook_add(callback=hook_code)

    # Set initial RIP
    try:
        start = ADDRESS
        uc.reg_write(UC_X86_REG_RIP, start)
        print("[emu] starting emulation...")
        uc.emu_start(start, ADDRESS + len(code))
    except Exception as e:
        # Unicorn raises when emulation stopped or errors; we catch and inspect RAX to determine exit
        if isinstance(e, Exception):
            # If emu stopped normally, check handler.exit_status if present
            try:
                status = getattr(handler, "exit_status", None)
                print(f"[emu] stopped. exit_status={status}")
            except Exception:
                print("[emu] stopped with exception:", e)
        else:
            print("[emu] exception:", e)

    print("[emu] finished. sockets created:", list(handler.sockets.keys()))

if __name__ == "__main__":
    main()

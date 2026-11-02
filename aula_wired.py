"""AULA F87 Pro wired (USB-C) lighting control, mirroring hub.aulacn.com's protocol.

Read config:  feature report 0x06, payload 84 00 00 01 00 80          -> reply: 7-byte header + 128 config bytes
Write config: feature report 0x06, payload 04 00 00 01 00 80 00 + 128 config bytes (zero padded to 519)
Config bytes 9-10 = lighting mode (big endian). Mode 0 = lights off.

Usage:
  python aula_wired.py read                 # print current config (read-only)
  python aula_wired.py mode <n>             # set lighting mode (0 = off)
  python aula_wired.py restore <hexfile>    # write a saved 128-byte config back
"""
import sys, time, hid

VID, PID = 0x258A, 0x010C
RID, LEN = 0x06, 520


def open_dev():
    for d in hid.enumerate(VID, PID):
        if d['usage_page'] == 0xFF00:
            return hid.Device(path=d['path'])
    sys.exit('Keyboard vendor interface not found (is it plugged in by cable?)')


def send(dev, payload):
    buf = bytes([RID]) + bytes(payload)
    dev.send_feature_report(buf + bytes(LEN - len(buf)))


def read_config(dev):
    send(dev, [0x84, 0, 0, 1, 0, 0x80])
    time.sleep(0.05)
    r = dev.get_feature_report(RID, LEN)
    if r[0] == RID:
        r = r[1:]
    if r[0] != 0x84:
        sys.exit(f'Unexpected reply: {bytes(r[:16]).hex(" ")}')
    return bytearray(r[7:7 + 128])


def write_config(dev, cfg):
    assert len(cfg) == 128
    send(dev, [0x04, 0, 0, 1, 0, 0x80, 0] + list(cfg))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'read'
    dev = open_dev()
    cfg = read_config(dev)
    if cmd == 'read':
        print(cfg.hex())
        print('mode =', cfg[9] << 8 | cfg[10], ' sleep byte[24] =', cfg[24])
    elif cmd == 'mode':
        n = int(sys.argv[2])
        cfg[9], cfg[10] = (n >> 8) & 0xFF, n & 0xFF
        write_config(dev, cfg)
        time.sleep(0.2)
        new = read_config(dev)
        print('mode now =', new[9] << 8 | new[10])
    elif cmd == 'restore':
        data = bytes.fromhex(open(sys.argv[2]).read().split()[0])
        write_config(dev, bytearray(data))
        time.sleep(0.2)
        print('restored; mode now =', (lambda c: c[9] << 8 | c[10])(read_config(dev)))
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()

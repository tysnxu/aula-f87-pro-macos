# AULA F87 Pro lighting control on macOS (USB-C cable)

Findings and a small tool for controlling the AULA F87 Pro (USB 258A:010C) without an official macOS driver.

## Usage
Needs `brew install hidapi` and `uv`. Plug in by cable (the settings channel is not reachable over Bluetooth or without the cable).

    ./aula off        # lighting mode 0
    ./aula on         # restore config-wired-original.txt (mode 8)
    ./aula read       # print config, mode and sleep byte
    ./aula mode <n>   # set lighting mode (1-4 tested; keys lit)

`config-wired-original.txt` is one keyboard's original 128-byte config. Read your own with `./aula read` and save it before writing anything.

## Protocol (from hub.aulacn.com's JS)
Vendor interface: usage page 0xFF00, feature report ID 0x06, 520 bytes.
- Read config: send `84 00 00 01 00 80`; reply = 7-byte header + 128 config bytes (ends `5a a5`).
- Write config: send `04 00 00 01 00 80 00` + the 128 bytes.
- Config bytes 9-10: lighting mode, big-endian. 0 = off.
- Config byte 24: sleep time. The hub offers Never/1/5/30 min; value is probably minutes (unverified).
- Other commands seen: `8a 00 00 01 00 e3 01` light colours (21-byte pattern repeated per mode, no separate side-strip entry), `86 .. 7a 01` per-key colours, `87 00 00 01 00 02` power/battery, `83`/`03` read/write keys.

## Why the web hub fails
It looks for `FF FF` in the config to find its per-effect brightness table. This keyboard has `80 8F` at offset 56, so the hub throws "Configuration table is incorrect" before any lighting write, including its OFF button. `aula_wired.py` skips that check.

## What worked / didn't
- Mode and sleep writes over the cable work (verified by read-back and by eye).
- The Fn shortcut turned off the key lights but not the side strip; no separate side-strip control was found.
- Practical workaround: after setting the short sleep timer, switch the keyboard to Bluetooth at night; it sleeps and the lights go out.
- The 2.4 GHz dongle uses a different 20-byte output-report protocol (see the Aula-F87-Controller repo by marcoslor); not tested here.

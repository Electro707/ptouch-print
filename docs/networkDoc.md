# libptouch network daemon

This daemon is one that can allow any printer compatible with `libptouch` to be utilized over the network.

# Protocol
This page describes the protocol used by this daemon to allow connecting to a Brother P-Touch label connected to a Pi (or other SBC) over the network

## Transport Layer
The protocol is sent over TCP/IP using port TODO.

## Hostname
For ease of lookup, the SBC shall have a hostname of 'ptouch' by default

## Application Layer
Data is sent and received  with an escape frame format, where a dedicated character (0xFA) is dedicates as the escape token. The character that follows (which cannot be an escape token itself) is the command. If the escape character is desired to be sent as part of the data, it is repeated twice.

After the escape token and command, the proceeding data (if any) is dictated by the command.

Any command that doesn't have a response shall return an ACK if successful. A NACK is returned on failure of acknowledge the command

The following are the available commands
- 0x01: Request the software version running. This can be used to determine this protocol version if things change in the future (by major number)
- 0x02: Set host name
	- The data is a string that changes the device's hostname (on next reboot). The string must end with a "\0"
- 0x03: Set dynamic IP on next reboot
- 0x04: Set static IP on next reboot
	- Byte 0 to 4: The IPv4 address
- 0x05: Reboot system
- 0x0A: Get printer info
- 0x10: Print raster image
	- Byte 0: Set to 0 to not eject after printing, 1 to cut and eject
	- Bytes 1 to n: The image data. This is expected to be a sequence of 16-byte (128 pixels) arrays
- 0x11: Advance the tape (no print) by n raster lines:
	- Byte 0: Number raster lines to advance by

The following are the available responses
- 0x01: First byte is major number, second is minor, third is bug fix, forth is version attributes, which can be:
	- 'd': Development
- 0x03:
	- Byte 0: If a printer is connected. If this is zero (nothing connected), the following data will be invalid
	- Byte 1: Tape width in mm
	- Byte 2: Media type
	- Byte 3: Media width in mm
	- Byte 4: Tape bg color
	- Byte 5: Tape text color
- 0xFE: ACK
- 0xFF: NACK

The following can be sent from the device to the host at any given time:
- 0x20: Printer status change
	- Byte 0: Error info 1
	- Byte 1: Error info 2
	- Byte 2: Status Type
	- Byte 3: Phase type
	- Byte 4 and 5: Phase number

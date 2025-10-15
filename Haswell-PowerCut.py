"""
	This is a reimplimentation of freecableguy's v3x4 VCCIN/PowerCut feature for Linux, written in Python
	Checkout the EFI driver here -> https://github.com/freecableguy/v3x4
"""

import os
import struct

# Mailbox command to set VCCIN and disable SVID
MailboxCmd = (
	# These are all constants from v3x4

	0x8000000000000000 | # OC_MB_COMMAND_EXEC
	0x0000001300000000 | # OC_MB_SET_SVID_PARAMS
	0x0000000000000000 | # OC_MB_DOMAIN_IACORE
	0x00000734 | # VCCIN (1.800 V)
	0x80000000 # OC_MB_FIVR_DYN_SVID_CONTROL_DIS
)

# Set CPU MSR to Value
def wrmsr(cpu, msr, value):
	msr_file = f"/dev/cpu/{cpu}/msr"
	with open(msr_file, "wb") as f:
		f.seek(msr)
		f.write(struct.pack("<Q", value))

# Read CPU MSR
def rdmsr(cpu, msr):
	msr_file = f"/dev/cpu/{cpu}/msr"
	with open(msr_file, "rb") as f:
		f.seek(msr)
		return struct.unpack("<Q", f.read(8))[0]


# Main script

if os.geteuid() != 0:
	print("This script requires root")
	exit(1)

if not os.path.exists(f"/dev/cpu/0/msr"):
	print("MSR module not loaded. Run: sudo modprobe msr")
	exit(1)

print(f"Writing to MSR 0x150...")
wrmsr(0, 0x150, MailboxCmd)

response = rdmsr(0, 0x150)
status = (response >> 32) & 0xFF

print("MSR Response: {0} -> {1}".format(response, status))

if status == 0x0:
	print("Success: PowerCut applied.")
elif status == 0x7:
	print("Reboot required for changes to take effect.")
else:
	print(f"Error: Mailbox returned status 0x{status:X}")

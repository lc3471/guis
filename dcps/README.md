Author: Laurel Carpenter
Date: 08/03/2021

Instructions for use of and explanation of development of modules for
communicating with instruments, currently including:
AimTTiEL302P, AimTTiCPX400DP, RigolDG5000, SiglentSDS1202XE, NewportESP301

Aim modules are based directly off of Stephen Goadhouse's AimTTiPLP class,
which inherits his SCPI class. The Rigol module follows the same setup as the
Aim modules and inherits SCPI, but commands were written by myself. Siglent
module does not inherit SCPI as there was a problem with the message chunk size
and machine timeout, though the instrument still uses SCPI language; all Siglent
 commands are written by myself. Newport module does not inherit SCPI as the
machine does not follow SCPI format (though machine still seems to respond to
basic SCPI commands like '*IDN?'); all Newport commands are written by myself.

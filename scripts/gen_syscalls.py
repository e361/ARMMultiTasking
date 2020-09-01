#!/usr/bin/python3

from textwrap import dedent

syscalls = """\
add_thread
get_thread_property
set_thread_property
get_kernel_config
set_kernel_config
yield
get_msg
send_msg
thread_wait
thread_wake
thread_cancel
mutex
open
read
write
lseek
remove
close
exit
malloc
realloc
free
list_dir""".split()

print(dedent("""\
/* Generated by scripts/gen_syscalls.py */
// clang-format off
#ifndef COMMON_SYSCALL_H
#define COMMON_SYSCALL_H

#ifdef __ASSEMBLER__
#ifdef __aarch64__
#define FNADDR .quad
#else
#define FNADDR .word
#endif"""))

for call in syscalls:
    print("  FNADDR k_{}".format(call))
# Some padding to catch off by something errors (only for asm)
for i in range(4):
    print("  FNADDR k_invalid_syscall")

print(dedent("""\
#else

#include <stddef.h>

typedef enum {"""))
first, rest = syscalls[0], syscalls[1:]
print("  syscall_{} = 0,".format(first))
for call in rest:
    print("  syscall_{},".format(call))

print(dedent("""\
  syscall_eol,
} Syscall;

size_t generic_syscall(Syscall num, size_t arg1, size_t arg2,
                       size_t arg3, size_t arg4);
"""))

for i in range(5):
    # +1s to start from ARG1 not ARG0
    args = "".join([", ARG{}".format(j+1) for j in range(i)])
    print("#define DO_SYSCALL_{}(NAME{}) \\".format(i, args))
    args = ["(size_t)(ARG{})".format(j+1) for j in range(i)]
    args.extend(["0"]*(4-i))
    args = ", ".join(args)
    print("  generic_syscall(syscall_##NAME, {})".format(args))

print(dedent("""
      #endif /* ifdef __ASSEMBLER__ */
      #endif /* ifdef COMMON_SYSCALL_H */"""))

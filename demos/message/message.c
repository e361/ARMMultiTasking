#include "common/assert.h"
#include "user/errno.h"
#include "user/thread.h"
#include "user/util.h"

__attribute__((noreturn)) void sender() {
  while (1) {
    if (send_msg(2, 99)) {
      log_event("sent a message");
    } else {
      log_event("message box was full");
    }

    yield();
  }
}

__attribute__((noreturn)) void spammer() {
  for (int i = 0;; ++i) {
    if (i == 2) {
      // just one msg this time
      send_msg(2, -1);
      log_event("not spamming");
    } else {
      // Clog the receivers messages
      bool sent = false;
      do {
        sent = send_msg(2, -1);
      } while (sent);
      log_event("spammed");
    }

    yield();
  }
}

__attribute__((noreturn)) void receiver() {
  while (1) {
    int sender, message;
    while (get_msg(&sender, &message)) {
      if (sender == 1) {
        log_event("got message from sender");
        exit(0);
      } else {
        log_event("discarded spam message");
      }
    }

    yield();
  }
}

void setup(void) {
  // Check syscall argument validation
  int tmp;
  errno = 0;
  assert(!get_msg(NULL, &tmp));
  assert(errno == E_INVALID_ARGS);

  errno = 0;
  assert(!get_msg(&tmp, NULL));
  assert(errno == E_INVALID_ARGS);

  add_named_thread(sender, "sender");
  add_named_thread(receiver, "receiver");
  set_thread_name(CURRENT_THREAD, "spammer");
  spammer();
}

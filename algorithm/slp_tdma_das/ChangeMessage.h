#ifndef SLP_MESSAGES_CHANGEMESSAGE_H
#define SLP_MESSAGES_CHANGEMESSAGE_H

#include "utils.h"

typedef nx_struct ChangeMessage {
    nx_am_addr_t source_id;
} ChangeMessage;

inline SequenceNumberWithBottom Change_get_sequence_number(const ChangeMessage* msg) { return BOTTOM; }
inline int32_t Change_get_source_id(const ChangeMessage* msg) { return msg->source_id; }

#endif /* SLP_MESSAGES_CHANGEMESSAGE_H */

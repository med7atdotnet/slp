#ifndef SLP_SERIAL_METRIC_LOGGING_H
#define SLP_SERIAL_METRIC_LOGGING_H

#include "AM.h"

// These constants are used to set the message channel and type
// The format of the name is required by the mig tool
enum {
	AM_ERROR_OCCURRED_MSG = 49,
	AM_METRIC_RECEIVE_MSG = 50,
	AM_METRIC_BCAST_MSG = 51,
	AM_METRIC_DELIVER_MSG = 52,
	AM_ATTACKER_RECEIVE_MSG = 53,
	AM_METRIC_NODE_CHANGE_MSG = 54,
	AM_METRIC_NODE_TYPE_ADD_MSG = 55,
	AM_METRIC_MESSAGE_TYPE_ADD_MSG = 56,
	//SLP TDMA DAS
	AM_METRIC_NODE_SLOT_CHANGE_MSG = 57,
};

#define MAXIMUM_NODE_TYPE_NAME_LENGTH 20
#define MAXIMUM_MESSAGE_TYPE_NAME_LENGTH 20

#define METRIC_LOGGING_HEADER \
	nx_am_id_t type; /* This is the type of debug/metric message*/ \
	nx_am_addr_t node_id; \
	nx_uint32_t local_time;

typedef nx_struct metric_receive_msg {
	METRIC_LOGGING_HEADER

	nx_uint8_t message_type;

	nx_am_addr_t proximate_source;
	nx_int16_t ultimate_source;

	nx_int64_t sequence_number;

	nx_int16_t distance;
} metric_receive_msg_t;

typedef nx_struct metric_bcast_msg {
	METRIC_LOGGING_HEADER

	nx_uint8_t message_type;

	nx_uint8_t status; // nx type for error_t

	nx_int64_t sequence_number;
} metric_bcast_msg_t;

typedef nx_struct metric_deliver_msg {
	METRIC_LOGGING_HEADER

	nx_uint8_t message_type;

	nx_am_addr_t proximate_source;
	nx_int32_t ultimate_source_poss_bottom;
	nx_int64_t sequence_number;
} metric_deliver_msg_t;

typedef nx_struct attacker_receive_msg {
	METRIC_LOGGING_HEADER
	nx_uint8_t message_type;

	nx_am_addr_t proximate_source;
	nx_int32_t ultimate_source_poss_bottom;
	nx_int64_t sequence_number;
} attacker_receive_msg_t;

typedef nx_struct metric_node_change_msg {
	METRIC_LOGGING_HEADER

	nx_uint8_t old_node_type;
	nx_uint8_t new_node_type;
} metric_node_change_msg_t;

typedef nx_struct metric_node_type_add_msg {
	METRIC_LOGGING_HEADER

	nx_uint8_t node_type_id;
	nx_uint8_t node_type_name[MAXIMUM_NODE_TYPE_NAME_LENGTH];

} metric_node_type_add_msg_t;

typedef nx_struct metric_message_type_add_msg {
	METRIC_LOGGING_HEADER

	nx_uint8_t message_type_id;
	nx_uint8_t message_type_name[MAXIMUM_MESSAGE_TYPE_NAME_LENGTH];

} metric_message_type_add_msg_t;

typedef nx_struct error_occurred_msg {
	METRIC_LOGGING_HEADER

	nx_uint16_t error_code;
} error_occurred_msg_t;

//##########SLP TDMA DAS##########
typedef nx_struct metric_node_slot_change_msg {
	METRIC_LOGGING_HEADER

	nx_uint16_t old_slot;
	nx_uint16_t new_slot;
} metric_node_slot_change_msg_t;

#endif // SLP_SERIAL_METRIC_LOGGING_H

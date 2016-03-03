#ifndef SLP_CONSTANTS_H
#define SLP_CONSTANTS_H

#define MESSAGE_QUEUE_SIZE 15

enum Channels
{
	NORMAL_CHANNEL = 1,
	DUMMY_NORMAL_CHANNEL = 2,
    BEACON_CHANNEL = 3,
    WAVE_CHANNEL = 4,
    COLLISION_CHANNEL = 5
};

#define SLP_MAX_NUM_SOURCES 20

#endif // SLP_CONSTANTS_H

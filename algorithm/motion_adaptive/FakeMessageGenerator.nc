#include "AwayChooseMessage.h"

interface FakeMessageGenerator
{
	command void start(const AwayChooseMessage* original_message, uint32_t period_ms);
	command void startLimited(const AwayChooseMessage* original_message, uint32_t period_ms, uint32_t duration_ms);

	command void stop();

	command void expireDuration();
	
	event void generateFakeMessage(FakeMessage* message);

	event void sent(error_t error, const FakeMessage* message);

	event void durationExpired(const AwayChooseMessage* original_message);
}
#include "Common.h"

module SourcePeriodModelImplP
{
	provides interface SourcePeriodModel;

	uses interface LocalTime<TMilli>;
}
implementation
{
	command uint32_t SourcePeriodModel.get()
	{
		typedef struct {
			uint32_t end;
			uint32_t period;
		} local_end_period_t;

		const local_end_period_t times[] = PERIOD_TIMES_MS;
		const uint32_t else_time = PERIOD_ELSE_TIME_MS;

		const unsigned int times_length = ARRAY_LENGTH(times);

		const uint32_t current_time = call LocalTime.get();

		unsigned int i;

		uint32_t period = -1;

		dbgverbose("stdout", "Called get_source_period current_time=%u #times=%u\n",
			current_time, times_length);

		for (i = 0; i != times_length; ++i)
		{
			//dbgverbose("stdout", "i=%u current_time=%u end=%u period=%u\n",
			//	i, current_time, times[i].end, times[i].period);

			if (current_time < times[i].end)
			{
				period = times[i].period;
				break;
			}
		}

		if (i == times_length)
		{
			period = else_time;
		}

		dbgverbose("stdout", "Providing source period %u at time=%u\n",
			period, current_time);
		return period;
	}
}
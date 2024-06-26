from __future__ import annotations

import cst_python as cst

from gbyg.time_utils import TimeInterval

class SummaryTriggerCodelet(cst.Codelet):
    def __init__(self, 
                 agent_info_memory_name:str | None=None, 
                 agent_time_memory_name:str | None=None, 
                 memory_stream_name:str | None = None,
                 characteristics_query_memory_name:str | None=None,
                 daily_occupation_query_memory_name:str | None = None,
                 progress_feeling_query_memory_name:str | None = None,
                 interval:float | None = None) -> None:
        super().__init__()

        if agent_info_memory_name is None:
            agent_info_memory_name = "AgentInfo"
        if agent_time_memory_name is None:
            agent_time_memory_name = "AgentTime"
        if memory_stream_name is None:
            memory_stream_name = "MemoryStream"
        if characteristics_query_memory_name is None:
            characteristics_query_memory_name = "characteristics_query"
        if daily_occupation_query_memory_name is None:
            daily_occupation_query_memory_name = "daily_occupation_query"
        if progress_feeling_query_memory_name is None:
            progress_feeling_query_memory_name = "progress_feeling_query"

        self._agent_info_memory_name = agent_info_memory_name
        self._agent_time_memory_name = agent_time_memory_name
        self._memory_stream_name = memory_stream_name
        self._characteristics_query_memory_name = characteristics_query_memory_name
        self._daily_occupation_query_memory_name = daily_occupation_query_memory_name
        self._progress_feeling_query_memory_name = progress_feeling_query_memory_name

        if interval is None:
            interval = TimeInterval.ONE_DAY

        self._interval = interval
        self._last_process = 0

    def access_memory_objects(self) -> None:
        self._agent_info_memory_mo = self.get_input(name=self._agent_info_memory_name)
        self._agent_time_memory_mo = self.get_input(name=self._agent_time_memory_name)
        self._memory_stream_mo = self.get_input(name=self._memory_stream_name)
        self._characteristics_query_memory_mo = self.get_output(name=self._characteristics_query_memory_name)
        self._daily_occupation_query_memory_mo = self.get_output(name=self._daily_occupation_query_memory_name)
        self._progress_feeling_query_memory_mo = self.get_output(name=self._progress_feeling_query_memory_name)
    
    def calculate_activation(self) -> None:
        pass

    def proc(self) -> None:
        agent_time = self._agent_time_memory_mo.get_info()
        agent_info = self._agent_info_memory_mo.get_info()
        memory_stream = self._memory_stream_mo.get_info()

        if agent_time is None or agent_time == "":
            return
        if agent_time-self._last_process  < self._interval:
            return
        
        if agent_info is None or agent_info == "":
            return
        
        if memory_stream is None or memory_stream == "" or len(memory_stream) == 0:
            return

        self._last_process = agent_time

        agent_name = agent_info["name"]

        characteristics_query = agent_name+" core characteristics"
        daily_occupation_query = agent_name+" current daily occupation"
        progress_feeling_query = agent_name+" feeling about his/her recent progress in life"

        self._characteristics_query_memory_mo.set_info(characteristics_query)
        self._daily_occupation_query_memory_mo.set_info(daily_occupation_query)
        self._progress_feeling_query_memory_mo.set_info(progress_feeling_query)
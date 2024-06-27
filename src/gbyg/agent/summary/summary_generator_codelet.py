from __future__ import annotations

from typing import List

import cst_python as cst


class SummaryGeneratorCodelet(cst.Codelet):
    def __init__(self,
                 agent_info_name:str|None = None, 
                 agent_time_name:str|None = None,
                 output_memory_name:str|None=None, 
                 separator:str | None=None) -> None:
        super().__init__()

        if agent_info_name is None:
            agent_info_name = "AgentInfo"
        if output_memory_name is None:
            output_memory_name = "Output"
        if agent_time_name is None:
            agent_time_name = "AgentTime"

        self._agent_info_name = agent_info_name
        self._output_memory_name = output_memory_name
        self._agent_time_name = agent_time_name

        if separator is None:
            separator = "\n"
        
        self._separator = separator

        self._last_proc = 0

    def access_memory_objects(self) -> None:
        self._agent_info_mo = self.get_input(name=self._agent_info_name)
        self._agent_time_mo = self.get_input(name=self._agent_time_name)
        self._output_memory_mo : cst.MemoryObject = self.get_output(name=self._output_memory_name)

    def calculate_activation(self) -> None:
        pass

    def proc(self) -> None:
        input_mos = self.inputs

        new_last_proc = self._last_proc
        infos = []
        for input_mo in input_mos:
            if input_mo.get_timestamp() > new_last_proc:
                new_last_proc = input_mo.get_timestamp()
            
            if input_mo != self._agent_info_mo and input_mo != self._agent_time_mo:
                infos.append(str(input_mo.get_info()))

        if new_last_proc == self._last_proc:
            return

        self._last_proc = new_last_proc

        agent_info = self._agent_info_mo.get_info()
        agent_info_str = f"Name: {agent_info['name']} (age: {agent_info['age']})\nInnate traits: {agent_info['traits']}"

        infos = [agent_info_str] + infos

        output = self._separator.join(infos)

        output = {"summary":output}
        output["generated_time"] = self._agent_time_mo.get_info()

        self._output_memory_mo.set_info(output)
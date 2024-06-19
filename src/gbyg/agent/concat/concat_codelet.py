from __future__ import annotations

from typing import List

import cst_python as cst


class TextConcatCodelet(cst.Codelet):
    def __init__(self, 
                 output_memory_name:str|None=None, 
                 separator:str | None=None) -> None:
        super().__init__()

        if output_memory_name is None:
            output_memory_name = "Output"

        self._output_memory_name = output_memory_name

        if separator is None:
            separator = "\n"
        
        self._separator = separator

        self._last_proc = 0

    def access_memory_objects(self) -> None:
        self._output_memory_mo = self.get_output(name=self._output_memory_name)

    def calculate_activation(self) -> None:
        pass

    def proc(self) -> None:
        input_mos = self.inputs

        new_last_proc = self._last_proc
        infos = []
        for input_mo in input_mos:
            if input_mo.get_timestamp() > new_last_proc:
                new_last_proc = input_mo.get_timestamp()

            infos.append(str(input_mo.get_info()))

        if new_last_proc == self._last_proc:
            return
        
        self._last_proc = new_last_proc

        output = self._separator.join(infos)

        self._output_memory_mo.set_info(output)
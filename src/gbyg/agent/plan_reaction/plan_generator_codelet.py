from __future__ import annotations

import datetime

import cst_python as cst

from .plan_generator_tool import PlanGenerator
from .plan_decomposer_tool import PlanDecomposer

class PlanGeneratorCodelet(cst.Codelet):
    def __init__(self, 
                 agent_info_memory_name:str | None=None, 
                 agent_time_memory_name:str | None=None, 
                 agent_summary_description_memory_name:str | None = None,
                 previous_day_summary_name : str|None = None,
                 plan_memory_name:str|None = None,
                 model_name:str|None=None) -> None:
        super().__init__()

        if agent_info_memory_name is None:
            agent_info_memory_name = "AgentInfo"
        if agent_time_memory_name is None:
            agent_time_memory_name = "AgentTime"
        if agent_summary_description_memory_name is None:
            agent_summary_description_memory_name = "MemoryStream"
        if plan_memory_name is None:
            plan_memory_name = "Plan"
        if previous_day_summary_name is None:
            previous_day_summary_name = "PreviousDaySummary"

        self._agent_info_memory_name = agent_info_memory_name
        self._agent_time_memory_name = agent_time_memory_name
        self._agent_summary_description_memory_name = agent_summary_description_memory_name
        self._plan_memory_name = plan_memory_name
        self._previous_day_summary_name = previous_day_summary_name

        self._last_process = None

        self._plan_generator = PlanGenerator(model_name)
        self._plan_decomposer = PlanDecomposer(model_name)

    def access_memory_objects(self) -> None:
        self._agent_info_memory_mo = self.get_input(name=self._agent_info_memory_name)
        self._agent_time_memory_mo = self.get_input(name=self._agent_time_memory_name)
        self._agent_summary_description_memory_mo = self.get_input(name=self._agent_summary_description_memory_name)
        self._previous_day_summary_mo = self.get_input(name=self._previous_day_summary_name)
        
        self._plan_memory_mo = self.get_output(name=self._plan_memory_name)

    def calculate_activation(self) -> None:
        pass

    def proc(self) -> None:
        agent_time = self._agent_time_memory_mo.get_info()

        if agent_time is None or agent_time == "":
            return

        if self._last_process is None:
            self._last_process = agent_time

        #Check if is a new day
        last_day = datetime.datetime.fromtimestamp(self._last_process).day
        today_day = datetime.datetime.fromtimestamp(agent_time).day

        if today_day == last_day:
            return
        
        #Check if summary description is new
        agent_summary_description = self._agent_summary_description_memory_mo.get_info()
        generated_time = agent_summary_description["generated_time"]
        generated_day = datetime.datetime.fromtimestamp(generated_time).day

        if generated_day != today_day:
            return
        
        #Check if previous day summary is new
        previous_day_summary = self._previous_day_summary_mo.get_info()
        generated_time = previous_day_summary["generated_time"]
        generated_day = datetime.datetime.fromtimestamp(generated_time).day

        if generated_day != today_day:
            return

        #Update last process
        self._last_process = agent_time

        #Generate plan
        agent_info = self._agent_info_memory_mo.get_info()
        today_date = datetime.datetime.fromtimestamp(agent_time).strftime("%A %B %d")

        query = {"summary_description":agent_summary_description["summary"],
                "previous_day_summary":previous_day_summary["summary"],
                "today_date":today_date,
                "agent_name":agent_info["name"]}

        plan_result, _ = self._plan_generator(query)
        
        #Decompose plan
        final_plan = []
        for action in plan_result["plan"]:
            original_action = f"At {action['hour']}: {action['action']}"
            query = {"original_plan":original_action,
                    "minimum_minutes":'10'}
            
            decomposer_result, _ = self._plan_decomposer(query)

            remove_indexes = []
            for index, new_action in enumerate(decomposer_result["plan"]):
                if new_action["hour"] != action["hour"]:
                    remove_indexes.append(index)
            for index in reversed(remove_indexes):
                del decomposer_result["plan"][index]

            final_plan += decomposer_result["plan"]

        #Sort by time and send to memory
        final_plan = sorted(final_plan, key=lambda action : (60*action["hour"])+ action["minute"])

        self._plan_memory_mo.set_info(final_plan)
            
            

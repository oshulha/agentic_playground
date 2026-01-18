#deepresearch.py
import asyncio
import time
from helper import call_OpenAI_model, call_Gemini_model
from planner_agent import planner_agent, ReportPlan, ReportPlanSection
from typing import List, Optional

MAX_ITERATIONS = 5

async def start():
    global MAX_ITERATIONS
    MAX_ITERATIONS = input("Input number of max iterations: ")
    plan = asyncio.run(deep("Tell me about quantum computers"))
    #print(plan)

async def deep(query: str) -> str:
        """Run the deep research workflow"""

        # First build the report plan which outlines the sections and compiles any relevant background context on the query
        report_plan: ReportPlan = await _build_report_plan(query)

        # Run the independent research loops concurrently for each section and gather the results
        research_results: List[str] = await _run_research_loops(report_plan)

        # Create the final report from the original report plan and the drafts of each section
        #final_report: str = await self._create_final_report(query, report_plan, research_results)

        #_log_message(f"DeepResearcher completed in (no time) minutes and (no time) seconds")

        return report_plan

        #return final_report

async def _build_report_plan(query: str) -> ReportPlan:
    """Build the initial report plan including the report outline (sections and key questions) and background context"""
    #_log_message("=== Building Report Plan ===")
    user_message = f"QUERY: {query}"
    result = await planner_agent(user_message)
    report_plan = result.final_output_as(ReportPlan)

    #verbose
    # num_sections = len(report_plan.report_outline)
    # message_log = '\n\n'.join(f"Section: {section.title}\nKey question: {section.key_question}" for section in report_plan.report_outline)
    # if report_plan.background_context:
    #     message_log += f"\n\nThe following background context has been included for the report build:\n{report_plan.background_context}"
    # else:
    #     message_log += "\n\nNo background context was provided for the report build.\n"
    #_log_message(f"Report plan created with {num_sections} sections:\n{message_log}")
    #verbose

    return report_plan

# plan = asyncio.run(deep("Tell me about quantum computers"))
# print(plan)

async def _run_research_loops(report_plan: ReportPlan) -> List[str]:
        """For a given ReportPlan, run a research loop concurrently for each section and gather the results"""
        async def run_research_for_section(section: ReportPlanSection):
            args = {
                "query": section.key_question,
                "output_length": "",
                "output_instructions": "",
                "background_context": report_plan.background_context,
                "iteration" : section.iteration
            }
            return await simple(**args)
        
        #_log_message("=== Initializing Research Loops ===")
        # Run all research loops concurrently in a single gather call
        research_results = await asyncio.gather(
            *(run_research_for_section(section) for section in report_plan.report_outline)
        )
        return research_results

async def simple(
            query: str,
            iteration: int,
            should_continue: str,
            output_length: str = "",  # A text description of the desired output length, can be left blank
            output_instructions: str = "",  # Instructions for the final report (e.g. don't include any headings, just a couple of paragraphs of text)
            background_context: str = "",
        ) -> str:
        """Run the deep research workflow for a given query."""

        #_log_message("=== Starting Iterative Research Workflow ===")
        
        # Iterative research loop
        while should_continue and _check_constraints():
            iteration += 1
            #_log_message(f"\n=== Starting Iteration {iteration} ===")

            # Set up blank IterationData for this iteration
            self.conversation.add_iteration()

            # 1. Generate observations
            observations: str = await self._generate_observations(query, background_context=background_context)

            # 2. Evaluate current gaps in the research
            evaluation: KnowledgeGapOutput = await self._evaluate_gaps(query, background_context=background_context)
            
            # Check if we should continue or break the loop
            if not evaluation.research_complete:
                next_gap = evaluation.outstanding_gaps[0]

                # 3. Select agents to address knowledge gap
                selection_plan: AgentSelectionPlan = await self._select_agents(next_gap, query, background_context=background_context)

                # 4. Run the selected agents to gather information
                results: Dict[str, ToolAgentOutput] = await self._execute_tools(selection_plan.tasks)
            else:
                self.should_continue = False
                self._log_message("=== IterativeResearcher Marked As Complete - Finalizing Output ===")
        
        # Create final report
        report = await self._create_final_report(query, length=output_length, instructions=output_instructions)
        
        self._log_message(f"IterativeResearcher completed in (no time) minutes and (no time) seconds after {self.iteration} iterations.")

        return report
    
    def _check_constraints(self) -> bool:
        """Check if we've exceeded our constraints (max iterations or time)."""
        if self.iteration >= self.max_iterations:
            self._log_message("\n=== Ending Research Loop ===")
            self._log_message(f"Reached maximum iterations ({self.max_iterations})")
            return False
        
        elapsed_minutes = (time.time() - self.start_time) / 60
        if elapsed_minutes >= self.max_time_minutes:
            self._log_message("\n=== Ending Research Loop ===")
            self._log_message(f"Reached maximum time ({self.max_time_minutes} minutes)")
            return False
        
        return True
    
    async def _evaluate_gaps(
        self, 
        query: str,
        background_context: str = ""
    ) -> KnowledgeGapOutput:
        """Evaluate the current state of research and identify knowledge gaps."""

        background = f"BACKGROUND CONTEXT:\n{background_context}" if background_context else ""

        input_str = f"""
        Current Iteration Number: {self.iteration}
        Time Elapsed: {(time.time() - self.start_time) / 60:.2f} minutes of maximum {self.max_time_minutes} minutes

        ORIGINAL QUERY:
        {query}

        {background}

        HISTORY OF ACTIONS, FINDINGS AND THOUGHTS:
        {self.conversation.compile_conversation_history() or "No previous actions, findings or thoughts available."}        
        """

        result = await ResearchRunner.run(
            self.knowledge_gap_agent,
            input_str,
        )
        
        evaluation = result.final_output_as(KnowledgeGapOutput)

        if not evaluation.research_complete:
            next_gap = evaluation.outstanding_gaps[0]
            self.conversation.set_latest_gap(next_gap)
            self._log_message(self.conversation.latest_task_string())
        
        return evaluation
    
    async def _select_agents(
        self, 
        gap: str, 
        query: str,
        background_context: str = ""
    ) -> AgentSelectionPlan:
        """Select agents to address the identified knowledge gap."""
        
        background = f"BACKGROUND CONTEXT:\n{background_context}" if background_context else ""

        input_str = f"""
        ORIGINAL QUERY:
        {query}

        KNOWLEDGE GAP TO ADDRESS:
        {gap}

        {background}

        HISTORY OF ACTIONS, FINDINGS AND THOUGHTS:
        {self.conversation.compile_conversation_history() or "No previous actions, findings or thoughts available."}
        """
        
        result = await ResearchRunner.run(
            self.tool_selector_agent,
            input_str,
        )
        
        selection_plan = result.final_output_as(AgentSelectionPlan)

        # Add the tool calls to the conversation
        self.conversation.set_latest_tool_calls([
            f"[Agent] {task.agent} [Query] {task.query} [Entity] {task.entity_website if task.entity_website else 'null'}" for task in selection_plan.tasks
        ])
        self._log_message(self.conversation.latest_action_string())
        
        return selection_plan
    
    async def _execute_tools(self, tasks: List[AgentTask]) -> Dict[str, ToolAgentOutput]:
        """Execute the selected tools concurrently to gather information."""
        with custom_span("Execute Tool Agents"):
            # Create a task for each agent
            async_tasks = []
            for task in tasks:
                async_tasks.append(self._run_agent_task(task))
            
            # Run all tasks concurrently
            num_completed = 0
            results = {}
            for future in asyncio.as_completed(async_tasks):
                gap, agent_name, result = await future
                results[f"{agent_name}_{gap}"] = result
                num_completed += 1
                self._log_message(f"<processing>\nTool execution progress: {num_completed}/{len(async_tasks)}\n</processing>")

            # Add findings from the tool outputs to the conversation
            findings = []
            for tool_output in results.values():
                findings.append(tool_output.output)
            self.conversation.set_latest_findings(findings)

            return results
    
    async def _run_agent_task(self, task: AgentTask) -> tuple[str, str, ToolAgentOutput]:
        """Run a single agent task and return the result."""
        try:
            agent_name = task.agent
            agent = self.tool_agents.get(agent_name)
            if agent:
                result = await ResearchRunner.run(
                    agent,
                    task.model_dump_json(),
                )
                # Extract ToolAgentOutput from RunResult
                output = result.final_output_as(ToolAgentOutput)
            else:
                output = ToolAgentOutput(
                    output=f"No implementation found for agent {agent_name}",
                    sources=[]
                )
            
            return task.gap, agent_name, output
        except Exception as e:
            error_output = ToolAgentOutput(
                output=f"Error executing {task.agent} for gap '{task.gap}': {str(e)}",
                sources=[]
            )
            return task.gap, task.agent, error_output
        
    async def _generate_observations(self, query: str, background_context: str = "") -> str:
        """Generate observations from the current state of the research."""
        
        background = f"BACKGROUND CONTEXT:\n{background_context}" if background_context else ""

        input_str = f"""
        You are starting iteration {self.iteration} of your research process.

        ORIGINAL QUERY:
        {query}

        {background}

        HISTORY OF ACTIONS, FINDINGS AND THOUGHTS:
        {self.conversation.compile_conversation_history() or "No previous actions, findings or thoughts available."}
        """
        result = await ResearchRunner.run(
            self.thinking_agent,
            input_str,
        )

        # Add the observations to the conversation
        observations = result.final_output
        self.conversation.set_latest_thought(observations)
        self._log_message(self.conversation.latest_thought_string())
        return observations
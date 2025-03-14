import asyncio
from typing import Any, Callable, List, TypeVar, Dict, Awaitable

T = TypeVar("T")
InputType = TypeVar("InputType")
ResultType = TypeVar("ResultType")


async def run_tasks_in_parallel(
    process_function: Callable[[InputType], Awaitable[ResultType]],
    inputs: List[InputType],
    show_progress: bool = True,
    result_handler: Callable[[InputType, ResultType], None] = None,
) -> List[ResultType]:
    """
    Run multiple tasks in parallel using asyncio.

    Args:
        process_function: The async function to run for each input
        inputs: List of input items to process
        show_progress: Whether to show progress messages
        result_handler: Optional callback to handle each result as it completes

    Returns:
        List of results from all processed inputs
    """
    if show_progress:
        print(f"Processing {len(inputs)} items in parallel...\n")

    # Create tasks for each input
    tasks = [process_function(input_item) for input_item in inputs]

    # Process all tasks in parallel
    results = await asyncio.gather(*tasks)

    # Handle results if a handler is provided
    if result_handler:
        for input_item, result in zip(inputs, results):
            result_handler(input_item, result)

    return results


async def run_dict_tasks_in_parallel(
    process_function: Callable[[Dict[str, Any]], Awaitable[ResultType]],
    input_dicts: List[Dict[str, Any]],
    show_progress: bool = True,
    result_handler: Callable[[Dict[str, Any], ResultType], None] = None,
) -> List[ResultType]:
    """
    Run multiple tasks with dictionary inputs in parallel using asyncio.

    Args:
        process_function: The async function to run for each input dictionary
        input_dicts: List of input dictionaries to process
        show_progress: Whether to show progress messages
        result_handler: Optional callback to handle each result as it completes

    Returns:
        List of results from all processed inputs
    """
    return await run_tasks_in_parallel(
        process_function=process_function,
        inputs=input_dicts,
        show_progress=show_progress,
        result_handler=result_handler,
    )

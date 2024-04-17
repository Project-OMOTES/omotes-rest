from omotes_sdk.workflow_type import WorkflowTypeManager, WorkflowType

# TODO to be retrieved via de omotes_sdk in the future
WORKFLOW_TYPE_MANAGER = WorkflowTypeManager(
    possible_workflows=[
        WorkflowType(
            workflow_type_name="grow_optimizer_default",
            workflow_type_description_name="Grow Optimizer"
        ),
        WorkflowType(
            workflow_type_name="grow_simulator",
            workflow_type_description_name="Grow Simulator"
        ),
        WorkflowType(
            workflow_type_name="grow_optimizer_no_heat_losses",
            workflow_type_description_name="Grow Optimizer without heat losses",
        ),
        WorkflowType(
            workflow_type_name="grow_optimizer_with_pressure",
            workflow_type_description_name="Grow Optimizer with pressure drops",
        ),
        WorkflowType(
            workflow_type_name="simulator",
            workflow_type_description_name="High fidelity simulator",
        ),
    ]
)

FRONTEND_NAME_TO_OMOTES_WORKFLOW_NAME = {
    'Draft Design - Quickscan Validation': 'grow_optimizer_no_heat_losses',
    'Draft Design - Optimization': 'grow_optimizer_default',
    'Draft Design - Optimization with Pressure Drops': 'grow_optimizer_with_pressure',
    'Draft Design - Simulation with Source Merit Order': 'grow_simulator',
    'Conceptual Design - Simulation': 'simulator',
}

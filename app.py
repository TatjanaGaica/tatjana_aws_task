import os

import aws_cdk as core

from tatjana_aws_task.sagemaker_ai_studio_stack import SageMakerAIStudioStack

app = core.App()

SageMakerAIStudioStack(
    app, "SageMakerAIStudioInfrastructureStack",
    env=core.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=os.getenv('CDK_DEFAULT_REGION')
    ),
    description="CDK stack for SageMaker AI Studio foundational infrastructure."
)

app.synth()

import aws_cdk as core
import aws_cdk.assertions as assertions

from my_appsync_cdk.my_appsync_cdk_stack import MyAppsyncCdkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in my_appsync_cdk/my_appsync_cdk_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = MyAppsyncCdkStack(app, "my-appsync-cdk")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })

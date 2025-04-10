from constructs import Construct
from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_iam as iam,
    RemovalPolicy,
    CfnOutput,
    Duration,
    Expiration,
)
import aws_cdk.aws_appsync_alpha as appsync

import os
DD_API_KEY = os.environ.get("DD_API_KEY")

class MyAppSyncCdkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB table
        table = dynamodb.Table(
            self, "ItemsTable",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,  # For demo purposes only, use RETAIN for production
        )

        # AppSync API
        api = appsync.GraphqlApi(
            self, "ItemsApi",
            name="items-api",
            schema=appsync.SchemaFile.from_asset("schema/schema.graphql"),
            authorization_config=appsync.AuthorizationConfig(
                default_authorization=appsync.AuthorizationMode(
                    authorization_type=appsync.AuthorizationType.API_KEY,
                    api_key_config=appsync.ApiKeyConfig(
                        expires= Expiration.after(Duration.days(365))
                    )
                )
            ),
            xray_enabled=False,
        )

        # Common Lambda layer for shared code or dependencies
        lambda_layer = lambda_.LayerVersion(
            self, "LambdaLayer",
            code=lambda_.Code.from_asset("lambda/layers/common"),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
            description="Common libraries for Lambda functions",
        )

        # IAM role for Lambda functions
        lambda_role = iam.Role(
            self, "LambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )

        # Add DynamoDB permissions to Lambda role
        table.grant_read_write_data(lambda_role)

        # Create Lambda functions for resolvers
        get_items_lambda = lambda_.Function(
            self, "GetItemsFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("lambda/get_items"),
            handler="index.handler",
            environment={
                "TABLE_NAME": table.table_name
            },
            timeout=Duration.seconds(30),
            role=lambda_role,
            layers=[lambda_layer],
        )

        get_item_by_id_lambda = lambda_.Function(
            self, "GetItemByIdFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("lambda/get_item_by_id"),
            handler="index.handler",
            environment={
                "TABLE_NAME": table.table_name
            },
            timeout=Duration.seconds(30),
            role=lambda_role,
            layers=[lambda_layer],
        )

        create_item_lambda = lambda_.Function(
            self, "CreateItemFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("lambda/create_item"),
            handler="index.handler",
            environment={
                "TABLE_NAME": table.table_name
            },
            timeout=Duration.seconds(30),
            role=lambda_role,
            layers=[lambda_layer],
        )

        update_item_lambda = lambda_.Function(
            self, "UpdateItemFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("lambda/update_item"),
            handler="index.handler",
            environment={
                "TABLE_NAME": table.table_name
            },
            timeout=Duration.seconds(30),
            role=lambda_role,
            layers=[lambda_layer],
        )

        delete_item_lambda = lambda_.Function(
            self, "DeleteItemFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("lambda/delete_item"),
            handler="index.handler",
            environment={
                "TABLE_NAME": table.table_name
            },
            timeout=Duration.seconds(30),
            role=lambda_role,
            layers=[lambda_layer],
        )

        # Set up data sources
        items_ds = api.add_lambda_data_source("ItemsDataSource", get_items_lambda)
        item_by_id_ds = api.add_lambda_data_source("ItemByIdDataSource", get_item_by_id_lambda)
        create_item_ds = api.add_lambda_data_source("CreateItemDataSource", create_item_lambda)
        update_item_ds = api.add_lambda_data_source("UpdateItemDataSource", update_item_lambda)
        delete_item_ds = api.add_lambda_data_source("DeleteItemDataSource", delete_item_lambda)

        # Set up resolvers
        items_ds.create_resolver(
            id="GetItemsResolver",
            type_name="Query",
            field_name="getItems"
        )

        item_by_id_ds.create_resolver(
            id="GetItemByIdResolver",
            type_name="Query",
            field_name="getItemById"
        )

        create_item_ds.create_resolver(
            id="CreateItemResolver",
            type_name="Mutation",
            field_name="createItem"
        )

        update_item_ds.create_resolver(
            id="UpdateItemResolver",
            type_name="Mutation",
            field_name="updateItem"
        )

        delete_item_ds.create_resolver(
            id="DeleteItemResolver",
            type_name="Mutation",
            field_name="deleteItem"
        )

        # Add the requests layer
        requests_layer = lambda_.LayerVersion(
            self, "RequestsLayer",
            code=lambda_.Code.from_asset("lambda/layers/requests_layer"),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
            description="Layer containing the requests package"
        )
        # Create a client Lambda function to interact with the GraphQL API
        graphql_client_lambda = lambda_.Function(
            self, "GraphQLClientFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("lambda/graphql_client"),
            handler="index.handler",
            environment={
                "GRAPHQL_API_URL": api.graphql_url,
                "GRAPHQL_API_KEY": api.api_key
            },
            timeout=Duration.seconds(30),
            layers=[requests_layer]
        )

        # Use datadog tool to automatically instrument all the lambdas.
        # Documentation link: https://docs.datadoghq.com/serverless/aws_lambda/installation/python/?tab=awscdk
        from datadog_cdk_constructs_v2 import DatadogLambda

        datadog_lambda = DatadogLambda(self, "DatadogLambda",
            python_layer_version=107,  # You can get the latest version number from https://github.com/DataDog/serverless-plugin-datadog/blob/main/src/layers.json
            extension_layer_version=75, # You can get the latest version number from https://github.com/DataDog/serverless-plugin-datadog/blob/main/src/layers.json
            site="datadoghq.com",
            api_key=DD_API_KEY,
            service="appsync-demo"
        )

        graphql_lambdas = [ create_item_lambda,
                            get_items_lambda,
                            get_item_by_id_lambda,
                            update_item_lambda,
                            delete_item_lambda]

        for l in graphql_lambdas:
            l.add_environment("DD_COLD_START_TRACING", 'False')
            l.add_environment("DD_CAPTURE_LAMBDA_PAYLOAD", 'True')
            l.add_environment("DD_TRACE_EXTRACTOR", 'custom_extractor.nested_json_extractor')

        datadog_lambda.add_lambda_functions([graphql_client_lambda] + graphql_lambdas)
# Outputs
        graphql_client_lambda.add_environment("DD_COLD_START_TRACING", 'False')

        CfnOutput(
            self, "GraphQLAPIURL",
            value=api.graphql_url,
            description="URL of the GraphQL API"
        )

        CfnOutput(
            self, "GraphQLAPIKey",
            value=api.api_key,
            description="API Key for the GraphQL API"
        )

#!/usr/bin/env python3
import aws_cdk as cdk
import os

from mycdk.mycdk_stack import MycdkStack

env_EU = cdk.Environment(account=os.environ.get("account"), region=os.environ.get("region"))

app = cdk.App()
MycdkStack(app, "MycdkStack", env=env_EU
    )

app.synth()

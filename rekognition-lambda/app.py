#!/usr/bin/env python3
import aws_cdk as cdk

from mycdk.mycdk_stack import MycdkStack


app = cdk.App()
MycdkStack(app, "MycdkStack",
    )

app.synth()

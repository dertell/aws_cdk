#!/usr/bin/env python3
import os

import aws_cdk as cdk

from hello_cdk.hello_cdk_stack import HelloCdkStack, ByeCdkStack


app = cdk.App()

HelloCdkStack(app, "HelloCdkStack",)

ByeCdkStack(app, "ByeCdkStack")

app.synth()

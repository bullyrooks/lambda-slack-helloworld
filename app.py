import aws_cdk as cdk

from slack_helloworld.slack_helloworld_stack import SlackHelloworldStack

app = cdk.App()
SlackHelloworldStack(app, "SlackHelloworldStack", )
app.synth()

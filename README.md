<table>
<tbody>
<tr>
<td><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Slack_Technologies_Logo.svg/2000px-Slack_Technologies_Logo.svg.png" width="256" height="73" /></td>
<td><span style="font-size: 36pt;">&nbsp;+&nbsp;</span></td>
<td><img src="https://s3.amazonaws.com/com.twilio.prod.twilio-docs/images/twitter-python-logos.width-808.jpg" width="204" height="102" /></td>
</tr>
</tbody>
</table>

# SlackTweet: A Team Project in Python 3

This project explores building a Slackbot using Python 3.  Of course there are many third-party platforms out there that can automate the process of creating AI-driven bots. But as emerging software engineers, we understand that by diving deep and exploring the nuts and bolts, we acquire a rich knowledge of how things work which will serve us well in the future, as well as honing our skill set of software best practices.  This is a longer-duration assignment-- you will be researching, planning, and experimenting and task-switching between other activities.  Be sure to allocate sufficient time!

This assignment integrates many concepts that you have learned over the last few weeks.  The goal is to create a slackbot framework that you can take with you to extend, adapt, and reuse in many ways.  You will be connecting your Slackbot to your own personal twitter account, and controlling it with a set of commands.

Yes, there already exists an off-the-shelf [twitter integration](https://slack.com/help/articles/205346227) that you can enable within a Slack workspace.  However, this app is limited in its functionality.  You can only post tweets and retweets from a single account.  No hashtag support.

## Learning Objectives
 - Become comfortable with self-guided API research and experimentation
 - Create, test, deploy, manage a long running program in a cloud environment 
 - Apply best practices in repository structure and virtual environment management
 - Familiarize with OAuth authentication process
 - Learn how to create an integration between two real-world APIs
 - Use multi-threading to create a responsive application

## Goal
The goal is to create a _controllable_, long-running Slackbot that subscribes to various Twitter streams, and republishes those tweets into a channel (or channels) on Slack.  You don't need to send messages from Slack to Twitter - just a Twitter listener.  The Bot will be deployed on your existing Heroku cloud-hosting account.

## Setup - Slack Account
You will need to set up your slack app. First you must be signed into a slack workspace, then go [here](https://api.slack.com/apps) fill out your App's name and select a workspace for your bot to work in

Under Add features and functionality select Bots, then hit add a bot user. Go back to basic settings and install the app to your workspace.

On the left side go to install App under settings grab the Bot User OAuth Access Token and store it in a .env file



## Setup - Twitter Account
You will need to set up a twitter account.  You can use your own existing account, or create a new one.  The important part is to register for _developer API access_.  This is a new requirement since July 2018.  You will need to fill out a short questionnaire about your intended usage of the developer account. Your answers should reflect that you are a student who is learning the Twitter API and you do not intend to post any tweets of any kind.

 - https://developer.twitter.com/en.html
 - <img src="img/twitter_quiz.png" height="360px">

Once you have been approved for developer access, Follow the Twitter documentation on creating an app.  Then use the `Keys and Tokens` tab to generate a pair of Consumer keys, and a pair of Access keys.

<img src="img/Twitter_app.png" width="471" height="211" />

You will use the Consumer and Access keys to communicate with your Twitter account via the API. Add them to your .env file

## Add Slack bot commands

First add a new command and help string to the command list in slacktweet.py:

```python
commands = {
    "help": "Prints a helpful message",
    "ping": "Show uptime of this bot",
    "exit": "Shutdown this bot",
    ...
    "new_command": "new_command help string"
}
```

Then handle the command into the slackbot_callback method:

```python
def slackbot_callback(client, command, data, channel, web_client, *args):
    """Callback method to handle commands emitted by the slackbot client""" 
    if command == 'ping':
        """returns the uptime of the bot"""
        uptime = dt.now() - client.start_time

        client.send_message(
            channel=channel,
            text=f"The bot has been active for: {uptime}"
        )
    ...
    if command == 'new_command':
        """Handles new_command"""
        pass
```


## Deployment Details

  You will need to copy your API tokens directly into Heroku config vars:

```
heroku config:set BOT_USER_TOKEN="xoxb-431941958864-124971466353-2Ysn7vyHOUkzjcABC76Tafrq"
heroku config:set OTHER_TOKEN="other-value"
```
Now everything should be ready to run.  Start up your slacktweet app and check the logs.  Find out more about viewing heroku logs [here](https://devcenter.heroku.com/articles/logging)

```
heroku ps:scale worker=1
heroku logs --tail
``` 
# Save Olegator Bot

> I wrote the project in a couple of hours without putting much thought in the code, please don't judge

My friend Oleg was forced to move from his hometown because of war.
While on the road, he had painfully slow internet connection.
That's why I came up with an idea to make a telegram bot that compresses videos
to make them accessible to people with bad internet connection.

## Service file

`save-olegator-bot.service` contains an example `systemctl` service file.
Place your own value in the `ExecStart` directive.
Usually I write some kind of `sh` script for running the service.

## How to run

Create folders: `logs/`, `media/` and install packages from `requirements.txt`.

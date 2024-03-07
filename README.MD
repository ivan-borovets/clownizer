# Clownizer

Telegram UserBot to support your friends and irritate your enemies with emoji reactions.

## Current features:

1. Immediately responds to the target's messages with emoji reactions, considering your friendship or enmity.
2. Includes up to 3 random emojis to one response from a specified custom emoticons list, taking into account your
   Telegram
   Premium status.
3. Periodically replaces the previously set emoji reactions with new random ones (in order to remind about yourself).
4. Logs its operations to the console and a file in the `logs` folder (it will be created in the root folder after
   the 1st successful launch).

## Current issues:

1. Apparently, the automatic emoji update does not work in all chats.

## Installation (temporarily rough description):

1. **Clone** this repo.

```sh
git clone https://github.com/ivan-borovets/clownizer.git
```

2. **Set up** venv (use `requirements.txt`). My Python interpreter version is `3.11.7`.
3. **Create** `.env` file in the root folder, and fill it in with the data
   obtained [here](https://core.telegram.org/api/obtaining_api_id).

Example of `.env` content:

```
API_ID = 123456
API_HASH = "12345a678b9c0d12ef123g45ef678g90"
```

4. **Edit** `src/settings.py` for your needs:

- Change `MSG_QUEUE_SIZE` `(DEFAULT=10)` to track more messages for emoji updates.
- Change `UPDATE_TIMEOUT` `(DEFAULT=3)` to set the timeout between updates `in seconds` between emoji updating actions.
- Change `UPDATE_JITTER` `(DEFAULT=2)` to set the maximum delay after `UPDATE_TIMEOUT` `in seconds` for timer
  variability.
- Change the `TARGETS` dictionary `DEFAULT format is provided in src/settings.py` to set your target list.
- Change `EMOTICONS_FOR_ENEMIES` and `EMOTICONS_FOR_FRIENDS` emoji list `DEFAULT format is provided in src/settings.py` to set
  the
  emoji lists.

5. **Activate** venv.
6. **Run** `main.py` (and perform the necessary actions in the dialogue with Telegram **once** for the first launch).
7. **Enjoy**! If necessary, **stop** the execution **manually**.

## Error messages that may occur:

1. `AttributeError: The API key is required for new authorizations`: `.env` file needs to be checked.
2. `SettingsException`: `src/settings.py` needs to be checked. Follow the steps in the instructions above.
3. `ReactionInvalid`: at least one of the emoticons specified in the `src/settings.py` cannot be used to generate a correct
   emoji response.
4. `MessageNotModified`: a message was not modified with emojis due to Telegram peculiarities.
5. `FloodWait`: Due to frequent or repeated requests, Telegram has temporarily limited their sending. Consider
   increasing the `UPDATE_TIMEOUT` in the `src/settings.py`.

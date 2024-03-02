# Clownizer

Telegram UserBot to support your friends and irritate your enemies by emoji reactions.

## Current features:

1. Immediately responds to the target's messages with emoji reactions, taking into account your friendship or enmity.
2. Includes up to 3 random emoticons to one response from a specified custom list, taking into account your Telegram
   Premium status.
3. Periodically replaces the previously set emoji reactions with new random ones (in order to remind about yourself).

## Installation (temporarily rough description):

1. **Clone** this repo.

```sh
   git clone https://github.com/ivan-borovets/clownizer.git
```

2. **Set up** venv (use `requirements.txt`).
3. **Create** `.env` file, fill it in with the data obtained [here](https://core.telegram.org/api/obtaining_api_id).

Example of `.env` content:

```
api_id = 123456
api_hash = "12345a678b9c0d12ef123g45ef678g90"
```

4. **Edit** `const.py` for your needs:

- Change `MESSAGE_MEMORY_SIZE` `(DEFAULT=10)` to track more messages for emoji updates.
- Change `REFRESH_SLEEP_TIME` `(DEFAULT=(5, 10))` to set the timeout `(FROM, TO)` `in seconds` between emoji updating
  actions.
- Change `TARGETS` dictionary `DEFAULT format is provided in const.py` to set your target list.
- Change `RESPONSE_TO_ENEMY` and `RESPONSE_TO_ENEMY` emoji list `DEFAULT format is provided in const.py` to set the
  emoji list.

5. **Activate** venv.
6. **Run** `main.py` (and perform the necessary actions in the dialogue with Telegram **once** for the first launch).
7. **Enjoy**! If necessary, **stop** the execution **manually**.
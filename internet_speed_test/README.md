# Internet Speed Test Monitor

Utility to monitor internet speed on a Mac. Every 5 minutes it runs a speed test, appends the result to `/tmp/speedtest.log`, and refreshes the graph at `~/Desktop/sptest.png`.

## Requirements

The official Ookla `speedtest` CLI must be installed:

```bash
brew tap teamookla/speedtest
brew install speedtest
```

Python dependencies: `matplotlib`, `numpy`, `pandas`.

> The legacy `sivel/speedtest-cli` Python script (the original `speedtest.py` in this directory) is no longer used — Speedtest.net now blocks it with HTTP 403. The script was switched to the official Ookla CLI.

## Files

- `speedtest_log.py` — the only file you need. Runs a speed test, logs the result, and regenerates the graph.

## Output files

- `/tmp/speedtest.log` — rolling log of timestamped results (last ~2,000 rows kept)
- `/tmp/speedtest.err` — stderr from cron runs (last ~2,000 rows kept)
- `~/Desktop/sptest.png` — graph of the last 5 days and last 2 hours

## Setup

Add this entry to the crontab (`crontab -e`):

```cron
# run internet speed test every 5 min
*/5 * * * * bash -c 'cd ~/; source .bashrc; cd ~/Documents/GitHub/setup_computer/internet_speed_test; python speedtest_log.py >> /tmp/speedtest.err 2>&1'
```

The `source .bashrc` step is what puts `/opt/homebrew/bin` (where `speedtest` lives) on cron's PATH.

## References

- Ookla Speedtest CLI: <https://www.speedtest.net/apps/cli>
- Original blog post (legacy approach):
  <https://www.accelebrate.com/blog/pandas-bandwidth-python-tutorial-plotting-results-internet-speed-tests/>

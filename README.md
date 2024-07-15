Usage

```bash
python dw_new_music.py [-h] [--younger-than YOUNGER_THAN] [--after AFTER] [--replace]
```
Options

    -h, --help: Show help message and exit.
    --younger-than YOUNGER_THAN: Specify the number of days to consider as a threshold for newer releases.
    --after AFTER: Specify the date in D/M/Y format to filter releases released after this date.
    --replace: Download even if the content was previously downloaded (overwrite existing downloads).

Configuration

    artists.txt: Create a text file named artists.txt in the same directory as dw_new_music.py. List one artist name per line.

    .dw file: The script maintains a .dw file in the current directory to log downloaded releases. This prevents re-downloading unless the --replace option is used.

Example

```bash
python dw_new_music.py --younger-than 30 --after 1/7/2024
```
This command will download music released by artists listed in artists.txt, within the last 30 days and after 1st July 2024. It will log downloads in .dw file to avoid re-downloading unless --replace is specified.
Notes

    Ensure spotdl is correctly installed and configured with your Spotify credentials for proper functionality.
    Modify artists.txt and adjust command-line options (--younger-than, --after, etc.) as per your specific requirements.

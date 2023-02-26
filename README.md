<h1 align='center'>Pit Mopper</h1>

<div align='center'>
  <a href=https://github.com/username121546434/pit-mopper/releases/latest>
    <img src='https://img.shields.io/github/v/release/username121546434/pit-mopper?include_prereleases&label=Latest%20Release'/>
  </a>
  <a href = 'https://github.com/username121546434/pit-mopper/pulls'>
    <img src = 'https://img.shields.io/github/issues-pr/username121546434/pit-mopper?label=Pull%20Requests'/>
  </a>
  <a href = 'https://github.com/username121546434/pit-mopper/issues'>
    <img src = 'https://img.shields.io/github/issues/username121546434/pit-mopper?label=Issues'/>
  </a>
</div>

Pit Mopper is a game based on "Minesweeper" that was built in python.

This was a game that I made for fun to learn more about programming.

Feel free to contribute if you want to!

## How to run

Note: You will need Python version 3.10 or above to run it

### Run on Windows

Step 1: Clone this repository using the following command

```text
git clone https://github.com/username121546434/pit-mopper.git
```

Step 2: Cd into the directory (if you aren't already there)

```text
cd ./pit-mopper
```

Step 3: Install all required modules

```text
pip install -r requirements.txt
```

Step 4: Run the main Python file

```text
py "Pit Mopper.py"
```

### Run on Linux

Note: This has only been tested on Linux Ubuntu distro, I have not tested it for any other distros

To install python 3.10, you can use this [article](https://computingforgeeks.com/how-to-install-python-on-ubuntu-linux-system/)

Step 1: Clone this repository using the following command

```text
git clone https://github.com/username121546434/pit-mopper.git
```

Step 2: Cd into the directory (if you aren't already there)

```text
cd ./pit-mopper
```

Step 3: Install all required modules

```text
python3.10 -m pip install -r requirements.txt
```

Step 4: Run the main Python file

```text
python3.10 "Pit Mopper.py"
```

## Version 2.0.2

**Note**: This is a minor bugfix update, so don't expect that many changes

### Bug Fixes
 - Fixed bug where the updater would fail to get patch notes
 - Fixed an error where the updater will crash the whole game on Ubuntu

### Other Changes
 - Made various changes to the updater, including making it work with dark mode
 - Made a slight change to dark mode during a game, the squares with numbers (other than 0) will not be darker than the ones in light mode to improve readability

**GitHub Changelog**: https://github.com/username121546434/pit-mopper/compare/v2.0.1...v2.0.2

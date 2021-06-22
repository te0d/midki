# Midki

A tool for learning typing in Chinese.

Midki, a portmanteau of Middle Kingdom, is a tool to help the user practice typing Chinese words. The quiz progresses
through words based on their HSK level and their frequency of appearance. A user's recent performance for a word weights
its chance of appearance, casuing troublesome words to appear more frequently. Users who are not logged are able to quiz
words by level. Words can be simplified or traditional. Meaning can also be quizzed, although meanings have little meaning
without appropriate context.

## Install

I create and activate a python3 virtual environment using venv:

```
python3 -m venv venv
. venv/bin/activate
```

To install dependencies of the application:

```
pip install -e .
```

A sqlite3 database is used to store word and user information. It is initialized by:

```
FLASK="middle_kingdom" flask init-db
```

For production, see https://flask.palletsprojects.com/en/2.0.x/quickstart/#sessions to set up a secret key to sign the cookie.

## Usage

To start the server:

```
FLASK="middle_kingdom" flask run
```

## Contributing

PRs accepted.

## License

MPL-2.0 © Tom O'Donnell

In the data/ folder, there is data from other repositories under their own licenses:

https://github.com/KyleBing/rime-wubi86-jidian
APACHE
This repository is used for character wubi input keys.

https://github.com/glxxyz/hskhsk.com
MIT
This repository is used for the hsk words and their relative frequencies of appearance.

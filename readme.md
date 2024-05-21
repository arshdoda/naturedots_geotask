# NatureDots Geotask

## Setup

The first thing to do is to clone the repository:

```shell
git clone https://github.com/arshdoda/naturedots_geotask.git
cd naturedots_geotask
```

Create a virtual environment to install dependencies in and activate it:

```shell
python3 -m venv .venv
source .venv/bin/activate
```

Then install the dependencies:

```shell
pip install -r requirements.txt
```

Note the `(env)` in front of the prompt. This indicates that this terminal session operates in a virtual environment set up by `virtualenv2`.

Once `pip` has finished downloading the dependencies, you can run the script using following command:

```shell
python3 script.py -i "input/lake.geojson" -sd 2003-01-01 -ed 2014-01-01 -o img.png
```

You can also check the help with the following command:

```
python3 script.py -h
```

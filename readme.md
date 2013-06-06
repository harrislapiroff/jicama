Jicama
------

Jicama is a Turntable robot built using Alain Gilbert's [Turntable-API][ttapi].

[ttapi]: https://github.com/alaingilbert/Turntable-API/tree/python_ttapi

Installation & Usage
====================

You will need to install the python packages listed in `requirements.txt` to run Jicama. I encourage you to use [pip][] and [virtualenv][] (and [virtualenvwrapper][]). If you're on a Mac this should get you started:

```bash
sudo easy_install pip # install pip
sudo pip install virtualenv virtualenvwrapper # install virtualenv
source ~/.profile # hopefully this works
mkvirtualenv jicama # create a new virtualenv
cd /PATH/TO/jicama/ # CHANGE THIS TO THE PATH TO JICAMA
pip install -r requirements.txt # install requirements to this environment
```

Now, be sure to create a new `settings/settings.py` file based on `settings/sample_settings.py`.

Now, every time you want to run Jicama, use the following commands:

```bash
workon jicama # activate the virtualenv
python jicama.py # run jicama
````

To stop Jicama, type Ctrl-C. You will need to restart Jicama between code changes.
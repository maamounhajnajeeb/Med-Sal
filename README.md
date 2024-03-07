## Med Sal Project
Django web app that enclose the relationship between patients and medical services providers.

## Motivation
Imagine that you need to buy a medicine but you're so ill, so you can't go out your room to buy it.
Do you remember a situation when you have to take an appointment with a doctor, but the medical clinic is far far away from your house.
Med Sal Project will do all of this, with Med Sal you can:
- Order medical products from pharmacies
- Reserve an appointments with Doctors
- Check your appointments status
- (And/use) or (Use) delivery service to deliver your ordered products.

## Cloning this project
Initially, you need python 3.10 or higher installed on your local machine, then:
- Open a folder and build virtual environment within it via these commands:
1. `virtualenv .venv`
2. `.venv\scripts\activate` for windows</br>
(if you user mac or linux, do this instead:
```console
source .venv/bin/activate
```
)
- Next, clone the repo:</br>
`git clone https://github.com/maamounhajnajeeb/Med-Sal.git`
- Now it's dependencies' time:</br>
`pip install -r requirements.txt`</br>
here  you have to wait for some time until the dependencies installed suucessfully</br>
actually the dependencies aren't that much (you can check them form **requirements.txt** file)
- Write the desired environment variables. Actually, you need to add: SECRET_KEY, ALLOWED_HOSTS, Database and Email Configuaration
- After that, write Django magic commands:</br>
`python manage.py migrate`</br>
`python manage.py runserver`</br>
**Note**: there's gunicorn dependecy in the requirements, but it's for production not development.

#!/bin/sh
RUST_BACKTRACE=1 FLASK_APP=vdex_web2.py FLASK_ENV=development flask run

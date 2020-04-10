#! /bin/bash
rm ./index.html favicon.ico
rm -rf static/*
cp ../awserv/dist/index.html ./
cp ../awserv/dist/favicon.ico ./
cp -r ../awserv/dist/static/* ./static/

#!/bin/bash
kill `ps -aux | grep -m 1 klimrsg | awk '{print $2}'`

#!/bin/bash

date
docker run --network nyt_reseau nyt_maj
docker run --network nyt_reseau nyt_train_ml

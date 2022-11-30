# CPHO server

This is a Django based API running GraphQL.

## Managing dependencies

Dependencies are managed with [PDM](https://pdm.fming.dev/latest/). Mostly this will boil down to adding deps with `pdm add newdep`.
For compatibilitiy with the current docker-compose setup, after adding a new dependency you should regenerate the requirements.txt file with the following command:
```sh
pdm export --production --without-hashes -o requirements.txt
```

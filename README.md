# Cloaked AI + Marqo

```
docker compose up
pmd run cloaked-marqo.py
```

## Current State

Still trying to get Marqo's getting started example running. The DIND expected setup in the getting started doesn't seem to work with NixOS rootless docker. I created a `docker-compose.yaml` based on their [M1 Mac](https://docs.marqo.ai/1.5.0/Guides/m1_mac_users/) workaround where DIND also doesn't work. That doesn't work yet, there's an SSL issue with the `marqo-os` container, it fails its healthcheck so the `marqo` container never tries to start.


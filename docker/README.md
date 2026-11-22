# ZEPHYRUM infrastructure image

One image, four modes: the ZYQL API, the QPU witness, the Zephyrum OS under
QEMU, and a smoke test. Built in CI and published to GHCR so it runs anywhere.

## Modes
- `api` - FastAPI server for ZYQL (port 8000)
- `witness` - Bell Phi+ witness on IBM Quantum; seals a receipt binding the
  exact verdict hash to the hardware job id
- `boot` - boots the Zephyrum OS disk image under QEMU (headless, serial)
- `test` - verifies the runtime inside the image

## Local use
```
cp .env.example .env        # IBM_QUANTUM_TOKEN, IBM_QUANTUM_CRN
docker build -f docker/Dockerfile.infra -t zephyrum-infra .
docker run --rm zephyrum-infra test
docker compose -f docker/docker-compose.yml --profile witness run --rm zyql-witness
```

## Rules baked into the package
1. Token and CRN never enter the image; they come from the environment.
2. The exact verdict is produced offline; hardware is witness only.
3. Every witness run writes a receipt with verdict hash and job id.

## Codespaces
Open the repository in a Codespace: `.devcontainer/devcontainer.json` brings
Docker up and builds this image on create.

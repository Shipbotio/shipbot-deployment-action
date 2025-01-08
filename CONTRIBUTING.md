```bash
brew install act

cp act.secrets.sample act.secrets

#
act --secret-file act.secrets

# If on M series Mac:
act --secret-file act.secrets --container-architecture linux/amd64
```
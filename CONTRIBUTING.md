```bash
brew install act

cp act.secrets.sample act.secrets

# Run action locally
act --secret-file act.secrets

# Specify a job
act --secret-file act.secrets -j test_basic

# Run action locally with multiple steps
act --secret-file act.secrets -j test_deployment_multiple_steps
```

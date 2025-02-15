# Shipbot.io Deployment Action

This Github action makes it easy to track deployments from your Github actions.

# Artifact Configuration

Within your artifact directory you can create a `shipbot.json` file to configure the artifact and retain it's ID.

```json
{
  "artifactId": 7
}
```

This should then be passed to the action using the `artifactConfig` parameter.

## Inputs

| Parameter     | Required | Description |
| ------------ | -------- | ----------- |
| `apiKey`     | ✅       | Shipbot API key (found in Settings). |
| `artifactConfig`| ✅      | Path to service configuration JSON file containing artifactId |
| `version`    | ✅       | The version can be any string. |
| `environment`| ✅       | This should match the environment created in Current Version. By default `PRODUCTION` is created. |
| `commitSha`  | ✅       | Commit SHA reference. |
| `user`       | ✅       | The user initiating the deployment. Will be linked to Slack users within Shipbot.io once the user has logged into Shipbot.io and connected with Github. |
| `branch`     | ✅       | The branch that is being deployed. |
| `status`     | ❌       | One of `STARTED`, `SUCCEEDED`, `FAILED`. |
| `changelog`  | ❌       | This can be a URL to a change log or the changelog notes itself. |
| `description`| ❌       | This can be further information on the deployment that wouldn't be considered part of the changelog. |
| `link`       | ❌       | This should link to an external place where more action on the deployment can take place for example it could be the deployment job in your CI/CD pipeline. |
| `type`       | ❌       | This is a enum describing the deployment strategy. The only option right now is SIMPLE. |
| `logLevel`   | ❌       | Log level (DEBUG, INFO, WARNING, ERROR). |

## Example usage

### GitHub secrets

[Github secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets#about-encrypted-secrets) assumed to be set:
* `SHIPBOT_API_KEY` - Shipbot.io API key found in [Settings](https://app.shipbot.io/settings).

The examples below use a number of [default GitHub environment variables](https://docs.github.com/en/actions/learn-github-actions/variables#default-environment-variables) which greatly enhance the quality of notifications and experience within Shipbot.io

### Recommended Implementation

From the below add the two jobs to your relevant Github workflow file.

```yaml
name: Deploy Lambda Functions

# Trigger the workflow on changes to the 'functions/' directory
on:
  push:
    branches:
      - main

# Define jobs
jobs:
  deploy-code:
    name: Deploy Code
    runs-on: ubuntu-latest

    steps:
      # Checkout the repository
      - name: Checkout Code
        uses: actions/checkout@v3

      # Log deployment
      - name: Log Deployment
        uses: Shipbotio/shipbot-deployment-action@v2.0.1
        with:
          apiKey: ${{ secrets.SHIPBOT_API_KEY }}
          artifactConfig: shipbot.json
          environment: "PRODUCTION"
          version: ${{ github.sha }}
          commitSha: ${{ github.sha }}
          branch: ${{ github.ref_name }}
          link: https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }}
          user: ${{ github.actor }}
          status: "STARTED"

      # Deploy Lambda function
      - name: Deploy Code
        run: |
          echo "Deploying code."

      - name: Mark deployment as succeeded
        if: always()
        uses: Shipbotio/shipbot-deployment-action@v2.0.1
        with:
          apiKey: ${{ secrets.SHIPBOT_API_KEY }}
          artifactConfig: shipbot.json
          deploymentId: ${{ steps.log_deployment.outputs.deploymentId }}
          status: ${{ job.status == 'success' && 'SUCCEEDED' || 'FAILED' }}
```

If you wish to just track successful deployments you can omit the `status` parameter.

```yaml
      - name: Log Deployment
        uses: Shipbotio/shipbot-deployment-action@v1
        with:
          apiKey: ${{ secrets.SHIPBOT_API_KEY }}
          artifactConfig: shipbot.json
          environment: "PRODUCTION"
          version: ${{ github.sha }}
          commitSha: ${{ github.sha }}
          branch: ${{ github.ref_name }}
          link: https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }}
          user: ${{ github.actor }}
```

## Versioning

This action follows semantic versioning. You can:
- Use a specific version: `uses: Shipbotio/shipbot-deployment-action@v1.0.1`
- Use the latest version of a major release: `uses: Shipbotio/shipbot-deployment-action@v1`
- Use the latest version (not recommended): `uses: Shipbotio/shipbot-deployment-action@master`

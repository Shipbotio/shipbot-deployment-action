# Shipbot.io Deployment Action

This Github action makes it easy to track deployments from your Github actions.


## Inputs

| Parameter              | Required | Description |
| ---------------- | -------- | ----------- |
| `apiKey`         | ✅  | Shipbot API key (found in Settings). |
| `artifactId`      | ✅       | Either artifact ID or name is required. If an artifact hasn't been created this can be ommited and the name will create a new artifact. Artifacts can be created and managed using the API or [Terraform module](https://docs.shipbot.io/docs/sdks/terraform) if desired. |
| `artifactName`      | ✅       | See above.     |
| `version`| ✅       | The version can be any string. |
| `environment`| ✅       | This should match the environment created in Current Version. By default `PRODUCTION` is created. |
| `status`| ❌       | One of `STARTED`, `SUCCEEDED`, `FAILED`. |
| `changelog`| ❌       | This can be a URL to a change log or the changelog notes itself. |
| `description`| ❌       | This can be further information on the deployment that wouldn't be considered part of the changelog. |
| `commitSha`| ❌       | Commit SHA reference. |
| `link`| ❌       | This should link to an external place where more action on the deployment can take place for example it could be the deployment job in your CI/CD pipeline. |
| `type`| ❌       | This is a enum describing the deployment strategy. The only option right now is SIMPLE. |
| `user`| ❌       | This can be any string, for example name or email but ideally it is `github.actor` which is the default when using the Github Action. We will link this to Slack users within Shipbot.io once said user has logged into Shipbot.io and connected with Github. |

## Example usage

### GitHub secrets

[Github secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets#about-encrypted-secrets) assumed to be set:
* `SHIPBOT_API_KEY` - Shipbot.io API key found in [Settings](https://app.shipbot.io/settings).

The examples below use a number of [default GitHub environment variables](https://docs.github.com/en/actions/learn-github-actions/variables#default-environment-variables) which greatly enhance the quality of notifications and experience within Shipbot.io

### Recommended Implementation

From the below add the two jobs to your relevant Github workflow file.

```yaml
TBD
```

## Versioning

This action follows semantic versioning. You can:
- Use a specific version: `uses: Shipbotio/shipbot-deployment-action@v1.0.1`
- Use the latest version of a major release: `uses: Shipbotio/shipbot-deployment-action@v1`
- Use the latest version (not recommended): `uses: Shipbotio/shipbot-deployment-action@master`
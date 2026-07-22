# Catalyst Deployment Stubs

Production deployment **must** use Zoho Catalyst services.
See [`catalyst.txt`](../catalyst.txt), [`docs/deployment/catalyst.md`](../docs/deployment/catalyst.md),
and the beginner console walkthrough:
[`docs/deployment/catalyst_console_setup.md`](../docs/deployment/catalyst_console_setup.md).

| Folder | Catalyst service |
|--------|------------------|
| `functions/` | Catalyst Serverless (Functions) |
| `appsail/` | Catalyst AppSail (OCI / managed runtime) |
| `client/` | Catalyst Slate / Web Client Hosting |
| `gateway/` | Catalyst API Gateway |
| `signals/` | Catalyst Signals + Event Functions |
| `circuits/` | Catalyst Circuits |

**TODO:** Add Catalyst project JSON / CLI configs when the Catalyst project is provisioned.
Do not substitute third-party services for capabilities Catalyst already provides.

# Azure Production Deployment Guide

## 1. Resources
- Azure Database for PostgreSQL Flexible Server
- Azure Container Apps (for the intake service)
- Azure Key Vault (for secrets)
- Azure Monitor (Log Analytics)

## 2. Authentication
- Enable System-Assigned Managed Identity on the Container App.
- Grant `Key Vault Secrets User` role to the identity.

## 3. Managed Mailbox
- Use an Application Access Policy in Exchange Online to restrict the app registration to the production pharmaceutical inbox.

## 4. CI/CD
- GitHub Actions workflow (in `.github/workflows/ci.yml`) handles testing.
- Add CD step to push to Azure Container Registry and update Container App.

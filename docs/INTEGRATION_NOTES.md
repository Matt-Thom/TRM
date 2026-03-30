# Integration Notes

## Microsoft Entra ID

- Single multi-purpose app registration (SSO + Graph API via incremental consent)
- Initial scopes: `openid`, `profile`, `email`, `User.Read`
- Future Graph scopes (Phase 4): `ChannelMessage.Send`, `Mail.Send`
- App registration is a manual Azure portal step — document redirect URIs here when completed

## ConnectWise Manage

- API target: `/company/configurations` endpoints
- Per-tenant credential storage (encrypted in `tenant_integrations` table)
- Rate limiting and exponential backoff on 429/5xx

## Microsoft Graph API

- Reuses Entra ID app registration
- Incremental consent for Teams/email scopes
- Adaptive cards for treatment approval notifications

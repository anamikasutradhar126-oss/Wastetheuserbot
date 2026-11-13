# Waste Userbot – requested update

Implemented the requested UI/feature updates while preserving existing command names and core handlers.

## Included
- Force-join channels: `@wasteBotz` and `@wasteuserbotUpdates`.
- Force-join UI uses quote-style HTML and red/blue button styling.
- Verified flow exposes a Help button and category menu.
- Help categories include Music, VcFight, Welcome, AI Chat, Tools, Fun, Promotion and Info.
- Existing userbot commands accept both `.` and `/` prefixes where supported.
- Connected user sessions use Telegram device model `Waste` and app version `1.0`.
- Connected session post-login setup attempts the three requested joins and starts `@EvaMusiicbot`.
- Automatic welcome module with `.welcome on/off` and `/welcome on/off`.
- Welcome mentions new members and uses quote-style messages.
- VcFight recording menu: `recordings`, `addrc`, `removerc`, `rcinfo`, `myrc`.
- Recordings can be saved from replied audio/voice or by using `addrc` and then sending the recording.
- Saved recordings can be deleted, inspected and played in the selected VC.
- Music `.play` and `/play` use the connected account's group VC and display quote-style now-playing messages.
- AutoTextPromo message pool expanded with more varied casual lines.
- Branding references updated: `@jp_network` → `@wasteBotz`; `@ii_jpexo_ii` → `@day1Nomore`.
- Owner set to `@day1Nomore` in the updated branding areas.

## Notes
- Existing commands and their names were not renamed.
- Telegram may cache an existing session's device display temporarily; the Pyrogram client is configured with `device_model="Waste"` for new connections/reconnections.
- Private invite links can only be joined when the connected account is allowed to join and the invite is valid.
